import hashlib
import hmac
import os
import secrets
import time
import uuid
from collections import defaultdict
from collections.abc import Generator
from typing import Annotated

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Article, Sentence, Word, Wordbook, WordbookEntry


APP_NAME = "CET-4 Study API"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "https://enplay.aoke.ltd,https://enplay.ningboaoke.com,https://cet4-words-study.pages.dev",
    ).split(",")
    if origin.strip()
]
AUDIO_ROOT = os.getenv("AUDIO_ROOT", "/app/audio")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "api-enplay.aoke.ltd,api-enplay.ningboaoke.com,localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", str(5 * 1024 * 1024)))
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
PRESENCE_CAPACITY = max(1, int(os.getenv("PRESENCE_CAPACITY", "200")))
PRESENCE_TTL_SECONDS = max(45, int(os.getenv("PRESENCE_TTL_SECONDS", "90")))
PRESENCE_SECRET = os.getenv("PRESENCE_SECRET", "") or ADMIN_TOKEN or "enplay-local-development"
PRESENCE_KEY = "enplay:presence:leases"

app = FastAPI(
    title=APP_NAME,
    version="0.2.0",
    docs_url="/docs" if ENABLE_DOCS else None,
    redoc_url="/redoc" if ENABLE_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_DOCS else None,
)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token", "X-Presence-Token"],
)

redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMITS = {
    "admin": (20, 60),
    "wordbooks": (120, 60),
    "audio": (600, 60),
    "presence": (12, 60),
}
rate_windows: dict[tuple[str, str], list[float | int]] = defaultdict(lambda: [0.0, 0])
wordbook_cache: dict[str, tuple[bytes, str]] = {}


def request_scope(path: str) -> str | None:
    if path.startswith("/v1/admin/"):
        return "admin"
    if path.startswith("/v1/wordbooks"):
        return "wordbooks"
    if path.startswith("/audio/"):
        return "audio"
    if path.startswith("/v1/presence"):
        return "presence"
    return None


def presence_protected(path: str) -> bool:
    # Recorded audio stays on one shared URL so Cloudflare can cache one copy for
    # every admitted visitor. The app gate controls normal access while API data
    # endpoints additionally require a live signed presence lease.
    return path.startswith(("/v1/words", "/v1/sentences", "/v1/articles", "/v1/wordbooks"))


def sign_device(device_id: str) -> str:
    signature = hmac.new(
        PRESENCE_SECRET.encode("utf-8"), device_id.encode("ascii"), hashlib.sha256
    ).hexdigest()
    return f"{device_id}.{signature}"


def verify_device_token(token: str | None) -> str | None:
    if not token or len(token) > 160 or "." not in token:
        return None
    device_id, supplied_signature = token.rsplit(".", 1)
    if len(device_id) != 32 or any(character not in "0123456789abcdef" for character in device_id):
        return None
    expected = sign_device(device_id).rsplit(".", 1)[1]
    if not secrets.compare_digest(supplied_signature, expected):
        return None
    return device_id


async def presence_count(now: float | None = None) -> int:
    current_time = now if now is not None else time.time()
    await redis_client.zremrangebyscore(PRESENCE_KEY, "-inf", current_time)
    return int(await redis_client.zcard(PRESENCE_KEY))


@app.middleware("http")
async def protect_api(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body is too large."},
                )
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid Content-Length header."},
            )

    # Let CORSMiddleware answer browser preflight requests before presence checks.
    if request.method == "OPTIONS":
        return await call_next(request)

    scope = request_scope(request.url.path)
    if scope:
        now = time.monotonic()
        ip_address = request.headers.get("cf-connecting-ip")
        if not ip_address:
            ip_address = request.client.host if request.client else "unknown"
        limit, window_seconds = RATE_LIMITS[scope]
        window = rate_windows[(scope, ip_address)]
        if now - float(window[0]) >= window_seconds:
            window[:] = [now, 0]
        window[1] = int(window[1]) + 1
        if int(window[1]) > limit:
            retry_after = max(1, int(window_seconds - (now - float(window[0]))))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": str(retry_after)},
            )
        if len(rate_windows) > 50_000:
            expired = [
                key
                for key, value in rate_windows.items()
                if now - float(value[0]) >= RATE_LIMITS[key[0]][1]
            ]
            for key in expired:
                rate_windows.pop(key, None)

    if presence_protected(request.url.path):
        presence_token = request.headers.get("x-presence-token") or request.query_params.get("presence")
        device_id = verify_device_token(presence_token)
        if device_id is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "An active visitor session is required."},
            )
        try:
            expires_at = await redis_client.zscore(PRESENCE_KEY, device_id)
        except RedisError:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "Visitor capacity service is temporarily unavailable."},
            )
        if expires_at is None or float(expires_at) <= time.time():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "The visitor session has expired."},
            )

    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if (
        request.method == "GET"
        and response.status_code == status.HTTP_200_OK
        and request.url.path.startswith("/v1/wordbooks")
    ):
        response.headers["Cache-Control"] = (
            "public, max-age=300, s-maxage=86400, stale-while-revalidate=604800"
        )
    return response

app.mount("/audio", StaticFiles(directory=AUDIO_ROOT, check_dir=False), name="audio")


class WordPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str = Field(min_length=1, max_length=120)
    phonetic: str | None = Field(default=None, max_length=255)
    definition: str = Field(min_length=1, max_length=5000)
    example: str | None = Field(default=None, max_length=5000)


class PresenceRequest(BaseModel):
    token: str | None = Field(default=None, max_length=160)


class PresenceStatus(BaseModel):
    admitted: bool
    online: int
    capacity: int
    lease_seconds: int
    token: str | None = None


class SentencePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scene: str | None = Field(default=None, max_length=120)
    text: str = Field(min_length=1, max_length=5000)
    translation: str | None = Field(default=None, max_length=10000)


class ArticlePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=200000)
    translation: str | None = Field(default=None, max_length=200000)
    level: str | None = Field(default=None, max_length=32)


class WordbookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    name: str
    description: str | None = None
    source_name: str
    source_url: str
    license_name: str
    license_url: str
    item_count: int


class WordbookEntryPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    word: str
    phonetic: str | None = None
    definition: str
    definition_en: str | None = None
    example: str | None = None


class WordbookPayload(WordbookSummary):
    items: list[WordbookEntryPayload]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not ADMIN_TOKEN or not x_admin_token or not secrets.compare_digest(
        x_admin_token, ADMIN_TOKEN
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrator authentication is required.",
        )


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def close_redis() -> None:
    await redis_client.aclose()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.get("/v1/presence/status", response_model=PresenceStatus)
async def get_presence_status() -> PresenceStatus:
    try:
        online = await presence_count()
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Visitor capacity service is temporarily unavailable.",
        ) from error
    return PresenceStatus(
        admitted=False,
        online=online,
        capacity=PRESENCE_CAPACITY,
        lease_seconds=PRESENCE_TTL_SECONDS,
    )


@app.post("/v1/presence/join", response_model=PresenceStatus)
async def join_presence(payload: PresenceRequest) -> PresenceStatus:
    device_id = verify_device_token(payload.token)
    if device_id is None:
        device_id = uuid.uuid4().hex
    token = sign_device(device_id)
    now = time.time()
    expires_at = now + PRESENCE_TTL_SECONDS
    admission_script = """
        redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
        local exists = redis.call('ZSCORE', KEYS[1], ARGV[3])
        local count = redis.call('ZCARD', KEYS[1])
        if not exists and count >= tonumber(ARGV[4]) then
            return {0, count}
        end
        redis.call('ZADD', KEYS[1], ARGV[2], ARGV[3])
        if not exists then count = count + 1 end
        return {1, count}
    """
    try:
        admitted, online = await redis_client.eval(
            admission_script,
            1,
            PRESENCE_KEY,
            now,
            expires_at,
            device_id,
            PRESENCE_CAPACITY,
        )
    except RedisError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Visitor capacity service is temporarily unavailable.",
        ) from error
    return PresenceStatus(
        admitted=bool(admitted),
        online=int(online),
        capacity=PRESENCE_CAPACITY,
        lease_seconds=PRESENCE_TTL_SECONDS,
        token=token if admitted else None,
    )


@app.get("/v1/words", response_model=list[WordPayload])
def list_words(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Word]:
    return list(db.scalars(select(Word).order_by(Word.id).offset(offset).limit(limit)))


@app.get("/v1/sentences", response_model=list[SentencePayload])
def list_sentences(
    scene: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[Sentence]:
    statement = select(Sentence).order_by(Sentence.id)
    if scene:
        statement = statement.where(Sentence.scene == scene)
    return list(db.scalars(statement.offset(offset).limit(limit)))


@app.get("/v1/articles", response_model=list[ArticlePayload])
def list_articles(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Article]:
    return list(db.scalars(select(Article).order_by(Article.id).offset(offset).limit(limit)))


@app.get("/v1/wordbooks", response_model=list[WordbookSummary])
def list_wordbooks(db: Session = Depends(get_db)) -> list[Wordbook]:
    statement = select(Wordbook).order_by(Wordbook.display_order, Wordbook.id)
    return list(db.scalars(statement))


@app.get("/v1/wordbooks/{slug}", response_model=WordbookPayload)
def get_wordbook(
    slug: str,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    cached = wordbook_cache.get(slug)
    if cached is not None:
        payload, etag = cached
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": etag})
        return Response(content=payload, media_type="application/json", headers={"ETag": etag})

    wordbook = db.scalar(select(Wordbook).where(Wordbook.slug == slug))
    if wordbook is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wordbook not found.")
    entries = list(
        db.scalars(
            select(WordbookEntry)
            .where(WordbookEntry.wordbook_id == wordbook.id)
            .order_by(WordbookEntry.rank, WordbookEntry.id)
        )
    )
    data = {
        "slug": wordbook.slug,
        "name": wordbook.name,
        "description": wordbook.description,
        "source_name": wordbook.source_name,
        "source_url": wordbook.source_url,
        "license_name": wordbook.license_name,
        "license_url": wordbook.license_url,
        "item_count": wordbook.item_count,
        "items": entries,
    }
    payload = WordbookPayload.model_validate(data).model_dump_json().encode("utf-8")
    etag = f'"{hashlib.sha256(payload).hexdigest()}"'
    wordbook_cache[slug] = (payload, etag)
    return Response(content=payload, media_type="application/json", headers={"ETag": etag})


@app.post("/v1/admin/words", dependencies=[Depends(require_admin)])
def import_words(
    items: Annotated[list[WordPayload], Body(min_length=1, max_length=1000)],
    db: Session = Depends(get_db),
) -> dict[str, int]:
    created = 0
    updated = 0
    for item in items:
        word = db.scalar(select(Word).where(Word.text == item.text.strip()))
        if word is None:
            db.add(Word(**item.model_dump()))
            created += 1
        else:
            word.phonetic = item.phonetic
            word.definition = item.definition
            word.example = item.example
            updated += 1
    db.commit()
    return {"created": created, "updated": updated}


@app.post("/v1/admin/sentences", dependencies=[Depends(require_admin)])
def import_sentences(
    items: Annotated[list[SentencePayload], Body(min_length=1, max_length=1000)],
    db: Session = Depends(get_db),
) -> dict[str, int]:
    db.add_all(Sentence(**item.model_dump()) for item in items)
    db.commit()
    return {"created": len(items)}


@app.post("/v1/admin/articles", dependencies=[Depends(require_admin)])
def import_articles(
    items: Annotated[list[ArticlePayload], Body(min_length=1, max_length=1000)],
    db: Session = Depends(get_db),
) -> dict[str, int]:
    db.add_all(Article(**item.model_dump()) for item in items)
    db.commit()
    return {"created": len(items)}

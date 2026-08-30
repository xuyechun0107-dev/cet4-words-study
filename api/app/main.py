import hashlib
import os
import secrets
import time
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
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Article, Sentence, Word, Wordbook, WordbookEntry


APP_NAME = "CET-4 Study API"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS", "https://enplay.ningboaoke.com"
    ).split(",")
    if origin.strip()
]
AUDIO_ROOT = os.getenv("AUDIO_ROOT", "/app/audio")
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS", "api-enplay.ningboaoke.com,localhost,127.0.0.1"
    ).split(",")
    if host.strip()
]
MAX_BODY_BYTES = int(os.getenv("MAX_BODY_BYTES", str(5 * 1024 * 1024)))
ENABLE_DOCS = os.getenv("ENABLE_DOCS", "false").lower() == "true"

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
    allow_headers=["Content-Type", "X-Admin-Token"],
)

RATE_LIMITS = {
    "admin": (20, 60),
    "wordbooks": (120, 60),
    "audio": (600, 60),
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
    return None


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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


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

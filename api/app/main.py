import hashlib
import hmac
import json
import os
import re
import secrets
import time
import unicodedata
import uuid
from collections import defaultdict
from collections.abc import Generator
from typing import Annotated, Literal

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import (
    Article,
    ContentLibrary,
    ContentLibraryItem,
    ContentSegment,
    ContentTranslation,
    Sentence,
    Word,
    Wordbook,
    WordbookEntry,
)


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
I18N_SCHEMA_VERSION = 1
I18N_LOCALES = frozenset({"zh-Hant", "ja", "ko", "fr", "es", "pt", "ru", "th", "ar"})
I18N_ARTICLE_DATASETS = frozenset(
    {
        "articles-graded",
        "articles-graded-junior-basic",
        "articles-graded-junior-advanced",
        "articles-graded-senior-basic",
        "articles-graded-senior-advanced",
    }
)
I18N_STATIC_DATASETS = frozenset(
    {
        "words-cet4",
        "sentences-daily",
        "sentences-common",
        "sentences-tatoeba-basic",
        "sentences-tatoeba-intermediate",
    }
) | I18N_ARTICLE_DATASETS
I18N_WORDBOOK_DATASET_PATTERN = re.compile(r"wordbook-[a-z0-9][a-z0-9-]{0,63}\Z")
I18N_ARTICLE_KEY_PATTERN = re.compile(r"[a-z0-9][a-z0-9_-]{0,191}\Z")
I18N_TATOEBA_KEY_PATTERN = re.compile(r"[1-9][0-9]*\Z")
I18N_ARTICLE_SENTENCE_FIELD_PATTERN = re.compile(r"sentences\.(0|[1-9][0-9]{0,4})\Z")
I18N_LIBRARY_ID_SUFFIX_PATTERN = re.compile(r"[a-z0-9][a-z0-9._-]{0,139}\Z")
I18N_SOURCE_LIBRARY_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}\Z")
I18N_CACHE_CONTROL = "private, no-store"
I18N_CATALOG_CACHE_CONTROL = "private, no-store"

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
    "i18n": (120, 60),
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
    if path.startswith("/v1/i18n/"):
        return "i18n"
    if path.startswith("/audio/"):
        return "audio"
    if path.startswith("/v1/presence"):
        return "presence"
    return None


def presence_protected(path: str) -> bool:
    # Recorded audio stays on one shared URL so Cloudflare can cache one copy for
    # every admitted visitor. The app gate controls normal access while API data
    # endpoints additionally require a live signed presence lease.
    return path.startswith(
        (
            "/v1/words",
            "/v1/sentences",
            "/v1/articles",
            "/v1/wordbooks",
            "/v1/i18n/",
        )
    )


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


def i18n_camel_alias(field_name: str) -> str:
    head, *tail = field_name.split("_")
    return head + "".join(part.capitalize() for part in tail)


class I18nTranslationUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    item_key: str = Field(min_length=1, max_length=512)
    field: str = Field(min_length=1, max_length=64)
    source_lang: str = Field(
        min_length=2,
        max_length=16,
        pattern=r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$",
    )
    source_field: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z][A-Za-z0-9_.-]*$",
    )
    source_text: str = Field(min_length=1, max_length=20_000)
    source_hash: str | None = Field(
        default=None,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    translated_text: str = Field(
        min_length=1,
        max_length=20_000,
    )
    provider: str | None = Field(default=None, max_length=64)
    model: str | None = Field(default=None, max_length=128)
    status: Literal["draft", "ready", "reviewed"] = "ready"


class I18nTranslationBatchUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    schema_version: Literal[1] = 1
    dataset: str = Field(min_length=1, max_length=96)
    locale: Literal["zh-Hant", "ja", "ko", "fr", "es", "pt", "ru", "th", "ar"]
    content_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$",
    )
    items: list[I18nTranslationUpsert] = Field(min_length=1, max_length=500)


class I18nCatalogAttribution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    url: str | None = Field(
        default=None,
        max_length=500,
        pattern=r"^(?:|https?://[^\s]+)$",
    )
    notice: str | None = Field(default=None, max_length=20_000)


class I18nCatalogLibraryUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    id: str = Field(min_length=4, max_length=160)
    type: Literal["words", "sentences", "articles"]
    dataset: str = Field(min_length=1, max_length=96)
    source_library_id: str = Field(
        min_length=1,
        max_length=160,
    )
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5_000)
    format: str | None = Field(default=None, max_length=160)
    item_count: int = Field(ge=0, le=1_000_000)
    source: I18nCatalogAttribution
    license: I18nCatalogAttribution
    status: Literal["draft", "ready", "reviewed"] = "draft"
    display_order: int = Field(default=0, ge=0, le=1_000_000)


class I18nCatalogBatchUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    schema_version: Literal[1] = 1
    locale: Literal["zh-Hant", "ja", "ko", "fr", "es", "pt", "ru", "th", "ar"]
    content_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$",
    )
    libraries: list[I18nCatalogLibraryUpsert] = Field(min_length=1, max_length=100)


class I18nLibraryItemUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    item_key: str = Field(min_length=1, max_length=512)
    position: int = Field(ge=0, le=1_000_000)
    payload: dict[str, object]
    source_hash: str = Field(
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    status: Literal["draft", "ready", "reviewed"] = "ready"


class I18nLibraryItemBatchUpsert(BaseModel):
    model_config = ConfigDict(
        alias_generator=i18n_camel_alias,
        extra="forbid",
        populate_by_name=True,
    )

    schema_version: Literal[1] = 1
    locale: Literal["zh-Hant", "ja", "ko", "fr", "es", "pt", "ru", "th", "ar"]
    library_id: str = Field(min_length=4, max_length=160)
    content_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$",
    )
    items: list[I18nLibraryItemUpsert] = Field(min_length=1, max_length=100)


def supported_i18n_dataset(dataset: str) -> bool:
    return dataset in I18N_STATIC_DATASETS or bool(
        I18N_WORDBOOK_DATASET_PATTERN.fullmatch(dataset)
    )


def normalize_i18n_item_key(dataset: str, item_key: str) -> str:
    normalized = " ".join(
        unicodedata.normalize("NFKC", item_key).strip().split()
    )
    if not normalized:
        raise ValueError("itemKey must contain visible text")
    if dataset == "words-cet4" or dataset.startswith("wordbook-"):
        return normalized.casefold()
    if dataset == "sentences-daily":
        return normalized.casefold()
    if dataset == "sentences-common" or dataset.startswith("sentences-tatoeba-"):
        if not I18N_TATOEBA_KEY_PATTERN.fullmatch(normalized):
            raise ValueError("Tatoeba itemKey must be a positive numeric source id")
        return normalized
    if dataset in I18N_ARTICLE_DATASETS:
        if not I18N_ARTICLE_KEY_PATTERN.fullmatch(normalized):
            raise ValueError("Article itemKey must be a lowercase article id")
        return normalized
    raise ValueError("Unsupported i18n dataset")


def valid_i18n_field(dataset: str, field: str) -> bool:
    if dataset == "words-cet4" or dataset.startswith("wordbook-"):
        return field == "definition"
    if dataset.startswith("sentences-"):
        return field == "translation"
    if dataset in I18N_ARTICLE_DATASETS:
        return field in {"title", "summary", "level", "genre", "topic"} or bool(
            I18N_ARTICLE_SENTENCE_FIELD_PATTERN.fullmatch(field)
        )
    return False


def valid_i18n_library_id(locale: str, library_id: str) -> bool:
    prefix = f"{locale}:"
    return library_id.startswith(prefix) and bool(
        I18N_LIBRARY_ID_SUFFIX_PATTERN.fullmatch(library_id[len(prefix) :])
    )


def i18n_dataset_matches_type(dataset: str, library_type: str) -> bool:
    if library_type == "words":
        return dataset == "words-cet4" or dataset.startswith("wordbook-")
    if library_type == "sentences":
        return dataset.startswith("sentences-")
    if library_type == "articles":
        return dataset in I18N_ARTICLE_DATASETS
    return False


def require_i18n_payload_text(
    payload: dict[str, object],
    key: str,
    *,
    max_length: int,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ValueError(f"payload.{key} must be non-empty text up to {max_length} characters")
    if "\x00" in value:
        raise ValueError(f"payload.{key} must not contain NUL bytes")
    return value


def normalize_i18n_library_payload(
    library: ContentLibrary,
    item_key: str,
    payload: dict[str, object],
) -> dict[str, object]:
    normalized = dict(payload)
    content_key = require_i18n_payload_text(normalized, "contentKey", max_length=512)
    if normalize_i18n_item_key(library.dataset, content_key) != item_key:
        raise ValueError("payload.contentKey must match itemKey")
    source_library_id = require_i18n_payload_text(
        normalized,
        "sourceLibraryId",
        max_length=160,
    )
    if source_library_id != library.source_library_id:
        raise ValueError("payload.sourceLibraryId must match the catalog library")

    if library.type == "words":
        localized = normalized.get("definitionLocalized")
        legacy_localized = normalized.get("definition")
        if localized is None and legacy_localized is not None:
            normalized["definitionLocalized"] = legacy_localized
        elif legacy_localized is not None and legacy_localized != localized:
            raise ValueError("payload.definition conflicts with definitionLocalized")
        normalized.pop("definition", None)

        word = require_i18n_payload_text(normalized, "word", max_length=120)
        if normalize_i18n_item_key(library.dataset, word) != item_key:
            raise ValueError("payload.word must match itemKey")
        require_i18n_payload_text(normalized, "definitionLocalized", max_length=10_000)
        require_i18n_payload_text(normalized, "definitionEn", max_length=10_000)
        phonetic = normalized.get("phonetic")
        if phonetic is not None and (not isinstance(phonetic, str) or len(phonetic) > 255):
            raise ValueError("payload.phonetic must be null or text up to 255 characters")
        example = normalized.get("example")
        if example is not None and (not isinstance(example, str) or len(example) > 10_000):
            raise ValueError("payload.example must be null or text up to 10000 characters")
        return normalized

    if library.type == "sentences":
        localized = normalized.get("translationLocalized")
        legacy_localized = normalized.get("translation")
        if localized is None and legacy_localized is not None:
            normalized["translationLocalized"] = legacy_localized
        elif legacy_localized is not None and legacy_localized != localized:
            raise ValueError("payload.translation conflicts with translationLocalized")
        normalized.pop("translation", None)

        require_i18n_payload_text(normalized, "text", max_length=20_000)
        require_i18n_payload_text(normalized, "translationLocalized", max_length=20_000)
        scene = normalized.get("scene")
        if scene is not None and (not isinstance(scene, str) or len(scene) > 120):
            raise ValueError("payload.scene must be null or text up to 120 characters")
        source_ids = normalized.get("sourceIds")
        if not isinstance(source_ids, list) or len(source_ids) > 16:
            raise ValueError("payload.sourceIds must be an array with at most 16 values")
        if any(not isinstance(source_id, (int, str)) for source_id in source_ids):
            raise ValueError("payload.sourceIds values must be strings or integers")
        return normalized

    if library.type == "articles":
        for canonical, legacy in (
            ("titleLocalized", "titleTranslation"),
            ("summaryLocalized", "summaryTranslation"),
        ):
            localized = normalized.get(canonical)
            legacy_localized = normalized.get(legacy)
            if localized is None and legacy_localized is not None:
                normalized[canonical] = legacy_localized
            elif legacy_localized is not None and legacy_localized != localized:
                raise ValueError(f"payload.{legacy} conflicts with {canonical}")
            normalized.pop(legacy, None)

        article_id = require_i18n_payload_text(normalized, "id", max_length=192)
        if article_id != item_key:
            raise ValueError("payload.id must match itemKey")
        for field, limit in (
            ("title", 500),
            ("titleLocalized", 500),
            ("summaryLocalized", 10_000),
            ("level", 160),
            ("levelLocalized", 160),
            ("cefr", 32),
            ("genre", 160),
            ("genreLocalized", 160),
            ("topic", 160),
            ("topicLocalized", 160),
        ):
            require_i18n_payload_text(normalized, field, max_length=limit)
        estimated_words = normalized.get("estimatedWords")
        if (
            not isinstance(estimated_words, int)
            or isinstance(estimated_words, bool)
            or estimated_words < 0
            or estimated_words > 1_000_000
        ):
            raise ValueError("payload.estimatedWords must be a non-negative integer")
        sentences = normalized.get("sentences")
        if not isinstance(sentences, list) or not sentences or len(sentences) > 500:
            raise ValueError("payload.sentences must contain between 1 and 500 entries")
        normalized_sentences: list[dict[str, object]] = []
        for sentence_index, sentence in enumerate(sentences):
            if not isinstance(sentence, dict):
                raise ValueError(f"payload.sentences[{sentence_index}] must be an object")
            normalized_sentence = dict(sentence)
            localized = normalized_sentence.get("translationLocalized")
            legacy_localized = normalized_sentence.get("translation")
            if localized is None and legacy_localized is not None:
                normalized_sentence["translationLocalized"] = legacy_localized
            elif legacy_localized is not None and legacy_localized != localized:
                raise ValueError(
                    f"payload.sentences[{sentence_index}].translation conflicts "
                    "with translationLocalized"
                )
            normalized_sentence.pop("translation", None)
            try:
                require_i18n_payload_text(normalized_sentence, "en", max_length=20_000)
                require_i18n_payload_text(
                    normalized_sentence,
                    "translationLocalized",
                    max_length=20_000,
                )
            except ValueError as error:
                raise ValueError(f"payload.sentences[{sentence_index}]: {error}") from error
            normalized_sentences.append(normalized_sentence)
        normalized["sentences"] = normalized_sentences
        return normalized

    raise ValueError("Unsupported catalog library type")


def i18n_json_response(
    payload_data: dict[str, object],
    request: Request,
    locale: str,
    cache_control: str = I18N_CACHE_CONTROL,
) -> Response:
    payload = json.dumps(
        payload_data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    etag = f'"{hashlib.sha256(payload).hexdigest()}"'
    headers = {
        "Cache-Control": cache_control,
        "Content-Language": locale,
        "ETag": etag,
        "Vary": "Accept-Encoding",
    }
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers=headers)
    return Response(
        content=payload,
        media_type="application/json",
        headers=headers,
    )


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


@app.get("/v1/i18n/catalog/{locale}")
def get_i18n_catalog(
    locale: str,
    request: Request,
    db: Session = Depends(get_db),
) -> Response:
    if locale not in I18N_LOCALES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation catalog not found.",
        )

    libraries = list(
        db.scalars(
            select(ContentLibrary)
            .where(
                ContentLibrary.locale == locale,
                ContentLibrary.status.in_(("ready", "reviewed")),
            )
            .order_by(ContentLibrary.display_order, ContentLibrary.library_id)
        )
    )
    item_stats: dict[int, tuple[int, int | None, int | None]] = {}
    if libraries:
        library_ids = [library.id for library in libraries]
        item_stats = {
            library_id: (
                int(item_count),
                int(min_position) if min_position is not None else None,
                int(max_position) if max_position is not None else None,
            )
            for library_id, item_count, min_position, max_position in db.execute(
                select(
                    ContentLibraryItem.library_id,
                    func.count(ContentLibraryItem.id),
                    func.min(ContentLibraryItem.position),
                    func.max(ContentLibraryItem.position),
                )
                .join(ContentLibrary, ContentLibrary.id == ContentLibraryItem.library_id)
                .where(
                    ContentLibraryItem.library_id.in_(library_ids),
                    ContentLibraryItem.content_version == ContentLibrary.content_version,
                    ContentLibraryItem.status.in_(("ready", "reviewed")),
                )
                .group_by(ContentLibraryItem.library_id)
            ).all()
        }

    complete_libraries = [
        library
        for library in libraries
        if library.item_count > 0
        and item_stats.get(library.id)
        == (library.item_count, 0, library.item_count - 1)
    ]
    catalog_libraries = [
        {
            "id": library.library_id,
            "type": library.type,
            "dataset": library.dataset,
            "sourceLibraryId": library.source_library_id,
            "name": library.name,
            "description": library.description,
            "format": library.format,
            "itemCount": item_stats.get(library.id, (0, None, None))[0],
            "source": {
                "name": library.source_name,
                "url": library.source_url,
                "notice": library.source_notice,
            },
            "license": {
                "name": library.license_name,
                "url": library.license_url,
                "notice": library.license_notice,
            },
            "contentVersion": library.content_version,
        }
        for library in complete_libraries
    ]
    return i18n_json_response(
        {
            "schemaVersion": I18N_SCHEMA_VERSION,
            "locale": locale,
            "libraries": catalog_libraries,
        },
        request,
        locale,
        I18N_CATALOG_CACHE_CONTROL,
    )


@app.get("/v1/i18n/bundles/{dataset}/{locale}")
def get_i18n_bundle(
    dataset: str,
    locale: str,
    request: Request,
    v: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=64,
            pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$",
        ),
    ] = None,
    db: Session = Depends(get_db),
) -> Response:
    if not supported_i18n_dataset(dataset) or locale not in I18N_LOCALES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation bundle not found.",
        )

    libraries = list(
        db.scalars(
            select(ContentLibrary).where(
                ContentLibrary.locale == locale,
                ContentLibrary.dataset == dataset,
                ContentLibrary.status.in_(("ready", "reviewed")),
            )
        )
    )
    if len(libraries) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="More than one active library resolves this locale and dataset.",
        )

    localized_rows: list[ContentLibraryItem] = []
    active_library = libraries[0] if libraries else None
    if active_library is not None and v is not None and v != active_library.content_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested translation bundle version is not active.",
        )
    if active_library is not None:
        localized_rows = list(
            db.scalars(
                select(ContentLibraryItem)
                .where(
                    ContentLibraryItem.library_id == active_library.id,
                    ContentLibraryItem.content_version == active_library.content_version,
                    ContentLibraryItem.status.in_(("ready", "reviewed")),
                )
                .order_by(ContentLibraryItem.position, ContentLibraryItem.item_key)
            )
        )
        if (
            active_library.item_count <= 0
            or len(localized_rows) != active_library.item_count
            or [row.position for row in localized_rows]
            != list(range(active_library.item_count))
        ):
            localized_rows = []

    rows: list[tuple[ContentSegment, ContentTranslation]] = []
    if locale == "zh-Hant":
        rows = db.execute(
            select(ContentSegment, ContentTranslation)
            .join(ContentTranslation, ContentTranslation.segment_id == ContentSegment.id)
            .where(
                ContentSegment.dataset == dataset,
                ContentTranslation.target_lang == locale,
                ContentTranslation.status.in_(("ready", "reviewed")),
            )
            .order_by(ContentSegment.item_key, ContentSegment.field)
        ).all()

    if not localized_rows and not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation bundle not found.",
        )

    items: dict[str, dict[str, object]] = {}
    for segment, translation in rows:
        item = items.setdefault(segment.item_key, {})
        if segment.field.startswith("sentences."):
            sentence_index = segment.field.split(".", 1)[1]
            sentences = item.get("sentences")
            if not isinstance(sentences, dict):
                sentences = {}
                item["sentences"] = sentences
            sentences[sentence_index] = translation.translated_text
        else:
            item[segment.field] = translation.translated_text

    content = [
        {
            "libraryId": active_library.library_id,
            "itemKey": library_item.item_key,
            "position": library_item.position,
            "payload": library_item.payload,
        }
        for library_item in localized_rows
    ]
    legacy_versions = {translation.content_version for _, translation in rows}
    bundle_content_version: str | None = None
    if localized_rows and active_library is not None:
        bundle_content_version = active_library.content_version
    elif len(legacy_versions) == 1:
        bundle_content_version = next(iter(legacy_versions))
    if v is not None and v != bundle_content_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested translation bundle version is not active.",
        )
    bundle: dict[str, object] = {
        "schemaVersion": I18N_SCHEMA_VERSION,
        "dataset": dataset,
        "locale": locale,
        "contentVersion": bundle_content_version,
        "items": items,
        "content": content,
    }
    return i18n_json_response(bundle, request, locale)


@app.post(
    "/v1/admin/i18n/catalog",
    dependencies=[Depends(require_admin)],
)
def upsert_i18n_catalog(
    batch: I18nCatalogBatchUpsert,
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    library_ids: set[str] = set()
    datasets: set[str] = set()
    for index, library_input in enumerate(batch.libraries):
        if not valid_i18n_library_id(batch.locale, library_input.id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].id must be scoped to locale {batch.locale}.",
            )
        if not supported_i18n_dataset(library_input.dataset):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].dataset is unsupported.",
            )
        if not i18n_dataset_matches_type(
            library_input.dataset,
            library_input.type,
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].type does not match its dataset.",
            )
        if not I18N_SOURCE_LIBRARY_ID_PATTERN.fullmatch(library_input.source_library_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].sourceLibraryId is invalid.",
            )
        if library_input.id in library_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].id is duplicated in this batch.",
            )
        if library_input.dataset in datasets:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}].dataset is duplicated for this locale.",
            )
        library_ids.add(library_input.id)
        datasets.add(library_input.dataset)
        text_values = (
            library_input.name,
            library_input.description,
            library_input.format,
            library_input.source.name,
            library_input.source.url,
            library_input.source.notice,
            library_input.license.name,
            library_input.license.url,
            library_input.license.notice,
        )
        if any(value is not None and "\x00" in value for value in text_values):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"libraries[{index}] contains a NUL byte.",
            )
        required_names = (
            ("name", library_input.name),
            ("source.name", library_input.source.name),
            ("license.name", library_input.license.name),
        )
        for field_name, value in required_names:
            if not value.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"libraries[{index}].{field_name} must contain visible text.",
                )

    # Catalog promotion and item imports lock the same parent row first.  This
    # prevents a late item transaction from mutating a version just after it
    # became active on MySQL.
    locale_libraries = list(
        db.scalars(
            select(ContentLibrary)
            .where(ContentLibrary.locale == batch.locale)
            .with_for_update()
        )
    )
    libraries_by_id = {library.library_id: library for library in locale_libraries}
    libraries_by_dataset = {library.dataset: library for library in locale_libraries}

    for index, library_input in enumerate(batch.libraries):
        existing = libraries_by_id.get(library_input.id)
        dataset_owner = libraries_by_dataset.get(library_input.dataset)
        if dataset_owner is not None and dataset_owner.library_id != library_input.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"libraries[{index}].dataset already belongs to another "
                    "library in this locale."
                ),
            )
        if existing is not None and (
            existing.dataset != library_input.dataset
            or existing.type != library_input.type
            or existing.source_library_id != library_input.source_library_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"libraries[{index}] cannot change dataset, type, or "
                    "sourceLibraryId for an existing library id."
                ),
            )
        if library_input.status in {"ready", "reviewed"}:
            if library_input.item_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"libraries[{index}] cannot publish an empty content version.",
                )
            ready_item_count = 0
            min_position: int | None = None
            max_position: int | None = None
            if existing is not None:
                count_value, min_value, max_value = db.execute(
                    select(
                        func.count(ContentLibraryItem.id),
                        func.min(ContentLibraryItem.position),
                        func.max(ContentLibraryItem.position),
                    ).where(
                        ContentLibraryItem.library_id == existing.id,
                        ContentLibraryItem.content_version == batch.content_version,
                        ContentLibraryItem.status.in_(("ready", "reviewed")),
                    )
                ).one()
                ready_item_count = int(count_value or 0)
                min_position = int(min_value) if min_value is not None else None
                max_position = int(max_value) if max_value is not None else None
            if (
                ready_item_count != library_input.item_count
                or min_position != 0
                or max_position != library_input.item_count - 1
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"libraries[{index}] declares {library_input.item_count} items "
                        f"but version {batch.content_version} does not have exactly "
                        f"{ready_item_count} ready items in contiguous positions from zero."
                    ),
                )

    libraries_created = 0
    libraries_updated = 0
    libraries_unchanged = 0
    libraries_staged = 0
    for library_input in batch.libraries:
        values = {
            "type": library_input.type,
            "dataset": library_input.dataset,
            "source_library_id": library_input.source_library_id,
            "name": library_input.name.strip(),
            "description": (
                library_input.description.strip()
                if library_input.description and library_input.description.strip()
                else None
            ),
            "format": (
                library_input.format.strip()
                if library_input.format and library_input.format.strip()
                else None
            ),
            "item_count": library_input.item_count,
            "source_name": library_input.source.name.strip(),
            "source_url": (
                library_input.source.url.strip()
                if library_input.source.url and library_input.source.url.strip()
                else None
            ),
            "source_notice": (
                library_input.source.notice.strip()
                if library_input.source.notice and library_input.source.notice.strip()
                else None
            ),
            "license_name": library_input.license.name.strip(),
            "license_url": (
                library_input.license.url.strip()
                if library_input.license.url and library_input.license.url.strip()
                else None
            ),
            "license_notice": (
                library_input.license.notice.strip()
                if library_input.license.notice and library_input.license.notice.strip()
                else None
            ),
            "content_version": batch.content_version,
            "status": library_input.status,
            "display_order": library_input.display_order,
        }
        library = libraries_by_id.get(library_input.id)
        if library is None:
            db.add(
                ContentLibrary(
                    locale=batch.locale,
                    library_id=library_input.id,
                    **values,
                )
            )
            libraries_created += 1
            continue
        if (
            library.status in {"ready", "reviewed"}
            and library_input.status == "draft"
        ):
            # Generated publishers use draft/items/ready for both first deploys
            # and updates.  A draft request for an already-published identity is
            # therefore a staging declaration, not permission to withdraw the
            # active version.  Versioned items can be loaded while this row keeps
            # pointing at the old complete version; the final ready request is
            # the atomic switch.
            libraries_staged += 1
            continue
        if all(getattr(library, name) == value for name, value in values.items()):
            libraries_unchanged += 1
            continue
        for name, value in values.items():
            setattr(library, name, value)
        libraries_updated += 1

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A concurrent catalog import conflicted with this batch.",
        ) from error

    return {
        "schemaVersion": I18N_SCHEMA_VERSION,
        "locale": batch.locale,
        "librariesCreated": libraries_created,
        "librariesUpdated": libraries_updated,
        "librariesUnchanged": libraries_unchanged,
        "librariesStaged": libraries_staged,
    }


@app.post(
    "/v1/admin/i18n/library-items",
    dependencies=[Depends(require_admin)],
)
def upsert_i18n_library_items(
    batch: I18nLibraryItemBatchUpsert,
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    if not valid_i18n_library_id(batch.locale, batch.library_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"libraryId must be scoped to locale {batch.locale}.",
        )
    library = db.scalar(
        select(ContentLibrary)
        .where(
            ContentLibrary.locale == batch.locale,
            ContentLibrary.library_id == batch.library_id,
        )
        .with_for_update()
    )
    if library is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create the draft catalog library before importing its items.",
        )

    prepared: list[tuple[I18nLibraryItemUpsert, str, dict[str, object], str]] = []
    item_keys: set[str] = set()
    for index, item in enumerate(batch.items):
        try:
            item_key = normalize_i18n_item_key(library.dataset, item.item_key)
            normalized_payload = normalize_i18n_library_payload(
                library,
                item_key,
                item.payload,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}]: {error}",
            ) from error
        if item_key in item_keys:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].itemKey is duplicated in this batch.",
            )
        item_keys.add(item_key)
        payload_json = json.dumps(
            normalized_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(payload_json) > 250_000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].payload exceeds 250000 UTF-8 bytes.",
            )
        payload_hash = hashlib.sha256(payload_json).hexdigest()
        prepared.append((item, item_key, normalized_payload, payload_hash))

    existing_items = list(
        db.scalars(
            select(ContentLibraryItem).where(
                ContentLibraryItem.library_id == library.id,
                ContentLibraryItem.content_version == batch.content_version,
                ContentLibraryItem.item_key.in_(item_keys),
            )
        )
    )
    items_by_key = {item.item_key: item for item in existing_items}

    if (
        library.status in {"ready", "reviewed"}
        and batch.content_version == library.content_version
    ):
        missing_item_keys = [
            item_key
            for _, item_key, _, _ in prepared
            if item_key not in items_by_key
        ]
        if missing_item_keys:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "The active published content version is sealed; only an "
                    "exact replay of existing items is allowed."
                ),
            )

    for item_input, item_key, normalized_payload, payload_hash in prepared:
        library_item = items_by_key.get(item_key)
        values = {
            "position": item_input.position,
            "payload": normalized_payload,
            "source_hash": item_input.source_hash,
            "payload_hash": payload_hash,
            "status": item_input.status,
        }
        if library_item is not None and any(
            getattr(library_item, name) != value for name, value in values.items()
        ):
            # A version may later become the rollback target and its URL/ETag may
            # already exist in downstream caches.  Immutability therefore
            # applies to every inserted version, not merely today's active row.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Library content versions are immutable; stage changes "
                    "under a new contentVersion."
                ),
            )

    items_created = 0
    items_updated = 0
    items_unchanged = 0
    for item_input, item_key, normalized_payload, payload_hash in prepared:
        values = {
            "position": item_input.position,
            "payload": normalized_payload,
            "source_hash": item_input.source_hash,
            "payload_hash": payload_hash,
            "status": item_input.status,
        }
        library_item = items_by_key.get(item_key)
        if library_item is None:
            db.add(
                ContentLibraryItem(
                    library_id=library.id,
                    item_key=item_key,
                    content_version=batch.content_version,
                    **values,
                )
            )
            items_created += 1
            continue
        if all(getattr(library_item, name) == value for name, value in values.items()):
            items_unchanged += 1
            continue
        for name, value in values.items():
            setattr(library_item, name, value)
        items_updated += 1

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A concurrent library item import conflicted with this batch.",
        ) from error

    return {
        "schemaVersion": I18N_SCHEMA_VERSION,
        "locale": batch.locale,
        "libraryId": library.library_id,
        "contentVersion": batch.content_version,
        "itemsCreated": items_created,
        "itemsUpdated": items_updated,
        "itemsUnchanged": items_unchanged,
    }


@app.post(
    "/v1/admin/i18n/translations",
    dependencies=[Depends(require_admin)],
)
def upsert_i18n_translations(
    batch: I18nTranslationBatchUpsert,
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    if not supported_i18n_dataset(batch.dataset):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported i18n dataset.",
        )

    prepared: list[tuple[I18nTranslationUpsert, str, str, str]] = []
    identities: set[tuple[str, str]] = set()
    for index, item in enumerate(batch.items):
        try:
            item_key = normalize_i18n_item_key(batch.dataset, item.item_key)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].itemKey: {error}",
            ) from error
        if not valid_i18n_field(batch.dataset, item.field):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].field is not valid for {batch.dataset}.",
            )
        identity = (item_key, item.field)
        if identity in identities:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}] duplicates itemKey and field in this batch.",
            )
        identities.add(identity)

        if not item.source_text.strip() or "\x00" in item.source_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].sourceText must contain visible text without NUL bytes.",
            )
        translated_text = item.translated_text.strip()
        if not translated_text or "\x00" in translated_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].translatedText must contain visible text without NUL bytes.",
            )
        source_hash = hashlib.sha256(item.source_text.encode("utf-8")).hexdigest()
        if item.source_hash and not hmac.compare_digest(item.source_hash, source_hash):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"items[{index}].sourceHash does not match sourceText.",
            )
        prepared.append((item, item_key, source_hash, translated_text))

    item_keys = {item_key for _, item_key, _, _ in prepared}
    existing_segments = db.scalars(
        select(ContentSegment).where(
            ContentSegment.dataset == batch.dataset,
            ContentSegment.item_key.in_(item_keys),
        )
    ).all()
    segments_by_identity = {
        (segment.item_key, segment.field): segment for segment in existing_segments
    }

    segments_created = 0
    for item, item_key, _, _ in prepared:
        identity = (item_key, item.field)
        if identity not in segments_by_identity:
            segment = ContentSegment(
                dataset=batch.dataset,
                item_key=item_key,
                field=item.field,
            )
            db.add(segment)
            segments_by_identity[identity] = segment
            segments_created += 1
    db.flush()

    segment_ids = [
        segments_by_identity[(item_key, item.field)].id
        for item, item_key, _, _ in prepared
    ]
    existing_translations = db.scalars(
        select(ContentTranslation).where(
            ContentTranslation.segment_id.in_(segment_ids),
            ContentTranslation.target_lang == batch.locale,
        )
    ).all()
    translations_by_segment = {
        translation.segment_id: translation for translation in existing_translations
    }

    translations_created = 0
    translations_updated = 0
    translations_unchanged = 0
    for item, item_key, source_hash, translated_text in prepared:
        segment = segments_by_identity[(item_key, item.field)]
        values = {
            "source_lang": item.source_lang,
            "source_field": item.source_field,
            "source_text": item.source_text,
            "source_hash": source_hash,
            "content_version": batch.content_version,
            "translated_text": translated_text,
            "provider": item.provider.strip() if item.provider and item.provider.strip() else None,
            "model": item.model.strip() if item.model and item.model.strip() else None,
            "status": item.status,
        }
        translation = translations_by_segment.get(segment.id)
        if translation is None:
            db.add(
                ContentTranslation(
                    segment_id=segment.id,
                    target_lang=batch.locale,
                    **values,
                )
            )
            translations_created += 1
            continue
        if all(getattr(translation, name) == value for name, value in values.items()):
            translations_unchanged += 1
            continue
        for name, value in values.items():
            setattr(translation, name, value)
        translations_updated += 1

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A concurrent translation import conflicted with this batch.",
        ) from error

    return {
        "schemaVersion": I18N_SCHEMA_VERSION,
        "dataset": batch.dataset,
        "locale": batch.locale,
        "segmentsCreated": segments_created,
        "translationsCreated": translations_created,
        "translationsUpdated": translations_updated,
        "translationsUnchanged": translations_unchanged,
    }


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

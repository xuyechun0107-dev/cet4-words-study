import os
import secrets
from collections.abc import Generator

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Token"],
)
app.mount("/audio", StaticFiles(directory=AUDIO_ROOT, check_dir=False), name="audio")


class WordPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    text: str = Field(min_length=1, max_length=120)
    phonetic: str | None = Field(default=None, max_length=255)
    definition: str = Field(min_length=1)
    example: str | None = None


class SentencePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scene: str | None = Field(default=None, max_length=120)
    text: str = Field(min_length=1)
    translation: str | None = None


class ArticlePayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    translation: str | None = None
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
def get_wordbook(slug: str, db: Session = Depends(get_db)) -> dict[str, object]:
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
    return {
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


@app.post("/v1/admin/words", dependencies=[Depends(require_admin)])
def import_words(items: list[WordPayload], db: Session = Depends(get_db)) -> dict[str, int]:
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
    items: list[SentencePayload], db: Session = Depends(get_db)
) -> dict[str, int]:
    db.add_all(Sentence(**item.model_dump()) for item in items)
    db.commit()
    return {"created": len(items)}


@app.post("/v1/admin/articles", dependencies=[Depends(require_admin)])
def import_articles(items: list[ArticlePayload], db: Session = Depends(get_db)) -> dict[str, int]:
    db.add_all(Article(**item.model_dump()) for item in items)
    db.commit()
    return {"created": len(items)}

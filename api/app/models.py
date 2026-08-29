from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    phonetic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    definition: Mapped[str] = mapped_column(Text)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Sentence(Base):
    __tablename__ = "sentences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scene: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    text: Mapped[str] = mapped_column(Text)
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    content: Mapped[str] = mapped_column(Text)
    translation: Mapped[str | None] = mapped_column(Text, nullable=True)
    level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Wordbook(Base):
    __tablename__ = "wordbooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[str] = mapped_column(String(500))
    license_name: Mapped[str] = mapped_column(String(80))
    license_url: Mapped[str] = mapped_column(String(500))
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class WordbookEntry(Base):
    __tablename__ = "wordbook_entries"
    __table_args__ = (
        UniqueConstraint("wordbook_id", "word", name="uq_wordbook_entry_word"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    wordbook_id: Mapped[int] = mapped_column(
        ForeignKey("wordbooks.id", ondelete="CASCADE"), index=True
    )
    word: Mapped[str] = mapped_column(String(120), index=True)
    phonetic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    definition: Mapped[str] = mapped_column(Text)
    definition_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank: Mapped[int] = mapped_column(Integer, default=0)

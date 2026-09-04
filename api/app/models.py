from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
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


class ContentLibrary(Base):
    """Locale-scoped bookshelf metadata for an independently translated library."""

    __tablename__ = "content_libraries"
    __table_args__ = (
        UniqueConstraint(
            "locale",
            "library_id",
            name="uq_content_library_locale_id",
        ),
        UniqueConstraint(
            "locale",
            "dataset",
            name="uq_content_library_locale_dataset",
        ),
        Index(
            "ix_content_libraries_locale_status_order",
            "locale",
            "status",
            "display_order",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    locale: Mapped[str] = mapped_column(String(16))
    library_id: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(16))
    dataset: Mapped[str] = mapped_column(String(96))
    source_library_id: Mapped[str] = mapped_column(String(160))
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    format: Mapped[str | None] = mapped_column(String(160), nullable=True)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    source_name: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_name: Mapped[str] = mapped_column(String(160))
    license_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license_notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="ready")
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class ContentLibraryItem(Base):
    """A complete localized record in one immutable library content version."""

    __tablename__ = "content_library_items"
    __table_args__ = (
        UniqueConstraint(
            "library_id",
            "item_key",
            "content_version",
            name="uq_content_library_item_version",
        ),
        UniqueConstraint(
            "library_id",
            "position",
            "content_version",
            name="uq_content_library_item_position_version",
        ),
        Index(
            "ix_content_library_items_order",
            "library_id",
            "content_version",
            "position",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    library_id: Mapped[int] = mapped_column(
        ForeignKey("content_libraries.id", ondelete="CASCADE"),
        index=True,
    )
    item_key: Mapped[str] = mapped_column(String(512))
    position: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict[str, object]] = mapped_column(JSON)
    source_hash: Mapped[str] = mapped_column(String(64))
    payload_hash: Mapped[str] = mapped_column(String(64))
    content_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="ready")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class ContentSegment(Base):
    """A stable, language-neutral output slot in an i18n content bundle."""

    __tablename__ = "content_segments"
    __table_args__ = (
        UniqueConstraint(
            "dataset",
            "item_key",
            "field",
            name="uq_content_segment_identity",
        ),
        Index("ix_content_segments_dataset_item", "dataset", "item_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset: Mapped[str] = mapped_column(String(96))
    item_key: Mapped[str] = mapped_column(String(512))
    field: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class ContentTranslation(Base):
    """One locale's cached translation plus its exact source provenance."""

    __tablename__ = "content_translations"
    __table_args__ = (
        UniqueConstraint(
            "segment_id",
            "target_lang",
            name="uq_content_translation_locale",
        ),
        Index(
            "ix_content_translations_locale_status",
            "target_lang",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(
        ForeignKey("content_segments.id", ondelete="CASCADE"),
        index=True,
    )
    target_lang: Mapped[str] = mapped_column(String(16))
    source_lang: Mapped[str] = mapped_column(String(16))
    source_field: Mapped[str] = mapped_column(String(64))
    source_text: Mapped[str] = mapped_column(Text)
    source_hash: Mapped[str] = mapped_column(String(64))
    content_version: Mapped[str] = mapped_column(String(64))
    translated_text: Mapped[str] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="ready")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

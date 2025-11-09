"""SQLAlchemy models for persistent Maimai data."""

# pylint: disable=too-few-public-methods, unsubscriptable-object

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    JSON
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""


class TimestampMixin:
    """Mixin providing created and updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )


CHART_TYPE_ENUM = Enum('STD', 'DX', name='chart_type_enum', validate_strings=True)
CHART_DIFFICULTY_ENUM = Enum(
    'ReMASTER',
    'MASTER',
    'EXPERT',
    'ADVANCED',
    'BASIC',
    name='chart_difficulty_enum',
    validate_strings=True,
)
RECORD_RANK_ENUM = Enum(
    'sssp',
    'sss',
    'ssp',
    'ss',
    'sp',
    's',
    'aaa',
    'aa',
    'a',
    'bbb',
    'bb',
    'b',
    'c',
    'd',
    name='record_rank_enum',
    validate_strings=True,
)
RECORD_SYNC_ENUM = Enum(
    '',
    'sync',
    'fs',
    'fsp',
    'fdx',
    'fdxp',
    name='record_sync_enum',
    validate_strings=True,
)
RECORD_COMBO_ENUM = Enum(
    '',
    'fc',
    'fcp',
    'ap',
    'app',
    name='record_combo_enum',
    validate_strings=True,
)


class Song(TimestampMixin, Base):
    """Music track metadata."""

    __tablename__ = 'songs'

    title: Mapped[str] = mapped_column(String(255), primary_key=True, nullable=False)
    artist: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[Optional[str]] = mapped_column(String(64))
    bpm: Mapped[Optional[str]] = mapped_column(String(32))
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    wiki_url: Mapped[Optional[str]] = mapped_column(Text)
    title_kana: Mapped[Optional[str]] = mapped_column(String(255))
    version: Mapped[Optional[str]] = mapped_column(String(64))

    charts: Mapped[list['Chart']] = relationship(
        back_populates='song',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - repr utility
        return f"<Song title={self.title!r} artist={self.artist!r}>"


class Chart(TimestampMixin, Base):
    """Chart information linked to a song."""

    __tablename__ = 'charts'
    __table_args__ = (
        UniqueConstraint('song_title', 'chart_type', 'difficulty', name='uq_chart_identity'),
    )

    #primary key composite
    song_title: Mapped[str] = mapped_column(
        ForeignKey('songs.title', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
    )
    chart_type: Mapped[str] = mapped_column(CHART_TYPE_ENUM, nullable=False, primary_key=True)
    difficulty: Mapped[str] = mapped_column(CHART_DIFFICULTY_ENUM, nullable=False, primary_key=True)

    internal_constant: Mapped[Optional[float]] = mapped_column(Float)
    designer: Mapped[Optional[str]] = mapped_column(String(255))

    notes_total: Mapped[Optional[int]] = mapped_column(Integer)
    notes_tap: Mapped[Optional[int]] = mapped_column(Integer)
    notes_hold: Mapped[Optional[int]] = mapped_column(Integer)
    notes_slide: Mapped[Optional[int]] = mapped_column(Integer)
    notes_break: Mapped[Optional[int]] = mapped_column(Integer)

    song: Mapped['Song'] = relationship(back_populates='charts')

    def __repr__(self) -> str:  # pragma: no cover - repr utility
        return (
            "<Chart "
            f"song_title={self.song_title!r} "
            f"type={self.chart_type!r} diff={self.difficulty!r}>"
        )


class Record(TimestampMixin, Base):
    """A recorded play for a chart."""

    __tablename__ = 'records'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    discord_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entry: Mapped[dict] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - repr utility
        return f"<Record id={self.id!r} discord_user_id={self.discord_id!r} entries={self.entry!r}>"
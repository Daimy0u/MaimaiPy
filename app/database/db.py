"""Database connection helpers for SQLAlchemy."""

import os
from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()


DEFAULT_DATABASE_URL = 'postgresql://maimaiweb:postgres@localhost:5432/maimai-web'


def _resolve_database_url(database_url: str | None = None) -> str:
    return (
        database_url
        or os.getenv('DATABASE_URL')
        or os.getenv('DATABASE_URI')
        or DEFAULT_DATABASE_URL
    )


def _build_engine(database_url: str | None = None, **engine_kwargs) -> Engine:
    url = _resolve_database_url(database_url)
    kwargs = dict(engine_kwargs)
    connect_args = dict(kwargs.pop('connect_args', {}))

    if url.startswith('sqlite'):
        connect_args = {'check_same_thread': False, **connect_args}

    return create_engine(url, connect_args=connect_args or [], **kwargs)


@lru_cache(maxsize=1)
def _get_cached_engine() -> Engine:
    return _build_engine()


def reset_engine_cache() -> None:
    """Clears the cached default engine."""

    _get_cached_engine.cache_clear()


def get_engine(database_url: str | None = None, **engine_kwargs) -> Engine:
    """Initialises and returns a SQLAlchemy engine instance."""

    if database_url is None and not engine_kwargs:
        return _get_cached_engine()

    return _build_engine(database_url, **engine_kwargs)


@lru_cache(maxsize=None)
def _get_cached_session_factory(
    expire_on_commit: bool,
    autoflush: bool,
) -> sessionmaker:
    return sessionmaker(
        bind=get_engine(),
        expire_on_commit=expire_on_commit,
        autoflush=autoflush,
    )


def reset_session_factory_cache() -> None:
    """Clears cached session factories and engine."""

    _get_cached_session_factory.cache_clear()
    reset_engine_cache()


def get_session_factory(
    engine: Engine | None = None,
    *,
    expire_on_commit: bool = False,
    autoflush: bool = False,
    reset: bool = False,
) -> sessionmaker:
    """Returns a session factory bound to the engine."""

    if reset:
        reset_session_factory_cache()

    if engine is not None:
        return sessionmaker(
            bind=engine,
            expire_on_commit=expire_on_commit,
            autoflush=autoflush,
        )

    return _get_cached_session_factory(expire_on_commit, autoflush)


@contextmanager
def session_scope(engine: Engine | None = None) -> Iterator[Session]:
    """Provides a transactional scope for database operations."""

    session_factory = get_session_factory(engine)
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

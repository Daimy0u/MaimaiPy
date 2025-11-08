"""Database connection helpers for SQLAlchemy."""

import os
from contextlib import contextmanager
from typing import Iterator, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()


DEFAULT_DATABASE_URL = 'postgresql://maimaiweb:postgres@localhost:5432/maimai-web'

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker[Session]] = None


def get_engine(database_url: str | None = None, **engine_kwargs) -> Engine:
    """Initialises and returns a SQLAlchemy engine instance."""
    global _engine

    if database_url is None and not engine_kwargs and _engine is not None:
        return _engine

    url = (
    	database_url
    	or os.getenv('DATABASE_URL')
    	or os.getenv('DATABASE_URI')
    	or DEFAULT_DATABASE_URL
    )
    kwargs = dict(engine_kwargs)
    connect_args = kwargs.pop("connect_args", None)

    if url.startswith('sqlite'):
        connect_args = {'check_same_thread': False, **(connect_args or {})}

    engine = create_engine(url, connect_args=connect_args, **kwargs)

    if database_url is None and not engine_kwargs:
        _engine = engine

    return engine


def get_session_factory(
    engine: Engine | None = None,
    *,
    expire_on_commit: bool = False,
    autoflush: bool = False,
    reset: bool = False,
) -> sessionmaker[Session]:
    """Returns a session factory bound to the engine."""

    global _SessionFactory

    if reset:
        _SessionFactory = None

    if _SessionFactory is not None and engine is None:
        return _SessionFactory

    bound_engine = engine or get_engine()
    factory = sessionmaker(
        bind=bound_engine,
        expire_on_commit=expire_on_commit,
        autoflush=autoflush,
    )
    if engine is None:
        _SessionFactory = factory

    return factory


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

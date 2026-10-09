"""
GLYAB AI
Database Infrastructure

MySQL + SQLAlchemy database layer.
"""

from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


logger = logging.getLogger("glyab.database")


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    query={
        "charset": "utf8mb4",
    },
)


# ============================================================
# SQLALCHEMY ENGINE
# ============================================================

engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": settings.DB_CONNECT_TIMEOUT,
    },
    echo=False,
    future=True,
)


# ============================================================
# SESSION FACTORY
# ============================================================

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ============================================================
# ORM BASE
# ============================================================

class Base(DeclarativeBase):
    """Base class for all GLYAB ORM models."""

    pass


# ============================================================
# DATABASE SESSION
# ============================================================

def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for each API request.
    """

    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# DATABASE HEALTH CHECK
# ============================================================

def check_database_connection() -> bool:
    """
    Check whether MySQL is reachable.
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as exc:
        logger.error(
            "MySQL connection failed: %s",
            exc,
        )

        return False


# ============================================================
# DATABASE INFORMATION
# ============================================================

def get_database_info() -> dict:
    """
    Return safe database configuration information.

    Password is intentionally never returned.
    """

    return {
        "engine": "MySQL",
        "driver": "PyMySQL",
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
    }
from __future__ import annotations

from typing import Any

from sqlalchemy import Table

from app.core.database import Base, engine


class GlacialLake(Base):
    """
    GLYAB Advanced Glacial Lake Model.

    Existing MySQL `glacial_lakes` table ko automatically
    reflect karta hai. Database me koi data create/update nahi karta.
    """

    __tablename__ = "glacial_lakes"

    __table__ = Table(
        __tablename__,
        Base.metadata,
        autoload_with=engine,
    )

    @classmethod
    def columns(cls) -> list[str]:
        """Actual MySQL table ke columns."""

        return [
            column.name
            for column in cls.__table__.columns
        ]

    @classmethod
    def serialize(cls, row: Any) -> dict[str, Any]:
        """Database row ko JSON-compatible dictionary me convert karta hai."""

        if hasattr(row, "_mapping"):
            data = dict(row._mapping)
        else:
            data = {
                column.name: getattr(
                    row,
                    column.name,
                    None,
                )
                for column in cls.__table__.columns
            }

        return {
            key: cls._normalize_value(value)
            for key, value in data.items()
        }

    @staticmethod
    def _normalize_value(value: Any) -> Any:

        if value is None:
            return None

        if hasattr(value, "isoformat"):
            return value.isoformat()

        if hasattr(value, "item"):
            try:
                return value.item()
            except Exception:
                pass

        return value


glacial_lakes_table = GlacialLake.__table__
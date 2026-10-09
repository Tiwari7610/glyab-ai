from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DECIMAL, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Glacier(Base):
    __tablename__ = "glaciers"

    glacier_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    glacier_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    glacier_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India",
    )

    state_province: Mapped[str | None] = mapped_column(
        String(150)
    )

    region: Mapped[str | None] = mapped_column(
        String(150)
    )

    mountain_range: Mapped[str | None] = mapped_column(
        String(150)
    )

    latitude: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 7),
        nullable=False,
    )

    longitude: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 7),
        nullable=False,
    )

    elevation_min_m: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2)
    )

    elevation_max_m: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2)
    )

    mean_elevation_m: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2)
    )

    area_km2: Mapped[Decimal | None] = mapped_column(
        DECIMAL(14, 6)
    )

    length_km: Mapped[Decimal | None] = mapped_column(
        DECIMAL(12, 5)
    )

    width_km: Mapped[Decimal | None] = mapped_column(
        DECIMAL(12, 5)
    )

    estimated_ice_thickness_m: Mapped[Decimal | None] = mapped_column(
        DECIMAL(12, 2)
    )

    glacier_type: Mapped[str] = mapped_column(
        Enum(
            "VALLEY",
            "MOUNTAIN",
            "ICE_CAP",
            "ICE_FIELD",
            "HANGING",
            "CIRQUE",
            "UNKNOWN",
            name="glacier_type_enum",
        ),
        nullable=False,
        default="UNKNOWN",
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "ACTIVE",
            "RETREATING",
            "ADVANCING",
            "STABLE",
            "CRITICAL",
            "UNKNOWN",
            name="glacier_status_enum",
        ),
        nullable=False,
        default="UNKNOWN",
    )

    data_source: Mapped[str | None] = mapped_column(
        String(150)
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(500)
    )

    source_dataset_version: Mapped[str | None] = mapped_column(
        String(100)
    )

    first_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    last_observed_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    observation_count: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime
    )
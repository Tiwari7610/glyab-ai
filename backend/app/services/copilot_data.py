"""
GLYAB AI - Copilot Data Intelligence Layer

Purpose:
    Provides trusted, database-backed information to the GLYAB AI Copilot.

Data sources:
    - MySQL glaciers table
    - MySQL glacial_lakes table

Important:
    This module NEVER creates synthetic scientific measurements.
    Missing values are returned as None / unknown.
"""

from __future__ import annotations

import math
from typing import Any

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.glacier import Glacier
from app.models.lake import GlacialLake


class CopilotDataEngine:
    """
    Database intelligence layer used by GLYAB AI Copilot.
    """

    # ============================================================
    # DATABASE HELPER
    # ============================================================

    def _session(self):
        return SessionLocal()

    # ============================================================
    # GLACIER STATISTICS
    # ============================================================

    def glacier_statistics(self) -> dict[str, Any]:
        """
        Return high-level statistics for the glacier inventory.
        """

        db = self._session()

        try:
            total = db.scalar(
                select(func.count(Glacier.glacier_id))
            ) or 0

            total_area = db.scalar(
                select(func.coalesce(func.sum(Glacier.area_km2), 0))
            ) or 0

            average_area = db.scalar(
                select(func.coalesce(func.avg(Glacier.area_km2), 0))
            ) or 0

            average_elevation = db.scalar(
                select(
                    func.coalesce(
                        func.avg(Glacier.mean_elevation_m),
                        0,
                    )
                )
            ) or 0

            maximum_elevation = db.scalar(
                select(
                    func.coalesce(
                        func.max(Glacier.elevation_max_m),
                        0,
                    )
                )
            ) or 0

            return {
                "total_glaciers": int(total),
                "total_area_km2": round(float(total_area), 4),
                "average_area_km2": round(float(average_area), 4),
                "average_elevation_m": round(
                    float(average_elevation),
                    2,
                ),
                "maximum_elevation_m": round(
                    float(maximum_elevation),
                    2,
                ),
                "data_source": "RGI 7.0",
            }

        finally:
            db.close()

    # ============================================================
    # LAKE STATISTICS
    # ============================================================

    def lake_statistics(self) -> dict[str, Any]:
        """
        Return statistics for currently loaded glacial lakes.

        If the HMA_GLI records have not yet been inserted into
        MySQL, this safely returns zero rather than inventing data.
        """

        db = self._session()

        try:
            total = db.scalar(
                select(func.count(GlacialLake.lake_id))
            ) or 0

            total_area = db.scalar(
                select(
                    func.coalesce(
                        func.sum(GlacialLake.area_km2),
                        0,
                    )
                )
            ) or 0

            average_area = db.scalar(
                select(
                    func.coalesce(
                        func.avg(GlacialLake.area_km2),
                        0,
                    )
                )
            ) or 0

            average_water_level = db.scalar(
                select(
                    func.coalesce(
                        func.avg(GlacialLake.water_level_m),
                        0,
                    )
                )
            ) or 0

            return {
                "total_lakes": int(total),
                "total_area_km2": round(
                    float(total_area),
                    4,
                ),
                "average_area_km2": round(
                    float(average_area),
                    4,
                ),
                "average_water_level_m": round(
                    float(average_water_level),
                    3,
                ),
                "data_source": "NASA NSIDC HMA_GLI",
            }

        finally:
            db.close()

    # ============================================================
    # PROJECT OVERVIEW
    # ============================================================

    def project_overview(self) -> dict[str, Any]:
        """
        Combined overview for the Copilot.
        """

        glacier = self.glacier_statistics()
        lake = self.lake_statistics()

        return {
            "system": "GLYAB",
            "mission": "Cryosphere Intelligence & GLOF Early Warning",
            "glaciers": glacier,
            "glacial_lakes": lake,
        }

    # ============================================================
    # GLACIER SEARCH
    # ============================================================

    def search_glaciers(
        self,
        query: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search glacier records by name or RGI code.
        """

        db = self._session()

        try:
            statement = select(Glacier)

            if query:
                pattern = f"%{query.strip()}%"

                statement = statement.where(
                    (Glacier.glacier_name.ilike(pattern))
                    | (Glacier.glacier_code.ilike(pattern))
                )

            statement = statement.limit(
                max(1, min(limit, 100))
            )

            records = db.scalars(statement).all()

            return [
                self._glacier_to_dict(glacier)
                for glacier in records
            ]

        finally:
            db.close()

    # ============================================================
    # LARGEST GLACIERS
    # ============================================================

    def largest_glaciers(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return glaciers sorted by area.
        """

        db = self._session()

        try:
            statement = (
                select(Glacier)
                .where(Glacier.area_km2.is_not(None))
                .order_by(
                    Glacier.area_km2.desc()
                )
                .limit(max(1, min(limit, 100)))
            )

            records = db.scalars(statement).all()

            return [
                self._glacier_to_dict(glacier)
                for glacier in records
            ]

        finally:
            db.close()

    # ============================================================
    # HIGHEST GLACIERS
    # ============================================================

    def highest_glaciers(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return glaciers sorted by maximum elevation.
        """

        db = self._session()

        try:
            statement = (
                select(Glacier)
                .where(
                    Glacier.elevation_max_m.is_not(None)
                )
                .order_by(
                    Glacier.elevation_max_m.desc()
                )
                .limit(max(1, min(limit, 100)))
            )

            records = db.scalars(statement).all()

            return [
                self._glacier_to_dict(glacier)
                for glacier in records
            ]

        finally:
            db.close()

    # ============================================================
    # LAKE SEARCH
    # ============================================================

    def search_lakes(
        self,
        query: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search glacial lakes by lake name or lake code.
        """

        db = self._session()

        try:
            statement = select(GlacialLake)

            if query:
                pattern = f"%{query.strip()}%"

                statement = statement.where(
                    (GlacialLake.lake_name.ilike(pattern))
                    | (GlacialLake.lake_code.ilike(pattern))
                )

            statement = statement.limit(
                max(1, min(limit, 100))
            )

            records = db.scalars(statement).all()

            return [
                self._lake_to_dict(lake)
                for lake in records
            ]

        finally:
            db.close()

    # ============================================================
    # LARGEST LAKES
    # ============================================================

    def largest_lakes(
        self,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Return lakes sorted by area.
        """

        db = self._session()

        try:
            statement = (
                select(GlacialLake)
                .where(
                    GlacialLake.area_km2.is_not(None)
                )
                .order_by(
                    GlacialLake.area_km2.desc()
                )
                .limit(max(1, min(limit, 100)))
            )

            records = db.scalars(statement).all()

            return [
                self._lake_to_dict(lake)
                for lake in records
            ]

        finally:
            db.close()

    # ============================================================
    # NEAREST GLACIERS
    # ============================================================

    def nearest_glaciers(
        self,
        latitude: float,
        longitude: float,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Find nearest glaciers using Haversine distance.

        This is an approximate geographic association based on
        glacier centroid coordinates.

        It does NOT claim that a lake is physically connected to
        a glacier.
        """

        db = self._session()

        try:
            statement = select(
                Glacier.glacier_id,
                Glacier.glacier_code,
                Glacier.glacier_name,
                Glacier.latitude,
                Glacier.longitude,
                Glacier.area_km2,
                Glacier.mean_elevation_m,
            ).where(
                Glacier.latitude.is_not(None),
                Glacier.longitude.is_not(None),
            )

            rows = db.execute(statement).all()

            results: list[dict[str, Any]] = []

            for row in rows:

                if row.latitude is None:
                    continue

                if row.longitude is None:
                    continue

                distance = self._haversine_km(
                    latitude,
                    longitude,
                    float(row.latitude),
                    float(row.longitude),
                )

                results.append(
                    {
                        "glacier_id": row.glacier_id,
                        "glacier_code": row.glacier_code,
                        "glacier_name": row.glacier_name,
                        "latitude": float(row.latitude),
                        "longitude": float(row.longitude),
                        "area_km2": (
                            float(row.area_km2)
                            if row.area_km2 is not None
                            else None
                        ),
                        "mean_elevation_m": (
                            float(row.mean_elevation_m)
                            if row.mean_elevation_m
                            is not None
                            else None
                        ),
                        "distance_km": round(
                            distance,
                            3,
                        ),
                    }
                )

            results.sort(
                key=lambda item: item["distance_km"]
            )

            return results[: max(1, min(limit, 20))]

        finally:
            db.close()

    # ============================================================
    # LAKE → NEAREST GLACIER
    # ============================================================

    def associate_lake_with_glaciers(
        self,
        lake_id: int,
        limit: int = 5,
    ) -> dict[str, Any] | None:
        """
        Calculate nearest glacier candidates for a lake.

        This does not modify the database.
        """

        db = self._session()

        try:
            lake = db.get(
                GlacialLake,
                lake_id,
            )

            if lake is None:
                return None

            if (
                lake.latitude is None
                or lake.longitude is None
            ):
                return {
                    "lake": self._lake_to_dict(lake),
                    "association_available": False,
                    "reason": (
                        "Lake coordinates are unavailable."
                    ),
                    "nearest_glaciers": [],
                }

            nearest = self.nearest_glaciers(
                float(lake.latitude),
                float(lake.longitude),
                limit,
            )

            return {
                "lake": self._lake_to_dict(lake),
                "association_available": True,
                "method": (
                    "Haversine distance using "
                    "inventory coordinates"
                ),
                "nearest_glaciers": nearest,
            }

        finally:
            db.close()

    # ============================================================
    # HIGH ALTITUDE GLACIERS
    # ============================================================

    def high_altitude_glaciers(
        self,
        minimum_elevation_m: float = 6000,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Find glaciers above a specified elevation threshold.
        """

        db = self._session()

        try:
            statement = (
                select(Glacier)
                .where(
                    Glacier.elevation_max_m
                    >= minimum_elevation_m
                )
                .order_by(
                    Glacier.elevation_max_m.desc()
                )
                .limit(max(1, min(limit, 100)))
            )

            records = db.scalars(statement).all()

            return [
                self._glacier_to_dict(glacier)
                for glacier in records
            ]

        finally:
            db.close()

    # ============================================================
    # INTERNAL SERIALIZATION
    # ============================================================

    @staticmethod
    def _glacier_to_dict(
        glacier: Glacier,
    ) -> dict[str, Any]:

        return {
            "glacier_id": glacier.glacier_id,
            "glacier_code": glacier.glacier_code,
            "glacier_name": glacier.glacier_name,
            "country": glacier.country,
            "state_province": glacier.state_province,
            "region": glacier.region,
            "mountain_range": glacier.mountain_range,
            "latitude": (
                float(glacier.latitude)
                if glacier.latitude is not None
                else None
            ),
            "longitude": (
                float(glacier.longitude)
                if glacier.longitude is not None
                else None
            ),
            "elevation_min_m": (
                float(glacier.elevation_min_m)
                if glacier.elevation_min_m is not None
                else None
            ),
            "elevation_max_m": (
                float(glacier.elevation_max_m)
                if glacier.elevation_max_m is not None
                else None
            ),
            "mean_elevation_m": (
                float(glacier.mean_elevation_m)
                if glacier.mean_elevation_m is not None
                else None
            ),
            "area_km2": (
                float(glacier.area_km2)
                if glacier.area_km2 is not None
                else None
            ),
            "data_source": glacier.data_source,
            "source_dataset_version": (
                glacier.source_dataset_version
            ),
        }

    @staticmethod
    def _lake_to_dict(
        lake: GlacialLake,
    ) -> dict[str, Any]:

        return {
            "lake_id": lake.lake_id,
            "lake_code": lake.lake_code,
            "lake_name": lake.lake_name,
            "glacier_id": lake.glacier_id,
            "latitude": (
                float(lake.latitude)
                if lake.latitude is not None
                else None
            ),
            "longitude": (
                float(lake.longitude)
                if lake.longitude is not None
                else None
            ),
            "elevation_m": (
                float(lake.elevation_m)
                if lake.elevation_m is not None
                else None
            ),
            "area_km2": (
                float(lake.area_km2)
                if lake.area_km2 is not None
                else None
            ),
            "water_level_m": (
                float(lake.water_level_m)
                if lake.water_level_m is not None
                else None
            ),
            "hazard_level": (
                lake.hazard_level.value
                if hasattr(lake.hazard_level, "value")
                else lake.hazard_level
            ),
            "monitoring_status": (
                lake.monitoring_status.value
                if hasattr(
                    lake.monitoring_status,
                    "value",
                )
                else lake.monitoring_status
            ),
            "data_source": lake.data_source,
            "dataset_version": lake.dataset_version,
        }

    # ============================================================
    # HAVERSINE
    # ============================================================

    @staticmethod
    def _haversine_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:

        earth_radius_km = 6371.0088

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)

        delta_lat = math.radians(
            lat2 - lat1
        )

        delta_lon = math.radians(
            lon2 - lon1
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad)
            * math.cos(lat2_rad)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a),
        )

        return earth_radius_km * c


# ================================================================
# SINGLETON
# ================================================================

copilot_data = CopilotDataEngine()
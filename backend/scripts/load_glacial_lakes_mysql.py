from __future__ import annotations

from pathlib import Path
import hashlib

import pandas as pd
from sqlalchemy import text

from app.core.database import engine


# ============================================================
# GLYAB â€” HMA_GLI â†’ MYSQL PRODUCTION LOADER
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "glacial_lakes"
    / "hma_gli_india_himalaya_2010_14.csv"
)

TABLE_NAME = "glacial_lakes"

SOURCE = "NASA NSIDC HMA_GLI"
VERSION = "V001"
TEMPORAL_PERIOD = "2010-2014"
SOURCE_REFERENCE = (
    "NASA NSIDC HMA_GLI Version 1, 2010-2014"
)


# ============================================================
# REQUIRED SOURCE COLUMNS
# ============================================================

REQUIRED_COLUMNS = {
    "Geo_ID",
    "FULL_NAME",
    "Country",
    "ISO",
    "RGI_CODE",
    "Year_Start",
    "YearRange",
    "latitude",
    "longitude",
    "area_m2",
    "area_km2",
    "data_source",
    "dataset_version",
    "temporal_period",
    "spatial_filter",
    "geometry_available",
}


# ============================================================
# ENUM VALUES â€” MATCH MYSQL SCHEMA
# ============================================================

VALID_LAKE_TYPES = {
    "PROGLACIAL",
    "SUPRAGLACIAL",
    "SUBGLACIAL",
    "ICE_DAMMED",
    "MORAINE_DAMMED",
    "UNKNOWN",
}

VALID_DAM_TYPES = {
    "MORAINE",
    "ICE",
    "ROCK",
    "MIXED",
    "UNKNOWN",
}

VALID_HAZARD_LEVELS = {
    "LOW",
    "MODERATE",
    "HIGH",
    "CRITICAL",
    "UNKNOWN",
}

VALID_MONITORING_STATUS = {
    "ACTIVE",
    "INACTIVE",
    "SEASONAL",
    "UNKNOWN",
}


# ============================================================
# HELPERS
# ============================================================

def clean_text(value) -> str | None:
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def clean_number(value) -> float | None:
    if pd.isna(value):
        return None

    return float(value)


def make_lake_code(
    geo_id: str,
    occurrence: int,
) -> str:
    """
    Creates a deterministic unique internal lake code.

    Duplicate Geo_ID values are intentionally preserved.
    """

    raw = f"{geo_id}|{occurrence}"

    digest = hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:12]

    return f"HMA-{digest.upper()}"


def validate_coordinate(
    latitude: float,
    longitude: float,
) -> None:

    if not -90 <= latitude <= 90:
        raise ValueError(
            f"Invalid latitude: {latitude}"
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            f"Invalid longitude: {longitude}"
        )


def validate_area(area_km2: float) -> None:

    if area_km2 <= 0:
        raise ValueError(
            f"Invalid lake area: {area_km2}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 78)
    print("GLYAB â€” HMA_GLI â†’ MYSQL PRODUCTION LOADER")
    print("=" * 78)

    print(f"Source file : {CSV_PATH}")
    print(f"Dataset     : {SOURCE}")
    print(f"Version     : {VERSION}")
    print(f"Period      : {TEMPORAL_PERIOD}")
    print()

    # ========================================================
    # 1. FILE CHECK
    # ========================================================

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Source CSV not found:\n{CSV_PATH}"
        )

    # ========================================================
    # 2. LOAD DATASET
    # ========================================================

    df = pd.read_csv(CSV_PATH)

    print(
        f"CSV records : {len(df)}"
    )

    if df.empty:
        raise ValueError(
            "CSV contains zero records."
        )

    # ========================================================
    # 3. COLUMN VALIDATION
    # ========================================================

    missing_columns = (
        REQUIRED_COLUMNS
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required columns:\n"
            + "\n".join(
                sorted(missing_columns)
            )
        )

    print("Column validation : OK")

    # ========================================================
    # 4. DATA QUALITY VALIDATION
    # ========================================================

    if df["latitude"].isna().any():

        raise ValueError(
            "NULL latitude detected."
        )

    if df["longitude"].isna().any():

        raise ValueError(
            "NULL longitude detected."
        )

    if df["area_km2"].isna().any():

        raise ValueError(
            "NULL area_km2 detected."
        )

    # Coordinate validation

    for index, row in df.iterrows():

        latitude = float(
            row["latitude"]
        )

        longitude = float(
            row["longitude"]
        )

        area_km2 = float(
            row["area_km2"]
        )

        validate_coordinate(
            latitude,
            longitude,
        )

        validate_area(
            area_km2
        )

    print("Coordinate validation : OK")
    print("Area validation       : OK")

    # ========================================================
    # 5. DUPLICATE ANALYSIS
    # ========================================================

    duplicate_records = int(
        df.duplicated(
            subset=["Geo_ID"],
            keep=False,
        ).sum()
    )

    unique_geo_ids = int(
        df["Geo_ID"].nunique()
    )

    unique_rgi_codes = int(
        df["RGI_CODE"].nunique()
    )

    print()
    print("DATASET QUALITY")
    print("-" * 50)

    print(
        f"Total records              : {len(df)}"
    )

    print(
        f"Unique Geo_ID              : {unique_geo_ids}"
    )

    print(
        f"Records in duplicate groups: "
        f"{duplicate_records}"
    )

    print(
        f"Unique RGI_CODE            : "
        f"{unique_rgi_codes}"
    )

    # ========================================================
    # 6. CREATE DETERMINISTIC OCCURRENCE
    # ========================================================

    df["_occurrence"] = (
        df.groupby(
            "Geo_ID",
            dropna=False,
        )
        .cumcount()
        + 1
    )

    # ========================================================
    # 7. CREATE UNIQUE LAKE CODE
    # ========================================================

    df["lake_code"] = [
        make_lake_code(
            clean_text(
                row["Geo_ID"]
            )
            or "UNKNOWN",
            int(
                row["_occurrence"]
            ),
        )
        for _, row in df.iterrows()
    ]

    if df["lake_code"].duplicated().any():

        raise ValueError(
            "Lake code collision detected."
        )

    print(
        "Lake-code generation       : OK"
    )

    # ========================================================
    # 8. PREVIEW
    # ========================================================

    print()
    print("DATA PREVIEW")
    print("-" * 78)

    preview_columns = [
        "Geo_ID",
        "RGI_CODE",
        "latitude",
        "longitude",
        "area_km2",
        "lake_code",
    ]

    print(
        df[preview_columns]
        .head(5)
        .to_string(
            index=False
        )
    )

    # ========================================================
    # 9. GET EXISTING RECORDS
    # ========================================================

    with engine.connect() as connection:

        existing_codes = set(
            connection.execute(
                text(
                    """
                    SELECT lake_code
                    FROM glacial_lakes
                    WHERE lake_code IS NOT NULL
                    """
                )
            )
            .scalars()
            .all()
        )

        max_lake_id = (
            connection.execute(
                text(
                    """
                    SELECT COALESCE(
                        MAX(lake_id),
                        0
                    )
                    FROM glacial_lakes
                    """
                )
            )
            .scalar()
        )

    next_lake_id = int(
        max_lake_id or 0
    ) + 1

    print()
    print(
        f"Existing lake records : "
        f"{len(existing_codes)}"
    )

    print(
        f"Next available lake_id: "
        f"{next_lake_id}"
    )

    # ========================================================
    # 10. MYSQL INSERT STATEMENT
    # ========================================================

    insert_sql = text(
        """
        INSERT INTO glacial_lakes
        (
            lake_id,
            lake_code,
            lake_name,
            glacier_id,
            latitude,
            longitude,
            elevation_m,
            area_km2,

            lake_type,
            dam_type,
            hazard_level,
            monitoring_status,

            observation_count,
            first_observed_at,
            last_observed_at,

            data_source,
            source_reference,
            dataset_version
        )
        VALUES
        (
            :lake_id,
            :lake_code,
            :lake_name,
            :glacier_id,
            :latitude,
            :longitude,
            :elevation_m,
            :area_km2,

            :lake_type,
            :dam_type,
            :hazard_level,
            :monitoring_status,

            :observation_count,
            :first_observed_at,
            :last_observed_at,

            :data_source,
            :source_reference,
            :dataset_version
        )
        """
    )

    # ========================================================
    # 11. LOAD TRANSACTION
    # ========================================================

    inserted = 0
    skipped = 0
    glacier_links = 0

    print()
    print("STARTING MYSQL TRANSACTION...")
    print()

    try:

        with engine.begin() as connection:

            current_lake_id = next_lake_id

            for _, row in df.iterrows():

                lake_code = row[
                    "lake_code"
                ]

                # ------------------------------------------------
                # Idempotency
                # ------------------------------------------------

                if lake_code in existing_codes:

                    skipped += 1
                    continue

                # ------------------------------------------------
                # Resolve glacier relation
                # ------------------------------------------------

                glacier_id = None

                rgi_code = clean_text(
                    row["RGI_CODE"]
                )

                if rgi_code:

                    glacier_id = connection.execute(
                        text(
                            """
                            SELECT glacier_id
                            FROM glaciers
                            WHERE glacier_code = :code
                            LIMIT 1
                            """
                        ),
                        {
                            "code": rgi_code
                        },
                    ).scalar_one_or_none()

                    if glacier_id is not None:

                        glacier_links += 1

                # ------------------------------------------------
                # Source-derived name
                # ------------------------------------------------

                source_name = clean_text(
                    row["FULL_NAME"]
                )

                if source_name:

                    lake_name = (
                        "HMA_GLI "
                        + source_name
                        + " "
                        + str(row["Geo_ID"])
                        + "-"
                        + str(
                            int(
                                row["_occurrence"]
                            )
                        )
                    )

                else:

                    lake_name = (
                        "HMA_GLI Lake "
                        + str(row["Geo_ID"])
                        + "-"
                        + str(
                            int(
                                row["_occurrence"]
                            )
                        )
                    )

                # ------------------------------------------------
                # INSERT
                # ------------------------------------------------

                connection.execute(
                    insert_sql,
                    {
                        "lake_id": current_lake_id,

                        "lake_code": lake_code,

                        "lake_name": lake_name,

                        "glacier_id": glacier_id,

                        "latitude": clean_number(
                            row["latitude"]
                        ),

                        "longitude": clean_number(
                            row["longitude"]
                        ),

                        # Not present in current
                        # validated HMA_GLI CSV.
                        "elevation_m": None,

                        "area_km2": clean_number(
                            row["area_km2"]
                        ),

                        # No classification in
                        # current source subset.
                        "lake_type": "UNKNOWN",

                        "dam_type": "UNKNOWN",

                        # IMPORTANT:
                        # These are NOT predicted by
                        # HMA_GLI itself.
                        "hazard_level": "UNKNOWN",

                        "monitoring_status": "UNKNOWN",

                        # One source observation.
                        "observation_count": 1,

                        "first_observed_at": None,

                        "last_observed_at": None,

                        "data_source": SOURCE,

                        "source_reference": (
                            SOURCE_REFERENCE
                        ),

                        "dataset_version": VERSION,
                    },
                )

                existing_codes.add(
                    lake_code
                )

                current_lake_id += 1

                inserted += 1

        print()
        print(
            "MYSQL TRANSACTION : COMMITTED"
        )

    except Exception as exc:

        print()
        print(
            "MYSQL TRANSACTION : ROLLED BACK"
        )

        print()
        print(
            "ERROR TYPE:"
        )

        print(
            type(exc).__name__
        )

        print()
        print(
            "ERROR:"
        )

        print(
            str(exc)
        )

        raise

    # ========================================================
    # 12. FINAL DATABASE VERIFICATION
    # ========================================================

    with engine.connect() as connection:

        source_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM glacial_lakes
                WHERE data_source = :source
                """
            ),
            {
                "source": SOURCE
            },
        ).scalar()

        total_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM glacial_lakes
                """
            )
        ).scalar()

        linked_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM glacial_lakes
                WHERE data_source = :source
                  AND glacier_id IS NOT NULL
                """
            ),
            {
                "source": SOURCE
            },
        ).scalar()

    # ========================================================
    # 13. FINAL REPORT
    # ========================================================

    print()
    print("=" * 78)
    print("GLYAB â€” HMA_GLI LOAD COMPLETE")
    print("=" * 78)

    print(
        f"Source CSV records       : {len(df)}"
    )

    print(
        f"New records inserted     : {inserted}"
    )

    print(
        f"Already existing/skipped : {skipped}"
    )

    print(
        f"HMA_GLI records in MySQL : "
        f"{source_count}"
    )

    print(
        f"Total glacial_lakes rows : "
        f"{total_count}"
    )

    print(
        f"Glacier-linked lakes     : "
        f"{linked_count}"
    )

    print(
        "Synthetic scientific data : 0"
    )

    print(
        "Hazard prediction         : NOT GENERATED"
    )

    print(
        "Geometry available        : FALSE"
    )

    print(
        "Source                     : "
        f"{SOURCE}"
    )

    print(
        "Dataset version            : "
        f"{VERSION}"
    )

    print(
        "Temporal period            : "
        f"{TEMPORAL_PERIOD}"
    )

    print("=" * 78)
    print()


if __name__ == "__main__":
    main()

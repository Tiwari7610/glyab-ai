from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.core.database import engine


# ============================================================
# GLYAB STEP 3
# RGI GLACIER MASTER -> MYSQL
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "glacier_master.csv"
)


# ============================================================
# REQUIRED CSV COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "rgi_id",
    "glacier_name",
    "latitude",
    "longitude",
    "area_km2",
    "min_elevation_m",
    "max_elevation_m",
    "median_elevation_m",
    "data_source",
    "source_version",
]


# ============================================================
# START
# ============================================================

print("=" * 70)
print("GLYAB STEP 3 - GLACIER MASTER -> MYSQL")
print("=" * 70)

print(f"\nInput CSV:")
print(CSV_FILE)


# ============================================================
# FILE CHECK
# ============================================================

if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"\nCSV file not found:\n{CSV_FILE}"
    )


# ============================================================
# LOAD CSV
# ============================================================

print("\n" + "=" * 70)
print("1. LOADING GLACIER MASTER CSV")
print("=" * 70)

df = pd.read_csv(
    CSV_FILE
)

print(
    f"CSV records loaded : {len(df):,}"
)


print("\nCSV columns:")

for column in df.columns:
    print(f"  - {column}")


# ============================================================
# COLUMN VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("2. VALIDATING CSV")
print("=" * 70)

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "\nMissing required CSV columns:\n"
        + "\n".join(
            f"  - {column}"
            for column in missing_columns
        )
    )


print("Required columns: OK")


# ============================================================
# RGI ID VALIDATION
# ============================================================

print("\nChecking RGI IDs...")

df["rgi_id"] = (
    df["rgi_id"]
    .astype(str)
    .str.strip()
)

invalid_rgi = (
    df["rgi_id"].isna()
    |
    (df["rgi_id"] == "")
)

print(
    f"Invalid RGI IDs : {invalid_rgi.sum():,}"
)

if invalid_rgi.any():
    raise ValueError(
        "Invalid RGI IDs detected."
    )


duplicate_rgi = (
    df["rgi_id"]
    .duplicated()
)

print(
    f"Duplicate RGI IDs : "
    f"{duplicate_rgi.sum():,}"
)

if duplicate_rgi.any():

    raise ValueError(
        "Duplicate RGI IDs found in CSV."
    )


# ============================================================
# GLACIER NAME VALIDATION
# ============================================================

print("\nChecking glacier names...")

df["glacier_name"] = (
    df["glacier_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

missing_names = (
    df["glacier_name"] == ""
)

print(
    f"Missing glacier names : "
    f"{missing_names.sum():,}"
)

# RGI often has unnamed glaciers.
# We create a deterministic database-safe name
# from the RGI identifier rather than inventing a
# geographic glacier name.

df.loc[
    missing_names,
    "glacier_name"
] = (
    "Unnamed glacier "
    + df.loc[
        missing_names,
        "rgi_id"
    ]
)


# ============================================================
# NUMERIC VALIDATION
# ============================================================

print("\nValidating numeric fields...")

numeric_columns = [
    "latitude",
    "longitude",
    "area_km2",
    "min_elevation_m",
    "max_elevation_m",
    "median_elevation_m",
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


invalid_coordinates = (
    df["latitude"].isna()
    |
    df["longitude"].isna()
)

print(
    f"Missing coordinates : "
    f"{invalid_coordinates.sum():,}"
)


invalid_area = (
    df["area_km2"].isna()
    |
    (df["area_km2"] <= 0)
)

print(
    f"Invalid area values : "
    f"{invalid_area.sum():,}"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

print("\n" + "=" * 70)
print("3. CONNECTING TO MYSQL")
print("=" * 70)

with engine.begin() as connection:

    print(
        "MySQL connection: OK"
    )

    # --------------------------------------------------------
    # Check table
    # --------------------------------------------------------

    table_check = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM glaciers
            """
        )
    )

    existing_count = (
        table_check.scalar()
        or 0
    )

    print(
        f"Existing glacier records : "
        f"{existing_count:,}"
    )


# ============================================================
# CHECK EXISTING GLACIER CODES
# ============================================================

print("\n" + "=" * 70)
print("4. CHECKING EXISTING RGI RECORDS")
print("=" * 70)

with engine.connect() as connection:

    existing_codes = pd.read_sql(
        text(
            """
            SELECT glacier_code
            FROM glaciers
            WHERE glacier_code IS NOT NULL
            """
        ),
        connection,
    )


existing_code_set = set(
    existing_codes[
        "glacier_code"
    ]
    .astype(str)
)


print(
    f"Existing glacier codes : "
    f"{len(existing_code_set):,}"
)


# ============================================================
# REMOVE ALREADY LOADED RECORDS
# ============================================================

df["already_loaded"] = (
    df["rgi_id"]
    .isin(existing_code_set)
)


already_loaded_count = (
    df["already_loaded"]
    .sum()
)


print(
    f"Already loaded          : "
    f"{already_loaded_count:,}"
)


new_df = df[
    ~df["already_loaded"]
].copy()


print(
    f"New records to insert   : "
    f"{len(new_df):,}"
)


if new_df.empty:

    print(
        "\nNo new glacier records "
        "need to be inserted."
    )

    print(
        "\nGLYAB STEP 3 COMPLETE."
    )

    raise SystemExit(0)


# ============================================================
# GET NEXT GLACIER ID
# ============================================================

print("\n" + "=" * 70)
print("5. PREPARING DATABASE IDS")
print("=" * 70)

with engine.connect() as connection:

    result = connection.execute(
        text(
            """
            SELECT COALESCE(
                MAX(glacier_id),
                0
            )
            FROM glaciers
            """
        )
    )

    max_glacier_id = (
        result.scalar()
        or 0
    )


print(
    f"Current maximum glacier_id : "
    f"{max_glacier_id:,}"
)


new_df = new_df.reset_index(
    drop=True
)

new_df["glacier_id"] = (
    max_glacier_id
    +
    new_df.index
    +
    1
)


# ============================================================
# PREPARE MYSQL RECORDS
# ============================================================

print("\n" + "=" * 70)
print("6. MAPPING RGI -> GLYAB SCHEMA")
print("=" * 70)


records = []


for _, row in new_df.iterrows():

    glacier_code = (
        str(row["rgi_id"])
        .strip()
    )

    glacier_name = (
        str(row["glacier_name"])
        .strip()
    )

    # --------------------------------------------------------
    # Scientific values directly from RGI
    # --------------------------------------------------------

    latitude = row["latitude"]

    longitude = row["longitude"]

    area_km2 = row["area_km2"]

    elevation_min = (
        row["min_elevation_m"]
    )

    elevation_max = (
        row["max_elevation_m"]
    )

    mean_elevation = (
        row["median_elevation_m"]
    )

    # --------------------------------------------------------
    # Build record
    # --------------------------------------------------------

    record = {

        "glacier_id": int(
            row["glacier_id"]
        ),

        "glacier_code": glacier_code,

        "glacier_name": glacier_name,

        "country": "India",

        # RGI master CSV currently does not
        # contain exact state attribution.
        # Keep NULL instead of guessing.
        "state_province": None,

        "region": (
            str(row["o1region"])
            if pd.notna(row.get("o1region"))
            else None
        ),

        "mountain_range": None,

        "latitude": (
            float(latitude)
            if pd.notna(latitude)
            else None
        ),

        "longitude": (
            float(longitude)
            if pd.notna(longitude)
            else None
        ),

        "elevation_min_m": (
            float(elevation_min)
            if pd.notna(elevation_min)
            else None
        ),

        "elevation_max_m": (
            float(elevation_max)
            if pd.notna(elevation_max)
            else None
        ),

        "mean_elevation_m": (
            float(mean_elevation)
            if pd.notna(mean_elevation)
            else None
        ),

        "area_km2": (
            float(area_km2)
            if pd.notna(area_km2)
            else None
        ),

        # Not available in current RGI CSV
        "length_km": None,

        "width_km": None,

        "estimated_ice_thickness_m": None,

        # Database defaults / unknown
        "glacier_type": "UNKNOWN",

        "status": "UNKNOWN",

        "data_source": (
            str(row["data_source"])
        ),

        "source_reference": (
            "Randolph Glacier Inventory 7.0"
        ),

        "source_dataset_version": (
            str(row["source_version"])
        ),

        # RGI 7.0 is a baseline inventory,
        # not a temporal observation series.
        "first_observed_at": None,

        "last_observed_at": None,

        "observation_count": 0,
    }

    records.append(
        record
    )


print(
    f"Prepared records : "
    f"{len(records):,}"
)


# ============================================================
# INSERT INTO MYSQL
# ============================================================

print("\n" + "=" * 70)
print("7. INSERTING GLACIERS INTO MYSQL")
print("=" * 70)

insert_sql = text(
    """
    INSERT INTO glaciers (

        glacier_id,
        glacier_code,
        glacier_name,
        country,
        state_province,
        region,
        mountain_range,

        latitude,
        longitude,

        elevation_min_m,
        elevation_max_m,
        mean_elevation_m,

        area_km2,

        length_km,
        width_km,
        estimated_ice_thickness_m,

        glacier_type,
        status,

        data_source,
        source_reference,
        source_dataset_version,

        first_observed_at,
        last_observed_at,

        observation_count

    )

    VALUES (

        :glacier_id,
        :glacier_code,
        :glacier_name,
        :country,
        :state_province,
        :region,
        :mountain_range,

        :latitude,
        :longitude,

        :elevation_min_m,
        :elevation_max_m,
        :mean_elevation_m,

        :area_km2,

        :length_km,
        :width_km,
        :estimated_ice_thickness_m,

        :glacier_type,
        :status,

        :data_source,
        :source_reference,
        :source_dataset_version,

        :first_observed_at,
        :last_observed_at,

        :observation_count

    )
    """
)


with engine.begin() as connection:

    connection.execute(
        insert_sql,
        records
    )


print(
    f"\nInserted records : "
    f"{len(records):,}"
)


# ============================================================
# FINAL DATABASE VERIFICATION
# ============================================================

print("\n" + "=" * 70)
print("8. VERIFYING MYSQL")
print("=" * 70)

with engine.connect() as connection:

    total_result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM glaciers
            """
        )
    )

    total_count = (
        total_result.scalar()
        or 0
    )

    rgi_result = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM glaciers
            WHERE data_source
            LIKE '%Randolph Glacier Inventory%'
            """
        )
    )

    rgi_count = (
        rgi_result.scalar()
        or 0
    )


print(
    f"Total glaciers in MySQL : "
    f"{total_count:,}"
)

print(
    f"RGI glaciers in MySQL   : "
    f"{rgi_count:,}"
)


# ============================================================
# SAMPLE RECORDS
# ============================================================

print("\n" + "=" * 70)
print("9. SAMPLE DATABASE RECORDS")
print("=" * 70)

with engine.connect() as connection:

    sample = pd.read_sql(
        text(
            """
            SELECT
                glacier_id,
                glacier_code,
                glacier_name,
                country,
                latitude,
                longitude,
                area_km2,
                elevation_min_m,
                elevation_max_m
            FROM glaciers
            ORDER BY glacier_id DESC
            LIMIT 5
            """
        ),
        connection,
    )


print(
    sample.to_string(
        index=False
    )
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("GLYAB STEP 3 COMPLETE")
print("=" * 70)

print(
    "\nReal RGI 7.0 glacier records "
    "have been loaded into MySQL."
)

print(
    f"\nNew records inserted : "
    f"{len(records):,}"
)

print(
    f"Total MySQL glaciers : "
    f"{total_count:,}"
)

print(
    "\nNo synthetic glacier measurements "
    "were created."
)

print(
    "\nNEXT:"
)

print(
    "STEP 4 - Temporal remote sensing, "
    "weather and glacial-lake data"
)
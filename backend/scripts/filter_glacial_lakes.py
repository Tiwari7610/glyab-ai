from pathlib import Path

import pandas as pd
from dbfread import DBF


BASE_DIR = Path(__file__).resolve().parents[1]

DBF_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "glacial_lakes"
    / "HMA_GLI"
    / "HMA_GLI_glacial_lakes_LatLonWGS84_2010_14.dbf"
)

GLACIER_MASTER_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "glacier_master.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "glacial_lakes"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "hma_gli_india_himalaya_2010_14.csv"
)


def parse_coordinate(value):
    """
    Convert HMA_GLI coordinate strings such as:

        N28.07
        E97.32

    into numeric values:

        28.07
        97.32
    """

    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text:
        return None

    direction = text[0].upper()

    try:
        number = float(text[1:])
    except ValueError:
        return None

    if direction in ("S", "W"):
        number = -number

    return number


print("=" * 70)
print("GLYAB — FINAL HMA_GLI LAKE DATA PROCESSING")
print("=" * 70)


# ---------------------------------------------------------
# 1. LOAD GLACIER MASTER
# ---------------------------------------------------------

print("\n[1/6] Loading real RGI glacier master...")

glaciers = pd.read_csv(GLACIER_MASTER_PATH)

glaciers = glaciers.dropna(
    subset=["latitude", "longitude"]
)

print("Glacier records:", len(glaciers))


# ---------------------------------------------------------
# 2. LOAD HMA_GLI DBF
# ---------------------------------------------------------

print("\n[2/6] Loading HMA_GLI 2010–2014 DBF...")

records = list(DBF(DBF_PATH))

lakes = pd.DataFrame(records)

print("HMA_GLI total records:", len(lakes))


# ---------------------------------------------------------
# 3. INDIA FILTER
# ---------------------------------------------------------

print("\n[3/6] Filtering India records...")

lakes["Country"] = (
    lakes["Country"]
    .astype(str)
    .str.strip()
)

india = lakes[
    lakes["Country"].str.lower() == "india"
].copy()

print("India records:", len(india))


# ---------------------------------------------------------
# 4. PARSE COORDINATES
# ---------------------------------------------------------

print("\n[4/6] Parsing HMA_GLI coordinates...")

india["latitude"] = india["Lat"].apply(
    parse_coordinate
)

india["longitude"] = india["Lon"].apply(
    parse_coordinate
)

india["area_m2"] = pd.to_numeric(
    india["Area_m2"],
    errors="coerce"
)

india["area_km2"] = (
    india["area_m2"] / 1_000_000
)

india = india.dropna(
    subset=[
        "latitude",
        "longitude",
        "area_m2",
    ]
)

print(
    "Valid coordinate records:",
    len(india)
)


# ---------------------------------------------------------
# 5. GLYAB AOI SCREENING
# ---------------------------------------------------------

print("\n[5/6] Applying GLYAB glacier-master AOI + 0.5° buffer...")

buffer = 0.5

min_lat = glaciers["latitude"].min() - buffer
max_lat = glaciers["latitude"].max() + buffer

min_lon = glaciers["longitude"].min() - buffer
max_lon = glaciers["longitude"].max() + buffer


filtered = india[
    (india["latitude"] >= min_lat)
    & (india["latitude"] <= max_lat)
    & (india["longitude"] >= min_lon)
    & (india["longitude"] <= max_lon)
].copy()


# ---------------------------------------------------------
# PROJECT METADATA
# ---------------------------------------------------------

filtered["data_source"] = "NASA NSIDC HMA_GLI"

filtered["dataset_version"] = "V001"

filtered["temporal_period"] = "2010-2014"

filtered["spatial_filter"] = (
    "GLYAB glacier-master bounding box + 0.5 degree buffer"
)

filtered["geometry_available"] = False


# ---------------------------------------------------------
# SELECT CLEAN OUTPUT FIELDS
# ---------------------------------------------------------

output_columns = [
    "Geo_ID",
    "FULL_NAME",
    "Country",
    "ISO",
    "RGI_CODE",
    "WGS_CODE",
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
]


available_columns = [
    column
    for column in output_columns
    if column in filtered.columns
]


final_df = filtered[
    available_columns
].copy()


# ---------------------------------------------------------
# 6. SAVE FINAL DATASET
# ---------------------------------------------------------

print("\n[6/6] Saving processed lake dataset...")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

final_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ---------------------------------------------------------
# FINAL REPORT
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 4 — GLACIAL LAKE DATA COMPLETE")
print("=" * 70)

print("HMA_GLI total records :", len(lakes))
print("India records         :", len(india))
print("GLYAB lake records    :", len(final_df))

if len(final_df) > 0:

    print(
        "Total lake area km²   :",
        round(
            final_df["area_km2"].sum(),
            4
        )
    )

    print(
        "Latitude range        :",
        round(final_df["latitude"].min(), 4),
        "to",
        round(final_df["latitude"].max(), 4)
    )

    print(
        "Longitude range       :",
        round(final_df["longitude"].min(), 4),
        "to",
        round(final_df["longitude"].max(), 4)
    )

print("\nOUTPUT:")
print(OUTPUT_PATH)

print("\nSCIENTIFIC LIMITATION:")
print(
    "HMA_GLI shapefile geometry is unavailable."
)

print(
    "This dataset therefore contains verified "
    "lake attributes and coordinates, not lake polygons."
)

print("=" * 70)
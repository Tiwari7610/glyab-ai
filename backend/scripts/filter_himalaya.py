from pathlib import Path
import json

import geopandas as gpd
import pandas as pd


# ============================================================
# GLYAB - STEP 2
# HIMALAYAN / INDIAN GLACIER SPATIAL FILTER
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RGI_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "rgi_v7_clean.gpkg"
)

BOUNDARY_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "boundaries"
    / "ne_10m_admin_1_states_provinces.shp"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MASTER_CSV = OUTPUT_DIR / "glacier_master.csv"
MASTER_GPKG = OUTPUT_DIR / "glacier_master.gpkg"
QUALITY_REPORT = OUTPUT_DIR / "glacier_master_quality_report.json"
AOI_GPKG = OUTPUT_DIR / "glyab_himalayan_aoi.gpkg"


# ============================================================
# TARGET INDIAN HIMALAYAN STATES
# ============================================================

TARGET_STATE_KEYWORDS = [
    "Jammu",
    "Kashmir",
    "Ladakh",
    "Himachal",
    "Uttarakhand",
    "Sikkim",
    "Arunachal",
]


# ============================================================
# HELPER
# ============================================================

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def find_column(gdf, candidates):
    """
    Find a column ignoring case.
    """

    column_map = {
        str(col).strip().lower(): col
        for col in gdf.columns
    }

    for candidate in candidates:
        key = candidate.strip().lower()

        if key in column_map:
            return column_map[key]

    return None


# ============================================================
# START
# ============================================================

print_section(
    "GLYAB STEP 2 - HIMALAYAN SPATIAL FILTER"
)

print("RGI input:")
print(RGI_FILE)

print("\nBoundary input:")
print(BOUNDARY_FILE)


# ============================================================
# FILE CHECK
# ============================================================

if not RGI_FILE.exists():
    raise FileNotFoundError(
        f"\nRGI dataset not found:\n{RGI_FILE}"
    )

if not BOUNDARY_FILE.exists():
    raise FileNotFoundError(
        f"\nBoundary dataset not found:\n{BOUNDARY_FILE}"
    )


# ============================================================
# LOAD RGI
# ============================================================

print_section(
    "1. LOADING RGI 7.0"
)

rgi = gpd.read_file(
    RGI_FILE
)

print(
    f"RGI records loaded : {len(rgi):,}"
)

print(
    f"RGI CRS            : {rgi.crs}"
)


# ============================================================
# LOAD NATURAL EARTH
# ============================================================

print_section(
    "2. LOADING NATURAL EARTH ADMIN-1"
)

admin1 = gpd.read_file(
    BOUNDARY_FILE
)

print(
    f"Boundary records loaded : {len(admin1):,}"
)

print(
    f"Boundary CRS            : {admin1.crs}"
)

print("\nDetected boundary columns:")

for column in admin1.columns:
    print(
        f"  - {column}"
    )


# ============================================================
# DETECT COUNTRY COLUMN
# ============================================================

print_section(
    "3. IDENTIFYING INDIA"
)

country_column = find_column(
    admin1,
    [
        "admin",
        "ADMIN",
        "adm0_name",
        "sovereignt",
        "geonunit",
        "admin0",
    ],
)

state_column = find_column(
    admin1,
    [
        "name_en",
        "NAME_1",
        "name",
        "name_local",
    ],
)

country_code_column = find_column(
    admin1,
    [
        "adm0_a3",
        "ADM0_A3",
        "iso_a3",
        "ISO_A3",
    ],
)


print(
    f"Country column detected : {country_column}"
)

print(
    f"State column detected   : {state_column}"
)

print(
    f"Country code column     : {country_code_column}"
)


if state_column is None:
    raise KeyError(
        "Could not find the state/province name column."
    )


# ============================================================
# FIND INDIA
# ============================================================

india = None

# ------------------------------------------------------------
# METHOD 1 - COUNTRY CODE
# ------------------------------------------------------------

if country_code_column is not None:

    country_codes = (
        admin1[country_code_column]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    india = admin1[
        country_codes == "IND"
    ].copy()


# ------------------------------------------------------------
# METHOD 2 - COUNTRY NAME
# ------------------------------------------------------------

if india is None or india.empty:

    if country_column is not None:

        country_names = (
            admin1[country_column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        india = admin1[
            country_names.isin(
                [
                    "india",
                    "republic of india",
                ]
            )
        ].copy()


if india is None or india.empty:

    raise RuntimeError(
        "\nIndia could not be identified in "
        "the Natural Earth dataset."
    )


print(
    f"\nIndian Admin-1 records : {len(india):,}"
)


# ============================================================
# SHOW INDIAN STATES
# ============================================================

print(
    "\nIndian administrative units detected:"
)

india_states = sorted(
    india[state_column]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
)

for state in india_states:
    print(
        f"  - {state}"
    )


# ============================================================
# SELECT HIMALAYAN STATES
# ============================================================

print_section(
    "4. SELECTING GLYAB HIMALAYAN AOI"
)

selected_states = []

for state in india_states:

    state_lower = state.lower()

    if any(
        keyword.lower() in state_lower
        for keyword in TARGET_STATE_KEYWORDS
    ):

        selected_states.append(
            state
        )


selected_states = sorted(
    set(selected_states)
)


print(
    "\nSelected Himalayan states:"
)

for state in selected_states:

    print(
        f"  ✓ {state}"
    )


if not selected_states:

    raise RuntimeError(
        "\nNo Himalayan states were detected."
    )


print(
    f"\nTotal selected states : "
    f"{len(selected_states)}"
)


# ============================================================
# CREATE AOI
# ============================================================

aoi = india[
    india[state_column]
    .astype(str)
    .str.strip()
    .isin(selected_states)
].copy()


if aoi.empty:

    raise RuntimeError(
        "Selected Himalayan AOI is empty."
    )


# ============================================================
# CRS
# ============================================================

print_section(
    "5. STANDARDIZING CRS"
)

if rgi.crs is None:

    raise RuntimeError(
        "RGI CRS is missing."
    )

if aoi.crs is None:

    raise RuntimeError(
        "Boundary CRS is missing."
    )


aoi = aoi.to_crs(
    rgi.crs
)

print(
    f"Working CRS : {rgi.crs}"
)


# ============================================================
# UNION AOI
# ============================================================

print_section(
    "6. CREATING HIMALAYAN AOI GEOMETRY"
)

aoi_geometry = aoi.geometry.union_all()


if aoi_geometry.is_empty:

    raise RuntimeError(
        "AOI geometry is empty."
    )


print(
    "AOI geometry created successfully."
)


# ============================================================
# SAVE AOI
# ============================================================

aoi_output = aoi[
    [
        state_column,
        "geometry",
    ]
].copy()


aoi_output.to_file(
    AOI_GPKG,
    layer="glyab_himalayan_aoi",
    driver="GPKG",
)


print(
    "\nAOI saved:"
)

print(
    AOI_GPKG
)


# ============================================================
# SPATIAL FILTER
# ============================================================

print_section(
    "7. FILTERING RGI GLACIERS"
)

print(
    "Checking glacier polygons against "
    "Himalayan AOI..."
)


intersects_mask = (
    rgi.geometry.intersects(
        aoi_geometry
    )
)


glacier_master = (
    rgi.loc[
        intersects_mask
    ]
    .copy()
)


print(
    f"\nOriginal RGI glaciers : "
    f"{len(rgi):,}"
)

print(
    f"GLYAB AOI glaciers    : "
    f"{len(glacier_master):,}"
)

print(
    f"Excluded glaciers     : "
    f"{len(rgi) - len(glacier_master):,}"
)


if glacier_master.empty:

    raise RuntimeError(
        "\nNo RGI glaciers intersect "
        "the selected Himalayan AOI."
    )


# ============================================================
# QUALITY CHECK
# ============================================================

print_section(
    "8. MASTER DATA QUALITY"
)

duplicate_count = (
    glacier_master["rgi_id"]
    .duplicated()
    .sum()
)

null_geometry_count = (
    glacier_master.geometry
    .isna()
    .sum()
)

empty_geometry_count = (
    glacier_master.geometry
    .is_empty
    .sum()
)

invalid_geometry_count = (
    ~glacier_master.geometry
    .is_valid
).sum()


missing_coordinate_count = (
    glacier_master[
        ["cenlat", "cenlon"]
    ]
    .isna()
    .any(axis=1)
    .sum()
)


area_numeric = pd.to_numeric(
    glacier_master["area_km2"],
    errors="coerce"
)

invalid_area_count = (
    area_numeric.isna()
    .sum()
    +
    area_numeric.le(0).sum()
)


print(
    f"Duplicate RGI IDs   : "
    f"{duplicate_count:,}"
)

print(
    f"Null geometries     : "
    f"{null_geometry_count:,}"
)

print(
    f"Empty geometries    : "
    f"{empty_geometry_count:,}"
)

print(
    f"Invalid geometries  : "
    f"{invalid_geometry_count:,}"
)

print(
    f"Missing coordinates : "
    f"{missing_coordinate_count:,}"
)

print(
    f"Invalid area values : "
    f"{invalid_area_count:,}"
)


# ============================================================
# CANONICAL GLYAB FIELDS
# ============================================================

print_section(
    "9. CREATING GLYAB MASTER FIELDS"
)

glacier_master["glacier_name"] = (
    glacier_master["glac_name"]
    .astype("string")
    .str.strip()
)

glacier_master["latitude"] = pd.to_numeric(
    glacier_master["cenlat"],
    errors="coerce"
)

glacier_master["longitude"] = pd.to_numeric(
    glacier_master["cenlon"],
    errors="coerce"
)

glacier_master["min_elevation_m"] = pd.to_numeric(
    glacier_master["zmin_m"],
    errors="coerce"
)

glacier_master["max_elevation_m"] = pd.to_numeric(
    glacier_master["zmax_m"],
    errors="coerce"
)

glacier_master["median_elevation_m"] = pd.to_numeric(
    glacier_master["zmed_m"],
    errors="coerce"
)


# ============================================================
# PROVENANCE
# ============================================================

glacier_master["data_source"] = (
    "Randolph Glacier Inventory 7.0"
)

glacier_master["source_version"] = (
    "RGI 7.0"
)

glacier_master["spatial_filter"] = (
    "GLYAB Indian Himalayan AOI"
)

glacier_master["aoi_definition"] = (
    "; ".join(selected_states)
)

glacier_master["data_quality"] = (
    "GOOD"
)


# ============================================================
# SAVE MASTER GEOPACKAGE
# ============================================================

print_section(
    "10. SAVING MASTER GEOPACKAGE"
)

glacier_master.to_file(
    MASTER_GPKG,
    layer="glacier_master",
    driver="GPKG",
)


print(
    f"Saved:\n{MASTER_GPKG}"
)


# ============================================================
# SAVE MASTER CSV
# ============================================================

print_section(
    "11. SAVING MASTER CSV"
)

csv_columns = [
    "rgi_id",
    "glacier_name",
    "o1region",
    "o2region",
    "latitude",
    "longitude",
    "area_km2",
    "min_elevation_m",
    "max_elevation_m",
    "median_elevation_m",
    "slope_deg",
    "aspect_deg",
    "data_source",
    "source_version",
    "spatial_filter",
    "aoi_definition",
    "data_quality",
]


available_columns = [
    col
    for col in csv_columns
    if col in glacier_master.columns
]


master_csv_df = glacier_master[
    available_columns
].copy()


master_csv_df.to_csv(
    MASTER_CSV,
    index=False,
)


print(
    f"Saved:\n{MASTER_CSV}"
)


# ============================================================
# QUALITY REPORT
# ============================================================

print_section(
    "12. CREATING QUALITY REPORT"
)

quality_report = {

    "project": "GLYAB",

    "dataset": (
        "GLYAB Himalayan Glacier Master Dataset"
    ),

    "source": {
        "name": "Randolph Glacier Inventory",
        "version": "7.0",
    },

    "boundary_source": {
        "name": (
            "Natural Earth Admin-1 "
            "States and Provinces"
        ),
        "version": "5.1.1",
    },

    "aoi": {
        "type": (
            "Indian Himalayan "
            "administrative AOI"
        ),
        "states": selected_states,
    },

    "records": {
        "rgi_input": int(len(rgi)),
        "aoi_selected": int(
            len(glacier_master)
        ),
        "excluded": int(
            len(rgi)
            - len(glacier_master)
        ),
    },

    "quality": {
        "duplicate_rgi_ids": int(
            duplicate_count
        ),
        "null_geometries": int(
            null_geometry_count
        ),
        "empty_geometries": int(
            empty_geometry_count
        ),
        "invalid_geometries": int(
            invalid_geometry_count
        ),
        "missing_coordinates": int(
            missing_coordinate_count
        ),
        "invalid_area_values": int(
            invalid_area_count
        ),
    },

    "outputs": {
        "csv": str(MASTER_CSV),
        "geopackage": str(MASTER_GPKG),
        "aoi": str(AOI_GPKG),
    },
}


with open(
    QUALITY_REPORT,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        quality_report,
        file,
        indent=4,
    )


print(
    f"Saved:\n{QUALITY_REPORT}"
)


# ============================================================
# COMPLETE
# ============================================================

print_section(
    "GLYAB STEP 2 COMPLETE"
)

print(
    "Himalayan spatial filtering "
    "completed successfully."
)

print(
    f"\nRGI input glaciers : "
    f"{len(rgi):,}"
)

print(
    f"GLYAB AOI glaciers : "
    f"{len(glacier_master):,}"
)

print(
    f"Excluded glaciers  : "
    f"{len(rgi) - len(glacier_master):,}"
)

print(
    "\nGenerated files:"
)

print(
    f"  ✓ {MASTER_CSV}"
)

print(
    f"  ✓ {MASTER_GPKG}"
)

print(
    f"  ✓ {AOI_GPKG}"
)

print(
    f"  ✓ {QUALITY_REPORT}"
)

print(
    "\nSTEP 2 FINISHED."
)
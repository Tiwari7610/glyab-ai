from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# GLYAB - RGI 7.0 REGIONAL ANALYSIS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "rgi_v7_clean.gpkg"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER
# ============================================================

def print_section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print_section("GLYAB RGI 7.0 REGIONAL ANALYSIS")

print(f"Input file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"RGI GeoPackage not found:\n{INPUT_FILE}"
    )

print("\nLoading RGI dataset...")

gdf = gpd.read_file(INPUT_FILE)

print(f"Total records loaded : {len(gdf):,}")
print(f"Total columns        : {len(gdf.columns)}")
print(f"CRS                  : {gdf.crs}")


# ============================================================
# COLUMN CHECK
# ============================================================

print_section("AVAILABLE RGI COLUMNS")

print(", ".join(gdf.columns.tolist()))


required_columns = [
    "rgi_id",
    "o1region",
    "o2region",
    "cenlat",
    "cenlon",
    "area_km2",
    "glac_name",
    "zmin_m",
    "zmax_m",
    "zmed_m",
]

missing_columns = [
    col for col in required_columns
    if col not in gdf.columns
]

if missing_columns:
    print("\nWARNING: Missing columns:")
    for col in missing_columns:
        print(f"  - {col}")

    raise KeyError(
        "Required RGI columns are missing from the GeoPackage."
    )

print("\nAll required RGI columns are available.")


# ============================================================
# BASIC DATA QUALITY
# ============================================================

print_section("DATA QUALITY")

print(f"Duplicate RGI IDs : {gdf['rgi_id'].duplicated().sum():,}")

print(
    f"Null geometries   : "
    f"{gdf.geometry.isna().sum():,}"
)

print(
    f"Empty geometries  : "
    f"{gdf.geometry.is_empty.sum():,}"
)

print(
    f"Invalid geometries: "
    f"{(~gdf.geometry.is_valid).sum():,}"
)


# ============================================================
# RGI REGIONS
# ============================================================

print_section("RGI REGIONS")

region_counts = (
    gdf["o1region"]
    .value_counts()
    .sort_index()
)

for region, count in region_counts.items():
    print(
        f"Region {region}: "
        f"{count:,} glaciers"
    )


# ============================================================
# RGI SUBREGIONS
# ============================================================

print_section("RGI SUBREGIONS")

subregion_counts = (
    gdf["o2region"]
    .value_counts()
    .sort_index()
)

for subregion, count in subregion_counts.items():
    print(
        f"{subregion}: "
        f"{count:,} glaciers"
    )


# ============================================================
# GEOGRAPHIC EXTENT
# ============================================================

print_section("GEOGRAPHIC EXTENT")

longitude = pd.to_numeric(
    gdf["cenlon"],
    errors="coerce"
)

latitude = pd.to_numeric(
    gdf["cenlat"],
    errors="coerce"
)

print(
    f"Longitude min : {longitude.min():.6f}"
)

print(
    f"Longitude max : {longitude.max():.6f}"
)

print(
    f"Latitude min  : {latitude.min():.6f}"
)

print(
    f"Latitude max  : {latitude.max():.6f}"
)

print(
    f"Valid longitude values : "
    f"{longitude.notna().sum():,}"
)

print(
    f"Valid latitude values  : "
    f"{latitude.notna().sum():,}"
)


# ============================================================
# AREA STATISTICS
# ============================================================

print_section("GLACIER AREA STATISTICS")

area = pd.to_numeric(
    gdf["area_km2"],
    errors="coerce"
)

print(
    f"Total glacier area : "
    f"{area.sum():,.4f} km²"
)

print(
    f"Mean glacier area  : "
    f"{area.mean():,.4f} km²"
)

print(
    f"Median glacier area: "
    f"{area.median():,.4f} km²"
)

print(
    f"Minimum area       : "
    f"{area.min():,.6f} km²"
)

print(
    f"Maximum area       : "
    f"{area.max():,.6f} km²"
)


# ============================================================
# ELEVATION STATISTICS
# ============================================================

print_section("ELEVATION STATISTICS")

zmin = pd.to_numeric(
    gdf["zmin_m"],
    errors="coerce"
)

zmax = pd.to_numeric(
    gdf["zmax_m"],
    errors="coerce"
)

zmed = pd.to_numeric(
    gdf["zmed_m"],
    errors="coerce"
)

print(
    f"Minimum elevation "
    f"(mean)   : {zmin.mean():,.2f} m"
)

print(
    f"Maximum elevation "
    f"(mean)   : {zmax.mean():,.2f} m"
)

print(
    f"Median elevation "
    f"(mean)   : {zmed.mean():,.2f} m"
)

print(
    f"Lowest glacier elevation : "
    f"{zmin.min():,.2f} m"
)

print(
    f"Highest glacier elevation: "
    f"{zmax.max():,.2f} m"
)


# ============================================================
# GLACIER NAME COVERAGE
# ============================================================

print_section("GLACIER NAME COVERAGE")

glacier_names = (
    gdf["glac_name"]
    .astype("string")
    .str.strip()
)

named_mask = (
    glacier_names.notna()
    & (glacier_names != "")
    & (glacier_names.str.lower() != "nan")
)

named_count = named_mask.sum()
unnamed_count = len(gdf) - named_count

named_percentage = (
    named_count / len(gdf) * 100
)

unnamed_percentage = (
    unnamed_count / len(gdf) * 100
)

print(
    f"Named glaciers   : "
    f"{named_count:,} "
    f"({named_percentage:.2f}%)"
)

print(
    f"Unnamed glaciers : "
    f"{unnamed_count:,} "
    f"({unnamed_percentage:.2f}%)"
)


# ============================================================
# REGION SUMMARY TABLE
# ============================================================

print_section("REGIONAL SUMMARY")

region_summary = (
    gdf.groupby("o1region")
    .agg(
        glacier_count=("rgi_id", "count"),
        total_area_km2=("area_km2", "sum"),
        mean_area_km2=("area_km2", "mean"),
        mean_zmin_m=("zmin_m", "mean"),
        mean_zmax_m=("zmax_m", "mean"),
        mean_zmed_m=("zmed_m", "mean"),
    )
    .reset_index()
)

print(
    region_summary.to_string(
        index=False
    )
)


# ============================================================
# SUBREGION SUMMARY TABLE
# ============================================================

print_section("SUBREGIONAL SUMMARY")

subregion_summary = (
    gdf.groupby("o2region")
    .agg(
        glacier_count=("rgi_id", "count"),
        total_area_km2=("area_km2", "sum"),
        mean_area_km2=("area_km2", "mean"),
        mean_zmin_m=("zmin_m", "mean"),
        mean_zmax_m=("zmax_m", "mean"),
        mean_zmed_m=("zmed_m", "mean"),
    )
    .reset_index()
)

print(
    subregion_summary.to_string(
        index=False
    )
)


# ============================================================
# SAVE REGION SUMMARY
# ============================================================

region_summary_file = (
    OUTPUT_DIR
    / "rgi_region_summary.csv"
)

region_summary.to_csv(
    region_summary_file,
    index=False
)

print(
    f"\nRegional summary saved to:"
    f"\n{region_summary_file}"
)


# ============================================================
# SAVE SUBREGION SUMMARY
# ============================================================

subregion_summary_file = (
    OUTPUT_DIR
    / "rgi_subregion_summary.csv"
)

subregion_summary.to_csv(
    subregion_summary_file,
    index=False
)

print(
    f"Subregional summary saved to:"
    f"\n{subregion_summary_file}"
)


# ============================================================
# SAMPLE RECORDS
# ============================================================

print_section("SAMPLE RGI RECORDS")

sample_columns = [
    "rgi_id",
    "glac_name",
    "o1region",
    "o2region",
    "cenlat",
    "cenlon",
    "area_km2",
    "zmin_m",
    "zmax_m",
    "zmed_m",
]

sample = (
    gdf[sample_columns]
    .head(10)
)

print(
    sample.to_string(
        index=False
    )
)


# ============================================================
# LARGEST GLACIERS
# ============================================================

print_section("TOP 10 LARGEST GLACIERS")

largest = (
    gdf[
        [
            "rgi_id",
            "glac_name",
            "o1region",
            "o2region",
            "cenlat",
            "cenlon",
            "area_km2",
            "zmin_m",
            "zmax_m",
            "zmed_m",
        ]
    ]
    .sort_values(
        "area_km2",
        ascending=False
    )
    .head(10)
)

print(
    largest.to_string(
        index=False
    )
)


# ============================================================
# HIGHEST MEDIAN ELEVATION GLACIERS
# ============================================================

print_section(
    "TOP 10 GLACIERS BY MEDIAN ELEVATION"
)

highest = (
    gdf[
        [
            "rgi_id",
            "glac_name",
            "o1region",
            "o2region",
            "cenlat",
            "cenlon",
            "area_km2",
            "zmed_m",
        ]
    ]
    .sort_values(
        "zmed_m",
        ascending=False
    )
    .head(10)
)

print(
    highest.to_string(
        index=False
    )
)


# ============================================================
# SOUTH ASIA WEST / EAST SUMMARY
# ============================================================

print_section(
    "SOUTH ASIA CRYOSPHERE SUMMARY"
)

south_asia_regions = gdf[
    gdf["o1region"].isin(
        ["14", "15", 14, 15]
    )
].copy()

print(
    f"Total South Asia RGI records : "
    f"{len(south_asia_regions):,}"
)

print(
    f"Total South Asia glacier area : "
    f"{south_asia_regions['area_km2'].sum():,.4f} km²"
)

print(
    f"Mean glacier area : "
    f"{south_asia_regions['area_km2'].mean():,.4f} km²"
)


# ============================================================
# EXPORT ANALYSIS DATASET
# ============================================================

analysis_csv = (
    OUTPUT_DIR
    / "rgi_v7_analysis_records.csv"
)

export_columns = [
    "rgi_id",
    "glac_name",
    "o1region",
    "o2region",
    "cenlat",
    "cenlon",
    "area_km2",
    "zmin_m",
    "zmax_m",
    "zmed_m",
    "slope_deg",
    "aspect_deg",
    "geometry",
]

available_export_columns = [
    col
    for col in export_columns
    if col in gdf.columns
]

analysis_df = gdf[
    available_export_columns
].copy()

# Geometry WKT for CSV compatibility
if "geometry" in analysis_df.columns:
    analysis_df["geometry_wkt"] = (
        analysis_df["geometry"]
        .apply(
            lambda geom:
            geom.wkt
            if geom is not None
            else None
        )
    )

    analysis_df = analysis_df.drop(
        columns=["geometry"]
    )

analysis_df.to_csv(
    analysis_csv,
    index=False
)

print(
    f"\nAnalysis records saved to:"
    f"\n{analysis_csv}"
)


# ============================================================
# COMPLETE
# ============================================================

print_section(
    "RGI REGIONAL ANALYSIS COMPLETE"
)

print("GLYAB RGI 7.0 analysis completed successfully.")

print(
    "\nNext stage:"
    "\n1. Define Himalayan/India Area of Interest"
    "\n2. Spatially filter RGI glaciers"
    "\n3. Build GLYAB glacier master dataset"
    "\n4. Load verified records into MySQL"
    "\n5. Add temporal remote-sensing/weather/lake data"
    "\n6. Build AI feature engineering pipeline"
)
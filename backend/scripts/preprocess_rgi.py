from __future__ import annotations

import json
import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# GLYAB AI
# RGI 7.0 PRODUCTION PREPROCESSING PIPELINE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_RGI_DIR = PROJECT_ROOT / "data" / "raw" / "rgi_v7"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_GPKG = PROCESSED_DIR / "rgi_v7_clean.gpkg"

OUTPUT_CSV = PROCESSED_DIR / "rgi_v7_clean.csv"

QUALITY_REPORT = PROCESSED_DIR / "rgi_v7_quality_report.json"


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("glyab.rgi")


# ============================================================
# RGI 7.0 EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = {
    "rgi_id",
    "o1region",
    "o2region",
    "glims_id",
    "anlys_id",
    "subm_id",
    "src_date",
    "cenlon",
    "cenlat",
    "utm_zone",
    "area_km2",
    "primeclass",
    "conn_lvl",
    "surge_type",
    "term_type",
    "glac_name",
    "is_rgi6",
    "termlon",
    "termlat",
    "zmin_m",
    "zmax_m",
    "zmed_m",
    "zmean_m",
    "slope_deg",
    "aspect_deg",
    "aspect_sec",
    "dem_source",
    "lmax_m",
}


# ============================================================
# RGI → GLYAB CANONICAL COLUMN MAPPING
# ============================================================

GLYAB_COLUMN_MAP = {
    "rgi_id": "glacier_code",
    "glac_name": "glacier_name",
    "cenlat": "latitude",
    "cenlon": "longitude",
    "zmin_m": "elevation_min_m",
    "zmax_m": "elevation_max_m",
    "zmed_m": "mean_elevation_m",
    "area_km2": "area_km2",
    "lmax_m": "length_max_m",
    "slope_deg": "slope_degree",
    "aspect_deg": "aspect_degree",
    "o1region": "rgi_region",
    "o2region": "rgi_subregion",
    "src_date": "source_date",
    "dem_source": "dem_source",
}


# ============================================================
# DISCOVER RGI SHAPEFILES
# ============================================================

def discover_rgi_files() -> list[Path]:
    """
    Discover all RGI shapefiles in the raw RGI directory.
    """

    if not RAW_RGI_DIR.exists():
        raise FileNotFoundError(
            f"RGI directory does not exist:\n"
            f"{RAW_RGI_DIR}"
        )

    files = sorted(
        RAW_RGI_DIR.glob("*.shp")
    )

    if not files:
        raise FileNotFoundError(
            "No RGI .shp files found in:\n"
            f"{RAW_RGI_DIR}"
        )

    return files


# ============================================================
# SCHEMA VALIDATION
# ============================================================

def validate_schema(
    gdf: gpd.GeoDataFrame,
    source_file: Path,
) -> None:
    """
    Validate required RGI 7.0 attributes.
    """

    actual_columns = set(gdf.columns)

    missing_columns = (
        EXPECTED_COLUMNS - actual_columns
    )

    if missing_columns:
        raise ValueError(
            f"\nMissing required columns in "
            f"{source_file.name}:\n"
            f"{sorted(missing_columns)}"
        )


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text_columns(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Normalize text attributes without inventing values.
    """

    text_columns = [
        "rgi_id",
        "o1region",
        "o2region",
        "glims_id",
        "src_date",
        "glac_name",
        "dem_source",
    ]

    for column in text_columns:

        if column not in gdf.columns:
            continue

        gdf[column] = (
            gdf[column]
            .astype("string")
            .str.strip()
        )

        gdf[column] = gdf[column].replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA,
                "none": pd.NA,
            }
        )

    return gdf


# ============================================================
# NUMERIC NORMALIZATION
# ============================================================

def normalize_numeric_columns(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Convert numeric RGI fields to numeric dtype.
    """

    numeric_columns = [
        "anlys_id",
        "subm_id",
        "cenlon",
        "cenlat",
        "utm_zone",
        "area_km2",
        "primeclass",
        "conn_lvl",
        "surge_type",
        "term_type",
        "is_rgi6",
        "termlon",
        "termlat",
        "zmin_m",
        "zmax_m",
        "zmed_m",
        "zmean_m",
        "slope_deg",
        "aspect_deg",
        "aspect_sec",
        "lmax_m",
    ]

    for column in numeric_columns:

        if column in gdf.columns:

            gdf[column] = pd.to_numeric(
                gdf[column],
                errors="coerce",
            )

    return gdf


# ============================================================
# GEOMETRY VALIDATION
# ============================================================

def validate_geometry(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Check geometry validity.
    """

    gdf["geometry_valid"] = (
        gdf.geometry.notna()
        & ~gdf.geometry.is_empty
        & gdf.geometry.is_valid
    )

    return gdf


# ============================================================
# COORDINATE VALIDATION
# ============================================================

def validate_coordinates(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Validate RGI centroid latitude/longitude.
    """

    gdf["latitude_valid"] = (
        gdf["cenlat"].notna()
        & gdf["cenlat"].between(
            -90,
            90,
        )
    )

    gdf["longitude_valid"] = (
        gdf["cenlon"].notna()
        & gdf["cenlon"].between(
            -180,
            180,
        )
    )

    gdf["coordinate_valid"] = (
        gdf["latitude_valid"]
        & gdf["longitude_valid"]
    )

    return gdf


# ============================================================
# ATTRIBUTE QUALITY FLAGS
# ============================================================

def add_quality_flags(
    gdf: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Generate explicit data-quality indicators.
    """

    gdf["rgi_id_valid"] = (
        gdf["rgi_id"].notna()
        & gdf["rgi_id"].ne("")
    )

    gdf["area_valid"] = (
        gdf["area_km2"].notna()
        & (gdf["area_km2"] > 0)
    )

    gdf["elevation_valid"] = (
        gdf["zmin_m"].notna()
        & gdf["zmax_m"].notna()
        & (gdf["zmin_m"] >= 0)
        & (gdf["zmax_m"] >= gdf["zmin_m"])
    )

    gdf["quality_flag"] = "GOOD"

    invalid_mask = (
        ~gdf["geometry_valid"]
        | ~gdf["coordinate_valid"]
        | ~gdf["rgi_id_valid"]
    )

    gdf.loc[
        invalid_mask,
        "quality_flag",
    ] = "INVALID"

    warning_mask = (
        ~gdf["area_valid"]
        | ~gdf["elevation_valid"]
    )

    gdf.loc[
        warning_mask
        & (gdf["quality_flag"] == "GOOD"),
        "quality_flag",
    ] = "WARNING"

    return gdf


# ============================================================
# SOURCE METADATA
# ============================================================

def add_source_metadata(
    gdf: gpd.GeoDataFrame,
    source_file: Path,
) -> gpd.GeoDataFrame:
    """
    Add provenance information.
    """

    gdf["source_file"] = source_file.name

    gdf["source_dataset"] = "RGI 7.0"

    gdf["source_format"] = "ESRI Shapefile"

    return gdf


# ============================================================
# PROCESS ONE RGI FILE
# ============================================================

def process_file(
    source_file: Path,
) -> gpd.GeoDataFrame:

    logger.info(
        "Reading: %s",
        source_file.name,
    )

    gdf = gpd.read_file(
        source_file
    )

    logger.info(
        "Loaded %d records.",
        len(gdf),
    )

    # --------------------------------------------------------
    # Validate schema
    # --------------------------------------------------------

    validate_schema(
        gdf,
        source_file,
    )

    # --------------------------------------------------------
    # Validate CRS
    # --------------------------------------------------------

    if gdf.crs is None:
        raise ValueError(
            f"CRS is missing in "
            f"{source_file.name}"
        )

    logger.info(
        "CRS: %s",
        gdf.crs,
    )

    # --------------------------------------------------------
    # Convert to WGS84
    # --------------------------------------------------------

    if gdf.crs.to_epsg() != 4326:

        logger.info(
            "Reprojecting to EPSG:4326..."
        )

        gdf = gdf.to_crs(
            "EPSG:4326"
        )

    # --------------------------------------------------------
    # Normalize attributes
    # --------------------------------------------------------

    gdf = normalize_text_columns(
        gdf
    )

    gdf = normalize_numeric_columns(
        gdf
    )

    # --------------------------------------------------------
    # Geometry checks
    # --------------------------------------------------------

    gdf = validate_geometry(
        gdf
    )

    # --------------------------------------------------------
    # Coordinate checks
    # --------------------------------------------------------

    gdf = validate_coordinates(
        gdf
    )

    # --------------------------------------------------------
    # Quality flags
    # --------------------------------------------------------

    gdf = add_quality_flags(
        gdf
    )

    # --------------------------------------------------------
    # Source metadata
    # --------------------------------------------------------

    gdf = add_source_metadata(
        gdf,
        source_file,
    )

    return gdf


# ============================================================
# REMOVE DUPLICATE RGI IDS
# ============================================================

def remove_duplicate_rgi_ids(
    gdf: gpd.GeoDataFrame,
) -> tuple[gpd.GeoDataFrame, int]:

    duplicate_mask = (
        gdf["rgi_id"]
        .duplicated(
            keep="first"
        )
    )

    duplicate_count = int(
        duplicate_mask.sum()
    )

    if duplicate_count > 0:

        logger.warning(
            "Duplicate RGI IDs detected: %d",
            duplicate_count,
        )

    gdf = gdf.loc[
        ~duplicate_mask
    ].copy()

    logger.info(
        "Records after deduplication: %d",
        len(gdf),
    )

    return (
        gdf,
        duplicate_count,
    )


# ============================================================
# CREATE GLYAB CANONICAL TABLE
# ============================================================

def create_canonical_attributes(
    gdf: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """
    Convert RGI attributes into GLYAB-friendly columns.
    """

    canonical = pd.DataFrame(
        index=gdf.index
    )

    for (
        source_column,
        target_column,
    ) in GLYAB_COLUMN_MAP.items():

        canonical[target_column] = (
            gdf[source_column]
        )

    # --------------------------------------------------------
    # Quality columns
    # --------------------------------------------------------

    quality_columns = [
        "source_file",
        "source_dataset",
        "source_format",
        "quality_flag",
        "geometry_valid",
        "coordinate_valid",
        "rgi_id_valid",
        "area_valid",
        "elevation_valid",
    ]

    for column in quality_columns:

        canonical[column] = (
            gdf[column]
        )

    return canonical


# ============================================================
# CREATE QUALITY REPORT
# ============================================================

def create_quality_report(
    gdf: gpd.GeoDataFrame,
    files: list[Path],
    duplicate_count: int,
) -> dict:

    quality_distribution = {
        str(key): int(value)
        for key, value in (
            gdf["quality_flag"]
            .value_counts()
            .items()
        )
    }

    geometry_distribution = {
        str(key): int(value)
        for key, value in (
            gdf.geometry
            .geom_type
            .value_counts()
            .items()
        )
    }

    report = {
        "dataset": "RGI 7.0",

        "pipeline": (
            "GLYAB AI RGI 7.0 "
            "production preprocessing"
        ),

        "input_files": [
            file.name
            for file in files
        ],

        "records_after_processing": int(
            len(gdf)
        ),

        "duplicate_rgi_ids_removed": (
            duplicate_count
        ),

        "crs": (
            str(gdf.crs)
            if gdf.crs
            else None
        ),

        "geometry_types": (
            geometry_distribution
        ),

        "invalid_geometry_count": int(
            (~gdf["geometry_valid"])
            .sum()
        ),

        "invalid_coordinate_count": int(
            (~gdf["coordinate_valid"])
            .sum()
        ),

        "invalid_rgi_id_count": int(
            (~gdf["rgi_id_valid"])
            .sum()
        ),

        "invalid_area_count": int(
            (~gdf["area_valid"])
            .sum()
        ),

        "invalid_elevation_count": int(
            (~gdf["elevation_valid"])
            .sum()
        ),

        "quality_distribution": (
            quality_distribution
        ),

        "missing_glacier_name_count": int(
            gdf["glac_name"]
            .isna()
            .sum()
        ),

        "missing_glacier_name_percent": round(
            float(
                gdf["glac_name"]
                .isna()
                .mean()
                * 100
            ),
            4,
        ),
    }

    return report


# ============================================================
# SAVE PROCESSED OUTPUTS
# ============================================================

def save_outputs(
    gdf: gpd.GeoDataFrame,
) -> None:

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Save GeoPackage
    # --------------------------------------------------------

    logger.info(
        "Saving GeoPackage..."
    )

    gdf.to_file(
        OUTPUT_GPKG,
        layer="rgi_glaciers",
        driver="GPKG",
    )

    # --------------------------------------------------------
    # Save canonical CSV
    # --------------------------------------------------------

    logger.info(
        "Creating canonical CSV..."
    )

    canonical = (
        create_canonical_attributes(
            gdf
        )
    )

    canonical.to_csv(
        OUTPUT_CSV,
        index=False,
    )

    logger.info(
        "GeoPackage saved: %s",
        OUTPUT_GPKG,
    )

    logger.info(
        "CSV saved: %s",
        OUTPUT_CSV,
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print()
    print("=" * 80)
    print(
        "GLYAB AI — RGI 7.0 "
        "PRODUCTION PREPROCESSING"
    )
    print("=" * 80)

    print()
    print("Raw directory:")
    print(RAW_RGI_DIR)

    # --------------------------------------------------------
    # Discover files
    # --------------------------------------------------------

    files = discover_rgi_files()

    print()
    print(
        f"RGI files discovered: {len(files)}"
    )

    for file in files:
        print(
            f"  - {file.name}"
        )

    # --------------------------------------------------------
    # Process files
    # --------------------------------------------------------

    processed_frames = []

    for file in files:

        processed = process_file(
            file
        )

        processed_frames.append(
            processed
        )

    # --------------------------------------------------------
    # Merge regions
    # --------------------------------------------------------

    print()
    print(
        "Merging RGI regions..."
    )

    combined = gpd.GeoDataFrame(
        pd.concat(
            processed_frames,
            ignore_index=True,
        ),
        geometry="geometry",
        crs="EPSG:4326",
    )

    print()
    print(
        f"Combined records: "
        f"{len(combined):,}"
    )

    # --------------------------------------------------------
    # Deduplication
    # --------------------------------------------------------

    (
        combined,
        duplicate_count,
    ) = remove_duplicate_rgi_ids(
        combined
    )

    # --------------------------------------------------------
    # Quality report
    # --------------------------------------------------------

    report = create_quality_report(
        combined,
        files,
        duplicate_count,
    )

    # --------------------------------------------------------
    # Save processed data
    # --------------------------------------------------------

    save_outputs(
        combined
    )

    # --------------------------------------------------------
    # Save quality report
    # --------------------------------------------------------

    QUALITY_REPORT.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print(
        "PREPROCESSING COMPLETE"
    )
    print("=" * 80)

    print()

    print(
        f"Clean records: "
        f"{len(combined):,}"
    )

    print(
        f"Duplicate RGI IDs removed: "
        f"{duplicate_count:,}"
    )

    print(
        f"Invalid geometries: "
        f"{report['invalid_geometry_count']:,}"
    )

    print(
        f"Invalid coordinates: "
        f"{report['invalid_coordinate_count']:,}"
    )

    print(
        f"Invalid RGI IDs: "
        f"{report['invalid_rgi_id_count']:,}"
    )

    print(
        f"Invalid area values: "
        f"{report['invalid_area_count']:,}"
    )

    print(
        f"Invalid elevation values: "
        f"{report['invalid_elevation_count']:,}"
    )

    print()
    print(
        "Quality distribution:"
    )

    for (
        quality,
        count,
    ) in report[
        "quality_distribution"
    ].items():

        print(
            f"  {quality}: {count:,}"
        )

    print()
    print(
        "GeoPackage:"
    )
    print(
        OUTPUT_GPKG
    )

    print()
    print(
        "CSV:"
    )
    print(
        OUTPUT_CSV
    )

    print()
    print(
        "Quality report:"
    )
    print(
        QUALITY_REPORT
    )

    print()
    print("=" * 80)


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
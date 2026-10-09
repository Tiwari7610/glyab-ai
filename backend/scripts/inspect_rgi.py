from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd


# ============================================================
# GLYAB AI
# RGI 7.0 DATA INSPECTION ENGINE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RGI_DIR = BASE_DIR / "data" / "raw" / "rgi_v7"


def find_shapefiles() -> list[Path]:
    """Find all RGI shapefiles recursively."""

    shapefiles = sorted(RGI_DIR.rglob("*.shp"))

    return shapefiles


def inspect_shapefile(path: Path) -> None:
    """Inspect one RGI shapefile without modifying it."""

    print("\n" + "=" * 80)
    print("GLYAB AI — RGI DATA INSPECTION")
    print("=" * 80)

    print(f"\nFILE:")
    print(path)

    print(f"\nSIZE:")
    print(f"{path.stat().st_size / (1024 * 1024):.2f} MB")

    print("\nLoading shapefile...")

    gdf = gpd.read_file(path)

    print("\n" + "-" * 80)
    print("BASIC INFORMATION")
    print("-" * 80)

    print(f"Rows              : {len(gdf):,}")
    print(f"Columns           : {len(gdf.columns):,}")
    print(f"CRS               : {gdf.crs}")
    print(f"Geometry type     : {gdf.geometry.geom_type.value_counts().to_dict()}")

    print("\n" + "-" * 80)
    print("COLUMNS")
    print("-" * 80)

    for index, column in enumerate(gdf.columns, start=1):
        print(f"{index:>3}. {column}")

    print("\n" + "-" * 80)
    print("DATA TYPES")
    print("-" * 80)

    print(gdf.dtypes.to_string())

    print("\n" + "-" * 80)
    print("MISSING VALUES")
    print("-" * 80)

    missing = (
        gdf.isna()
        .sum()
        .sort_values(ascending=False)
    )

    missing_percent = (
        (missing / len(gdf)) * 100
    ).round(2)

    missing_report = pd.DataFrame(
        {
            "missing_count": missing,
            "missing_percent": missing_percent,
        }
    )

    print(
        missing_report[
            missing_report["missing_count"] > 0
        ].to_string()
    )

    print("\n" + "-" * 80)
    print("DUPLICATES")
    print("-" * 80)

    print(
        f"Duplicate rows: "
        f"{gdf.duplicated().sum():,}"
    )

    print("\n" + "-" * 80)
    print("GEOMETRY QUALITY")
    print("-" * 80)

    invalid_geometry = (~gdf.geometry.is_valid).sum()
    empty_geometry = gdf.geometry.is_empty.sum()
    null_geometry = gdf.geometry.isna().sum()

    print(f"Invalid geometries : {invalid_geometry:,}")
    print(f"Empty geometries   : {empty_geometry:,}")
    print(f"Null geometries    : {null_geometry:,}")

    print("\n" + "-" * 80)
    print("GEOGRAPHIC EXTENT")
    print("-" * 80)

    if not gdf.empty:

        bounds = gdf.total_bounds

        print(f"Minimum X : {bounds[0]}")
        print(f"Minimum Y : {bounds[1]}")
        print(f"Maximum X : {bounds[2]}")
        print(f"Maximum Y : {bounds[3]}")

    print("\n" + "-" * 80)
    print("SAMPLE RECORDS")
    print("-" * 80)

    print(
        gdf.head(5).to_string()
    )

    print("\n" + "-" * 80)
    print("NUMERIC SUMMARY")
    print("-" * 80)

    numeric_columns = gdf.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:

        print(
            gdf[numeric_columns]
            .describe()
            .transpose()
            .to_string()
        )

    print("\n" + "=" * 80)
    print("INSPECTION COMPLETE")
    print("=" * 80)


def main() -> None:

    print("\n")
    print("=" * 80)
    print("GLYAB AI — RGI 7.0 DATA DISCOVERY")
    print("=" * 80)

    print(f"\nRGI directory:")
    print(RGI_DIR)

    if not RGI_DIR.exists():

        print(
            "\nERROR: RGI directory does not exist."
        )

        print(
            "\nExpected:"
        )

        print(RGI_DIR)

        return

    shapefiles = find_shapefiles()

    print(
        f"\nShapefiles found: "
        f"{len(shapefiles)}"
    )

    if not shapefiles:

        print(
            "\nERROR: No .shp files found."
        )

        return

    for index, shapefile in enumerate(
        shapefiles,
        start=1,
    ):

        print(
            f"\n[{index}] "
            f"{shapefile}"
        )

    # Inspect every discovered shapefile.
    for shapefile in shapefiles:

        inspect_shapefile(
            shapefile
        )


if __name__ == "__main__":
    main()
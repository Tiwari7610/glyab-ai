from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from data_loader import (
    load_glof_history,
    load_glacier_master,
)

from feature_engineering import (
    prepare_glacier_features,
)


EARTH_RADIUS_KM = 6371.0088

# Initial association radius.
# We will later test sensitivity at multiple radii.
EVENT_RADIUS_KM = 10.0


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "glof_training_dataset.csv"


def nearest_event_distance(
    glacier_lat: np.ndarray,
    glacier_lon: np.ndarray,
    event_lat: np.ndarray,
    event_lon: np.ndarray,
):
    """
    Calculate nearest historical GLOF-event distance
    using spherical coordinates.
    """

    glacier_coords = np.radians(
        np.column_stack(
            [
                glacier_lat,
                glacier_lon,
            ]
        )
    )

    event_coords = np.radians(
        np.column_stack(
            [
                event_lat,
                event_lon,
            ]
        )
    )

    tree = BallTree(
        event_coords,
        metric="haversine",
    )

    distances, indices = tree.query(
        glacier_coords,
        k=1,
    )

    distances_km = (
        distances[:, 0]
        * EARTH_RADIUS_KM
    )

    nearest_indices = indices[:, 0]

    return distances_km, nearest_indices


def main():

    print("\n==============================")
    print(" GLYAB TRAINING DATA BUILDER")
    print("==============================\n")

    glof = load_glof_history()
    glaciers = load_glacier_master()

    print("\nGLOF columns:", len(glof.columns))
    print("Glacier columns:", len(glaciers.columns))

    # -----------------------------------------
    # Historical event coordinates
    # -----------------------------------------

    event_lat = pd.to_numeric(
        glof["Lat_lake"],
        errors="coerce",
    )

    event_lon = pd.to_numeric(
        glof["Lon_lake"],
        errors="coerce",
    )

    valid_events = (
        event_lat.notna()
        & event_lon.notna()
        & event_lat.between(-90, 90)
        & event_lon.between(-180, 180)
    )

    glof = glof.loc[valid_events].copy()

    event_lat = event_lat.loc[valid_events]
    event_lon = event_lon.loc[valid_events]

    print(
        f"\nValid historical events: "
        f"{len(glof):,}"
    )

    # -----------------------------------------
    # Glacier features
    # -----------------------------------------

    features = prepare_glacier_features(
        glaciers
    )

    valid_glaciers = (
        features["latitude"].notna()
        & features["longitude"].notna()
        & features["latitude"].between(-90, 90)
        & features["longitude"].between(-180, 180)
    )

    glaciers = glaciers.loc[
        valid_glaciers
    ].reset_index(drop=True)

    features = features.loc[
        valid_glaciers
    ].reset_index(drop=True)

    print(
        f"Valid glacier records: "
        f"{len(features):,}"
    )

    # -----------------------------------------
    # Spatial association
    # -----------------------------------------

    distances, event_indices = nearest_event_distance(
        features["latitude"].to_numpy(),
        features["longitude"].to_numpy(),
        event_lat.to_numpy(),
        event_lon.to_numpy(),
    )

    features["nearest_glof_km"] = distances

    features["historical_glof"] = (
        distances <= EVENT_RADIUS_KM
    ).astype(int)

    # -----------------------------------------
    # Historical event metadata
    # -----------------------------------------

    nearest_events = glof.iloc[
        event_indices
    ].reset_index(drop=True)

    features["historical_event_year"] = pd.to_numeric(
        nearest_events["Year_approx"],
        errors="coerce",
    ).to_numpy()

    features["historical_event_count_proxy"] = (
        features["historical_glof"]
    )

    # -----------------------------------------
    # Keep original glacier identifiers
    # -----------------------------------------

    for column in [
        "rgi_id",
        "glacier_name",
        "o1region",
        "o2region",
    ]:

        if column in glaciers.columns:
            features[column] = glaciers[
                column
            ].values

    # -----------------------------------------
    # Remove impossible values
    # -----------------------------------------

    features.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True,
    )

    numeric_columns = features.select_dtypes(
        include=np.number
    ).columns

    features[numeric_columns] = (
        features[numeric_columns]
        .replace([np.inf, -np.inf], np.nan)
    )

    # -----------------------------------------
    # Save
    # -----------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    features.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\n==============================")
    print(" TRAINING DATA READY")
    print("==============================")

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print(
        f"Rows: {len(features):,}"
    )

    print(
        "\nTarget distribution:"
    )

    print(
        features["historical_glof"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()
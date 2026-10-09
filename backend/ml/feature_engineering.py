import numpy as np
import pandas as pd


def numeric_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> pd.Series:

    for column in candidates:
        if column in df.columns:
            return pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return pd.Series(
        np.nan,
        index=df.index,
        dtype="float64",
    )


def prepare_glacier_features(
    glacier_df: pd.DataFrame,
) -> pd.DataFrame:

    df = pd.DataFrame(index=glacier_df.index)

    df["latitude"] = numeric_column(
        glacier_df,
        ["latitude", "lat", "cenlat"],
    )

    df["longitude"] = numeric_column(
        glacier_df,
        ["longitude", "lon", "cenlon"],
    )

    df["area_km2"] = numeric_column(
        glacier_df,
        ["area_km2"],
    )

    df["elevation_min_m"] = numeric_column(
        glacier_df,
        ["min_elevation_m", "elevation_min_m", "zmin_m"],
    )

    df["elevation_max_m"] = numeric_column(
        glacier_df,
        ["max_elevation_m", "elevation_max_m", "zmax_m"],
    )

    df["mean_elevation_m"] = numeric_column(
        glacier_df,
        ["median_elevation_m", "mean_elevation_m", "zmed_m"],
    )

    df["slope_deg"] = numeric_column(
        glacier_df,
        ["slope_deg", "slope_degree"],
    )

    df["aspect_deg"] = numeric_column(
        glacier_df,
        ["aspect_deg", "aspect_degree"],
    )

    df["elevation_range_m"] = (
        df["elevation_max_m"]
        - df["elevation_min_m"]
    )

    df["area_log"] = np.log1p(
        df["area_km2"].clip(lower=0)
    )

    return df
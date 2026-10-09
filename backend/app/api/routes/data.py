"""
GLYAB AI
GLOF Dataset API

Provides real training-dataset data to the frontend.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "glof_training_dataset.csv"
)

FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "area_km2",
    "elevation_min_m",
    "elevation_max_m",
    "mean_elevation_m",
    "slope_deg",
    "aspect_deg",
    "elevation_range_m",
    "area_log",
    "o1region",
]


def load_dataset() -> pd.DataFrame:
    """
    Load the real GLYAB GLOF training dataset.
    """

    if not DATASET_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "message": "GLOF training dataset not found.",
                "path": str(DATASET_PATH),
            },
        )

    try:
        return pd.read_csv(DATASET_PATH)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Unable to read GLOF dataset.",
                "error": str(exc),
            },
        )


@router.get("/data")
async def get_glof_data(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    )
):
    """
    Return real GLOF dataset records.
    """

    df = load_dataset()

    available_features = [
        column
        for column in FEATURE_COLUMNS
        if column in df.columns
    ]

    optional_columns = [
        "historical_glof",
        "risk",
        "label",
        "target",
    ]

    for column in optional_columns:
        if column in df.columns:
            available_features.append(column)

    if not available_features:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "No expected GLOF features found in dataset.",
                "columns": list(df.columns),
            },
        )

    result_df = df[available_features].head(limit).copy()

    result_df = result_df.replace(
        [float("inf"), float("-inf")],
        None,
    )

    result_df = result_df.where(
        pd.notnull(result_df),
        None,
    )

    return {
        "success": True,
        "dataset": "glof_training_dataset.csv",
        "source": str(DATASET_PATH),
        "total_rows": int(len(df)),
        "returned_rows": int(len(result_df)),
        "columns": available_features,
        "data": result_df.to_dict(
            orient="records"
        ),
    }


@router.get("/data/summary")
async def get_glof_data_summary():
    """
    Return statistical information about the real dataset.
    """

    df = load_dataset()

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    statistics = {}

    for column in numeric_columns:
        series = df[column].dropna()

        if len(series) == 0:
            continue

        statistics[column] = {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "median": float(series.median()),
        }

    class_distribution = {}

    for column in [
        "historical_glof",
        "risk",
        "label",
        "target",
    ]:
        if column in df.columns:
            counts = (
                df[column]
                .value_counts(dropna=False)
                .to_dict()
            )

            class_distribution[column] = {
                str(key): int(value)
                for key, value in counts.items()
            }

    return {
        "success": True,
        "dataset": "glof_training_dataset.csv",
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "numeric_features": numeric_columns,
        "statistics": statistics,
        "class_distribution": class_distribution,
    }
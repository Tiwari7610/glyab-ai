"""
GLYAB AI
GLOF ML Prediction API

Production-ready prediction endpoint.
Connects:
Frontend → FastAPI → ML Predictor → Trained Model
"""

from __future__ import annotations

import math
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from ml.predictor import get_predictor


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger("glyab.glof")


# ============================================================
# ROUTER
# ============================================================

router = APIRouter()


# ============================================================
# REQUEST SCHEMA
# ============================================================

class GLOFPredictionRequest(BaseModel):
    """
    Input features required by GLYAB GLOF ML model.
    """

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Glacier latitude",
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Glacier longitude",
    )

    area_km2: float = Field(
        ...,
        ge=0,
        description="Glacial lake area in km²",
    )

    elevation_min_m: float = Field(
        ...,
        ge=0,
        description="Minimum elevation in meters",
    )

    elevation_max_m: float = Field(
        ...,
        ge=0,
        description="Maximum elevation in meters",
    )

    mean_elevation_m: float = Field(
        ...,
        ge=0,
        description="Mean elevation in meters",
    )

    slope_deg: float = Field(
        ...,
        ge=0,
        le=90,
        description="Terrain slope in degrees",
    )

    aspect_deg: float = Field(
        ...,
        ge=0,
        le=360,
        description="Terrain aspect in degrees",
    )

    # --------------------------------------------------------
    # Derived features
    # --------------------------------------------------------

    elevation_range_m: float | None = Field(
        default=None,
        ge=0,
        description="Elevation range",
    )

    area_log: float | None = Field(
        default=None,
        description="Log transformed lake area",
    )

    o1region: float | None = Field(
        default=0,
        description="Encoded region feature",
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    @field_validator("elevation_max_m")
    @classmethod
    def validate_elevation_max(
        cls,
        value: float,
    ) -> float:

        if not math.isfinite(value):
            raise ValueError(
                "elevation_max_m must be a finite number"
            )

        return value

    @field_validator("mean_elevation_m")
    @classmethod
    def validate_mean_elevation(
        cls,
        value: float,
    ) -> float:

        if not math.isfinite(value):
            raise ValueError(
                "mean_elevation_m must be a finite number"
            )

        return value


# ============================================================
# MODEL ACCESS
# ============================================================

def get_model():

    try:
        return get_predictor()

    except Exception as exc:

        logger.exception(
            "Unable to load GLYAB GLOF model"
        )

        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": "GLOF ML model is unavailable",
                "error": str(exc),
            },
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get(
    "/health",
    tags=["GLOF Prediction"],
)
async def prediction_health():

    try:

        predictor = get_model()

        return {
            "success": True,
            "service": "GLYAB GLOF ML",
            "status": "online",
            "model": "glyab_glof_model.joblib",
            "model_loaded": True,
            "features": getattr(
                predictor,
                "features",
                [],
            ),
        }

    except Exception as exc:

        return {
            "success": False,
            "service": "GLYAB GLOF ML",
            "status": "degraded",
            "model_loaded": False,
            "error": str(exc),
        }


# ============================================================
# PREDICTION
# ============================================================

@router.post(
    "/predict",
    tags=["GLOF Prediction"],
)
async def predict_glof(
    request: GLOFPredictionRequest,
):

    try:

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if request.elevation_max_m < request.elevation_min_m:

            raise HTTPException(
                status_code=422,
                detail={
                    "success": False,
                    "message": (
                        "Maximum elevation cannot be "
                        "less than minimum elevation."
                    ),
                },
            )

        # ----------------------------------------------------
        # CALCULATE DERIVED FEATURES
        # ----------------------------------------------------

        elevation_range = (
            request.elevation_range_m
            if request.elevation_range_m is not None
            else (
                request.elevation_max_m
                - request.elevation_min_m
            )
        )

        area_log = (
            request.area_log
            if request.area_log is not None
            else math.log1p(
                request.area_km2
            )
        )

        region = (
            request.o1region
            if request.o1region is not None
            else 0
        )

        # ----------------------------------------------------
        # BUILD MODEL INPUT
        # ----------------------------------------------------

        data = {

            "latitude": request.latitude,

            "longitude": request.longitude,

            "area_km2": request.area_km2,

            "elevation_min_m": request.elevation_min_m,

            "elevation_max_m": request.elevation_max_m,

            "mean_elevation_m": request.mean_elevation_m,

            "slope_deg": request.slope_deg,

            "aspect_deg": request.aspect_deg,

            "elevation_range_m": elevation_range,

            "area_log": area_log,

            "o1region": region,
        }

        logger.info(
            "GLOF prediction request received: %s",
            data,
        )

        # ----------------------------------------------------
        # LOAD MODEL
        # ----------------------------------------------------

        predictor = get_model()

        # ----------------------------------------------------
        # RUN ML MODEL
        # ----------------------------------------------------

        result = predictor.predict(data)

        logger.info(
            "GLOF prediction completed: %s",
            result,
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {

            "success": True,

            "system": "GLYAB AI",

            "service": "GLOF Prediction",

            "prediction": result,

            "input_features": data,

            "model": {
                "name": "GLYAB GLOF Risk Model",
                "status": "loaded",
                "type": "Machine Learning",
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "GLOF prediction failed"
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success": False,

                "message": (
                    "GLOF prediction failed"
                ),

                "error": str(exc),
            },
        )


# ============================================================
# MODEL INFORMATION
# ============================================================

@router.get(
    "/model-info",
    tags=["GLOF Prediction"],
)
async def model_info():

    try:

        predictor = get_model()

        return {

            "success": True,

            "model": "GLYAB GLOF Risk Model",

            "file": "glyab_glof_model.joblib",

            "status": "loaded",

            "features": getattr(
                predictor,
                "features",
                [],
            ),

        }

    except Exception as exc:

        raise HTTPException(

            status_code=503,

            detail={
                "success": False,
                "message": "Model information unavailable",
                "error": str(exc),
            },
        )
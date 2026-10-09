"""
GLYAB AI
Cryosphere Intelligence & GLOF Early Warning System

Main FastAPI application.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import (
    check_database_connection,
    get_database_info,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("glyab")


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""

    logger.info("=" * 60)
    logger.info("GLYAB AI BACKEND STARTING")
    logger.info("=" * 60)

    logger.info(
        "Application: %s",
        settings.APP_NAME,
    )

    logger.info(
        "Version: %s",
        settings.APP_VERSION,
    )

    logger.info(
        "Environment: %s",
        settings.APP_ENV,
    )

    # --------------------------------------------------------
    # DATABASE CHECK
    # --------------------------------------------------------

    database_online = check_database_connection()

    if database_online:
        logger.info(
            "MySQL database connection: ONLINE"
        )
    else:
        logger.warning(
            "MySQL database connection: OFFLINE"
        )

    logger.info(
        "Database: %s",
        get_database_info()["database"],
    )

    # --------------------------------------------------------
    # AI STATUS
    # --------------------------------------------------------

    logger.info(
        "AI Risk Model: %s",
        settings.RISK_MODEL_NAME,
    )

    logger.info(
        "Anomaly Model: %s",
        settings.ANOMALY_MODEL_NAME,
    )

    # --------------------------------------------------------
    # MQTT STATUS
    # --------------------------------------------------------

    logger.info(
        "MQTT Gateway: %s",
        (
            "ENABLED"
            if settings.MQTT_ENABLED
            else "STANDBY"
        ),
    )

    logger.info("=" * 60)

    yield

    # --------------------------------------------------------
    # SHUTDOWN
    # --------------------------------------------------------

    logger.info(
        "GLYAB AI BACKEND SHUTTING DOWN"
    )

    logger.info("=" * 60)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered Cryosphere Intelligence "
        "& GLOF Early Warning System"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():
    return {
        "system": "GLYAB AI",
        "mission": (
            "Cryosphere Intelligence "
            "& GLOF Early Warning"
        ),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "status": "online",
        "api_prefix": settings.API_V1_PREFIX,
    }


# ============================================================
# GENERAL HEALTH
# ============================================================

@app.get(
    "/health",
    tags=["System"],
)
async def health():

    database_online = (
        check_database_connection()
    )

    return {
        "status": (
            "healthy"
            if database_online
            else "degraded"
        ),
        "api": "online",
        "database": (
            "online"
            if database_online
            else "offline"
        ),
        "ai_engine": "initializing",
        "risk_model": (
            settings.RISK_MODEL_NAME
        ),
        "anomaly_engine": (
            settings.ANOMALY_MODEL_NAME
        ),
        "sensor_gateway": (
            "enabled"
            if settings.MQTT_ENABLED
            else "standby"
        ),
    }


# ============================================================
# DATABASE HEALTH
# ============================================================

@app.get(
    "/health/database",
    tags=["System"],
)
async def database_health():

    online = (
        check_database_connection()
    )

    database_info = (
        get_database_info()
    )

    return {
        "status": (
            "online"
            if online
            else "offline"
        ),
        "database": database_info,
    }
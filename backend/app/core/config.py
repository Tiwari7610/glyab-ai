"""
GLYAB AI
Cryosphere Intelligence & GLOF Early Warning System

Central application configuration.

Architecture:
    Frontend
        ↓
    FastAPI
        ↓
    AI / GLOF Prediction Engine
        ↓
    Trained ML Model
        ↓
    Risk Intelligence
        ↓
    AI Copilot / Dashboard
"""

from __future__ import annotations

import configparser
import logging
from functools import lru_cache
from pathlib import Path


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger("glyab.config")


# ============================================================
# PROJECT PATHS
# ============================================================

# backend/
BASE_DIR = Path(__file__).resolve().parents[2]

# backend/config.ini
CONFIG_FILE = BASE_DIR / "config.ini"


# ============================================================
# CONFIGURATION LOADER
# ============================================================

config = configparser.ConfigParser()

if CONFIG_FILE.exists():
    config.read(CONFIG_FILE, encoding="utf-8")
else:
    logger.warning(
        "config.ini not found. Using built-in defaults."
    )


# ============================================================
# SAFE CONFIG HELPERS
# ============================================================

def get_config(
    section: str,
    key: str,
    default: str = "",
) -> str:
    """Read string configuration safely."""

    try:
        if config.has_option(section, key):
            return config.get(section, key).strip()
    except Exception as exc:
        logger.warning(
            "Config read failed [%s.%s]: %s",
            section,
            key,
            exc,
        )

    return default


def get_bool(
    section: str,
    key: str,
    default: bool = False,
) -> bool:
    """Read boolean configuration."""

    value = get_config(
        section,
        key,
        str(default),
    ).lower()

    return value in {
        "true",
        "1",
        "yes",
        "on",
        "enabled",
    }


def get_int(
    section: str,
    key: str,
    default: int,
) -> int:
    """Read integer configuration."""

    value = get_config(
        section,
        key,
        str(default),
    )

    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_float(
    section: str,
    key: str,
    default: float,
) -> float:
    """Read floating-point configuration."""

    value = get_config(
        section,
        key,
        str(default),
    )

    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_list(
    section: str,
    key: str,
    default: list[str],
) -> list[str]:
    """Read comma-separated configuration."""

    value = get_config(section, key, "")

    if not value:
        return default

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


# ============================================================
# SETTINGS
# ============================================================

class Settings:
    """
    Central configuration object for GLYAB AI.

    All backend services should read configuration
    through this class.
    """

    # ========================================================
    # APPLICATION
    # ========================================================

    APP_NAME: str = get_config(
        "application",
        "name",
        "GLYAB AI",
    )

    APP_VERSION: str = get_config(
        "application",
        "version",
        "1.0.0",
    )

    APP_ENV: str = get_config(
        "application",
        "environment",
        "development",
    )

    DEBUG: bool = get_bool(
        "application",
        "debug",
        True,
    )

    LOG_LEVEL: str = get_config(
        "application",
        "log_level",
        "INFO",
    )

    # ========================================================
    # API
    # ========================================================

    API_V1_PREFIX: str = get_config(
        "api",
        "prefix",
        "/api/v1",
    )

    API_HOST: str = get_config(
        "api",
        "host",
        "127.0.0.1",
    )

    API_PORT: int = get_int(
        "api",
        "port",
        8000,
    )

    API_DOCS_ENABLED: bool = get_bool(
        "api",
        "docs_enabled",
        True,
    )

    API_TIMEOUT_SECONDS: int = get_int(
        "api",
        "timeout_seconds",
        30,
    )

    # ========================================================
    # CORS
    # ========================================================

    # React / Vite frontend
    CORS_ORIGINS: list[str] = get_list(
        "cors",
        "origins",
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ],
    )

    # ========================================================
    # DATABASE
    # ========================================================

    DB_USER: str = get_config(
        "database",
        "user",
        "root",
    )

    DB_PASSWORD: str = get_config(
        "database",
        "password",
        "",
    )

    DB_HOST: str = get_config(
        "database",
        "host",
        "127.0.0.1",
    )

    DB_PORT: int = get_int(
        "database",
        "port",
        3306,
    )

    DB_NAME: str = get_config(
        "database",
        "name",
        "glyab_db",
    )

    DB_POOL_SIZE: int = get_int(
        "database",
        "pool_size",
        10,
    )

    DB_MAX_OVERFLOW: int = get_int(
        "database",
        "max_overflow",
        20,
    )

    DB_POOL_TIMEOUT: int = get_int(
        "database",
        "pool_timeout",
        30,
    )

    DB_POOL_RECYCLE: int = get_int(
        "database",
        "pool_recycle",
        3600,
    )

    DB_CONNECT_TIMEOUT: int = get_int(
        "database",
        "connect_timeout",
        10,
    )

    DB_ENABLED: bool = get_bool(
        "database",
        "enabled",
        True,
    )

    # ========================================================
    # AI ENGINE
    # ========================================================

    AI_ENABLED: bool = get_bool(
        "ai",
        "enabled",
        True,
    )

    AI_MODEL_DIRECTORY: str = get_config(
        "ai",
        "model_directory",
        "trained_models",
    )

    # Actual trained model created by your training pipeline
    RISK_MODEL_FILE: str = get_config(
        "ai",
        "risk_model_file",
        "glyab_glof_model.joblib",
    )

    RISK_MODEL_NAME: str = get_config(
        "ai",
        "risk_model_name",
        "GLYAB GLOF Risk Model",
    )

    ANOMALY_MODEL_FILE: str = get_config(
        "ai",
        "anomaly_model_file",
        "anomaly_model.joblib",
    )

    ANOMALY_MODEL_NAME: str = get_config(
        "ai",
        "anomaly_model_name",
        "GLYAB Cryosphere Anomaly Engine",
    )

    FEATURE_SCHEMA_FILE: str = get_config(
        "ai",
        "feature_schema_file",
        "feature_schema.json",
    )

    MODEL_METRICS_FILE: str = get_config(
        "ai",
        "model_metrics_file",
        "model_metrics.json",
    )

    FEATURE_VERSION: str = get_config(
        "ai",
        "feature_version",
        "v1.0",
    )

    MODEL_THRESHOLD: float = get_float(
        "ai",
        "model_threshold",
        0.50,
    )

    # ========================================================
    # GLOF RISK ENGINE
    # ========================================================

    GLOF_ENGINE_ENABLED: bool = get_bool(
        "glof",
        "enabled",
        True,
    )

    LOW_RISK_THRESHOLD: float = get_float(
        "glof",
        "low_risk_threshold",
        0.30,
    )

    MEDIUM_RISK_THRESHOLD: float = get_float(
        "glof",
        "medium_risk_threshold",
        0.60,
    )

    HIGH_RISK_THRESHOLD: float = get_float(
        "glof",
        "high_risk_threshold",
        0.80,
    )

    CRITICAL_RISK_THRESHOLD: float = get_float(
        "glof",
        "critical_risk_threshold",
        0.90,
    )

    # ========================================================
    # AI COPILOT
    # ========================================================

    COPILOT_ENABLED: bool = get_bool(
        "copilot",
        "enabled",
        True,
    )

    COPILOT_NAME: str = get_config(
        "copilot",
        "name",
        "GLYAB AI Copilot",
    )

    COPILOT_MAX_CONTEXT: int = get_int(
        "copilot",
        "max_context",
        12,
    )

    COPILOT_MAX_RESPONSE_TOKENS: int = get_int(
        "copilot",
        "max_response_tokens",
        800,
    )

    # ========================================================
    # DATA PIPELINE
    # ========================================================

    RAW_DATA_DIRECTORY: str = get_config(
        "data",
        "raw_directory",
        "data/raw",
    )

    PROCESSED_DATA_DIRECTORY: str = get_config(
        "data",
        "processed_directory",
        "data/processed",
    )

    RGI_DATA_DIRECTORY: str = get_config(
        "data",
        "rgi_directory",
        "data/raw/rgi_v7",
    )

    TRAINING_DATASET_FILE: str = get_config(
        "data",
        "training_dataset",
        "data/processed/glof_training_dataset.csv",
    )

    GLOF_HISTORY_FILE: str = get_config(
        "data",
        "glof_history",
        "data/raw/glof_history.csv",
    )

    GLACIER_MASTER_FILE: str = get_config(
        "data",
        "glacier_master",
        "data/processed/glacier_master.csv",
    )

    RGI_CLEAN_FILE: str = get_config(
        "data",
        "rgi_clean",
        "data/processed/rgi_v7_clean.csv",
    )

    # ========================================================
    # HARDWARE / SENSOR GATEWAY
    # ========================================================

    MQTT_ENABLED: bool = get_bool(
        "mqtt",
        "enabled",
        False,
    )

    MQTT_HOST: str = get_config(
        "mqtt",
        "host",
        "127.0.0.1",
    )

    MQTT_PORT: int = get_int(
        "mqtt",
        "port",
        1883,
    )

    MQTT_USERNAME: str = get_config(
        "mqtt",
        "username",
        "",
    )

    MQTT_PASSWORD: str = get_config(
        "mqtt",
        "password",
        "",
    )

    MQTT_TOPIC_PREFIX: str = get_config(
        "mqtt",
        "topic_prefix",
        "glyab",
    )

    # ========================================================
    # ALERT ENGINE
    # ========================================================

    ALERTS_ENABLED: bool = get_bool(
        "alerts",
        "enabled",
        True,
    )

    ALERT_COOLDOWN_SECONDS: int = get_int(
        "alerts",
        "cooldown_seconds",
        900,
    )

    # ========================================================
    # PATH HELPERS
    # ========================================================

    @property
    def raw_data_path(self) -> Path:
        return BASE_DIR / self.RAW_DATA_DIRECTORY

    @property
    def processed_data_path(self) -> Path:
        return BASE_DIR / self.PROCESSED_DATA_DIRECTORY

    @property
    def rgi_data_path(self) -> Path:
        return BASE_DIR / self.RGI_DATA_DIRECTORY

    @property
    def training_dataset_path(self) -> Path:
        path = BASE_DIR / self.TRAINING_DATASET_FILE
        return path

    @property
    def glof_history_path(self) -> Path:
        return BASE_DIR / self.GLOF_HISTORY_FILE

    @property
    def glacier_master_path(self) -> Path:
        return BASE_DIR / self.GLACIER_MASTER_FILE

    @property
    def rgi_clean_path(self) -> Path:
        return BASE_DIR / self.RGI_CLEAN_FILE

    @property
    def model_path(self) -> Path:
        return BASE_DIR / self.AI_MODEL_DIRECTORY

    @property
    def risk_model_path(self) -> Path:
        return self.model_path / self.RISK_MODEL_FILE

    @property
    def anomaly_model_path(self) -> Path:
        return self.model_path / self.ANOMALY_MODEL_FILE

    @property
    def feature_schema_path(self) -> Path:
        return self.model_path / self.FEATURE_SCHEMA_FILE

    @property
    def model_metrics_path(self) -> Path:
        return self.model_path / self.MODEL_METRICS_FILE

    # ========================================================
    # MODEL STATUS
    # ========================================================

    @property
    def risk_model_exists(self) -> bool:
        return self.risk_model_path.exists()

    @property
    def anomaly_model_exists(self) -> bool:
        return self.anomaly_model_path.exists()

    @property
    def feature_schema_exists(self) -> bool:
        return self.feature_schema_path.exists()

    # ========================================================
    # DATABASE URL
    # ========================================================

    @property
    def database_url(self) -> str:
        """
        SQLAlchemy-compatible MySQL connection URL.

        Password is not logged anywhere.
        """

        return (
            f"mysql+pymysql://"
            f"{self.DB_USER}:"
            f"{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )

    # ========================================================
    # SYSTEM SUMMARY
    # ========================================================

    def system_summary(self) -> dict:
        """Return safe runtime configuration."""

        return {
            "application": self.APP_NAME,
            "version": self.APP_VERSION,
            "environment": self.APP_ENV,
            "api": {
                "host": self.API_HOST,
                "port": self.API_PORT,
                "prefix": self.API_V1_PREFIX,
            },
            "ai": {
                "enabled": self.AI_ENABLED,
                "risk_model": self.RISK_MODEL_NAME,
                "risk_model_file": self.RISK_MODEL_FILE,
                "risk_model_exists": self.risk_model_exists,
                "feature_version": self.FEATURE_VERSION,
            },
            "glof_engine": {
                "enabled": self.GLOF_ENGINE_ENABLED,
                "low": self.LOW_RISK_THRESHOLD,
                "medium": self.MEDIUM_RISK_THRESHOLD,
                "high": self.HIGH_RISK_THRESHOLD,
                "critical": self.CRITICAL_RISK_THRESHOLD,
            },
            "copilot": {
                "enabled": self.COPILOT_ENABLED,
                "name": self.COPILOT_NAME,
            },
            "mqtt": {
                "enabled": self.MQTT_ENABLED,
            },
        }


# ============================================================
# CACHED SETTINGS
# ============================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


settings = get_settings()
"""
GLYAB AI COPILOT
================
Cryosphere Intelligence Engine

Features:
- Natural language intent detection
- Entity extraction
- MySQL-backed glacier analytics
- Glacial lake analytics
- GLOF risk context
- AI model context
- Hardware / ESP32 / MQTT context
- News intelligence placeholder
- Explainable responses
- Frontend / FastAPI ready

Scientific rule:
No fake scientific prediction is generated.
Real model outputs will be connected when the ML engine is ready.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.glacier import Glacier

try:
    from app.models.lake import GlacialLake
except ImportError:
    GlacialLake = None


# ============================================================
# INTENT RESULT
# ============================================================

@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: dict[str, Any]


# ============================================================
# GLYAB COPILOT
# ============================================================

class GLYABCopilot:
    """
    Main GLYAB intelligence engine.

    Pipeline:

        USER QUESTION
             |
             v
        INTENT ENGINE
             |
             v
        ENTITY EXTRACTION
             |
             v
        DATABASE CONTEXT
             |
             v
        INTELLIGENCE ENGINE
             |
             v
        EXPLAINABLE RESPONSE
    """

    VERSION = "2.0.0"

    def __init__(self) -> None:
        self.name = "GLYAB AI Copilot"

    # ========================================================
    # MAIN ENTRY POINT
    # ========================================================

    def generate_response(
        self,
        question: str,
        user_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        question = (question or "").strip()

        if not question:
            return self._empty_response()

        intent = self.detect_intent(question)

        context = self.build_context(
            question=question,
            intent=intent,
        )

        answer = self.generate_answer(
            question=question,
            intent=intent,
            context=context,
            user_context=user_context,
        )

        return {
            "assistant": self.name,
            "version": self.VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "question": question,
            "intent": intent.intent,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "answer": answer,
            "context_used": bool(context),
            "context": context,
            "scientific_status": self.scientific_status(),
        }

    # ========================================================
    # INTENT DETECTION
    # ========================================================

    def detect_intent(self, question: str) -> IntentResult:

        q = question.lower().strip()
        entities = self.extract_entities(q)

        # GLOF / RISK
        if any(
            word in q
            for word in [
                "glof",
                "glacial lake outburst",
                "risk",
                "hazard",
                "danger",
                "flood",
                "outburst",
                "warning",
                "alert",
            ]
        ):
            return IntentResult(
                "GLOF_RISK",
                0.97,
                entities,
            )

        # GLACIER STATISTICS
        if any(
            phrase in q
            for phrase in [
                "how many glaciers",
                "number of glaciers",
                "total glaciers",
                "glacier count",
                "glacier statistics",
                "glacier stats",
                "total glacier area",
                "average glacier",
            ]
        ):
            return IntentResult(
                "GLACIER_STATISTICS",
                0.98,
                entities,
            )

        # LARGEST GLACIERS
        if any(
            phrase in q
            for phrase in [
                "largest glacier",
                "largest glaciers",
                "biggest glacier",
                "biggest glaciers",
            ]
        ):
            return IntentResult(
                "LARGEST_GLACIERS",
                0.98,
                entities,
            )

        # HIGHEST GLACIERS
        if any(
            phrase in q
            for phrase in [
                "highest glacier",
                "highest glaciers",
                "highest elevation glacier",
                "highest elevation",
            ]
        ):
            return IntentResult(
                "HIGHEST_GLACIERS",
                0.98,
                entities,
            )

        # GLACIER SEARCH
        if any(
            phrase in q
            for phrase in [
                "find glacier",
                "search glacier",
                "show glacier",
                "glacier near",
                "glacier location",
                "where is glacier",
            ]
        ):
            return IntentResult(
                "GLACIER_SEARCH",
                0.92,
                entities,
            )

        # LAKES
        if any(
            word in q
            for word in [
                "lake",
                "lakes",
                "glacial lake",
                "glacial lakes",
                "water level",
                "lake area",
            ]
        ):
            return IntentResult(
                "GLACIAL_LAKES",
                0.96,
                entities,
            )

        # CLIMATE
        if any(
            word in q
            for word in [
                "temperature",
                "climate",
                "warming",
                "rainfall",
                "precipitation",
                "snowfall",
                "weather",
            ]
        ):
            return IntentResult(
                "CLIMATE",
                0.93,
                entities,
            )

        # HARDWARE
        if any(
            word in q
            for word in [
                "sensor",
                "esp32",
                "hardware",
                "telemetry",
                "mqtt",
                "device",
                "iot",
                "water sensor",
                "temperature sensor",
            ]
        ):
            return IntentResult(
                "HARDWARE",
                0.96,
                entities,
            )

        # AI / MACHINE LEARNING
        if any(
            word in q
            for word in [
                "ai",
                "model",
                "machine learning",
                "xgboost",
                "isolation forest",
                "shap",
                "prediction",
                "forecast",
                "anomaly",
            ]
        ):
            return IntentResult(
                "AI_MODEL",
                0.94,
                entities,
            )

        # NEWS
        if any(
            phrase in q
            for phrase in [
                "news",
                "latest news",
                "recent news",
                "latest update",
                "breaking news",
                "headlines",
            ]
        ):
            return IntentResult(
                "NEWS",
                0.98,
                entities,
            )

        # SYSTEM
        if any(
            phrase in q
            for phrase in [
                "what is glyab",
                "who are you",
                "what can you do",
                "help me",
                "capabilities",
            ]
        ):
            return IntentResult(
                "SYSTEM",
                0.99,
                entities,
            )

        return IntentResult(
            "GENERAL",
            0.55,
            entities,
        )

    # ========================================================
    # ENTITY EXTRACTION
    # ========================================================

    def extract_entities(
        self,
        question: str,
    ) -> dict[str, Any]:

        entities: dict[str, Any] = {}

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        numbers = re.findall(
            r"\b\d+\b",
            question,
        )

        for value in numbers:
            number = int(value)

            if 1 <= number <= 100:
                entities["limit"] = number
                break

        # ----------------------------------------------------
        # COORDINATES
        # ----------------------------------------------------

        coordinate_match = re.search(
            r"(-?\d+(?:\.\d+)?)\s*[, ]\s*"
            r"(-?\d+(?:\.\d+)?)",
            question,
        )

        if coordinate_match:

            try:
                latitude = float(
                    coordinate_match.group(1)
                )

                longitude = float(
                    coordinate_match.group(2)
                )

                if (
                    -90 <= latitude <= 90
                    and -180 <= longitude <= 180
                ):
                    entities["latitude"] = latitude
                    entities["longitude"] = longitude

            except ValueError:
                pass

        # ----------------------------------------------------
        # REGIONS
        # ----------------------------------------------------

        regions = [
            "himalaya",
            "karakoram",
            "ladakh",
            "uttarakhand",
            "himachal",
            "sikkim",
            "nepal",
            "bhutan",
            "india",
        ]

        for region in regions:

            if region in question:
                entities["region"] = region
                break

        return entities

    # ========================================================
    # CONTEXT BUILDER
    # ========================================================

    def build_context(
        self,
        question: str,
        intent: IntentResult,
    ) -> dict[str, Any]:

        try:

            if intent.intent == "GLACIER_STATISTICS":
                return self.glacier_statistics()

            if intent.intent == "LARGEST_GLACIERS":

                limit = intent.entities.get(
                    "limit",
                    5,
                )

                return {
                    "largest_glaciers":
                        self.largest_glaciers(limit)
                }

            if intent.intent == "HIGHEST_GLACIERS":

                limit = intent.entities.get(
                    "limit",
                    5,
                )

                return {
                    "highest_glaciers":
                        self.highest_glaciers(limit)
                }

            if intent.intent == "GLACIER_SEARCH":

                region = intent.entities.get(
                    "region"
                )

                limit = intent.entities.get(
                    "limit",
                    10,
                )

                return {
                    "search_results":
                        self.search_glaciers(
                            region=region,
                            limit=limit,
                        )
                }

            if intent.intent == "GLACIAL_LAKES":
                return self.lake_statistics()

            if intent.intent == "GLOF_RISK":
                return self.risk_context()

            if intent.intent == "AI_MODEL":
                return self.ai_context()

            if intent.intent == "HARDWARE":
                return self.hardware_context()

            return {}

        except Exception as exc:

            return {
                "status": "context_error",
                "error": str(exc),
            }

    # ========================================================
    # GLACIER STATISTICS
    # ========================================================

    def glacier_statistics(
        self,
    ) -> dict[str, Any]:

        with SessionLocal() as session:

            total = session.scalar(
                select(
                    func.count(
                        Glacier.glacier_id
                    )
                )
            ) or 0

            total_area = session.scalar(
                select(
                    func.sum(
                        Glacier.area_km2
                    )
                )
            ) or 0

            average_area = session.scalar(
                select(
                    func.avg(
                        Glacier.area_km2
                    )
                )
            ) or 0

            average_elevation = session.scalar(
                select(
                    func.avg(
                        Glacier.mean_elevation_m
                    )
                )
            ) or 0

            maximum_elevation = session.scalar(
                select(
                    func.max(
                        Glacier.elevation_max_m
                    )
                )
            ) or 0

            return {
                "total_glaciers": int(total),
                "total_area_km2": round(
                    float(total_area),
                    4,
                ),
                "average_area_km2": round(
                    float(average_area),
                    4,
                ),
                "average_elevation_m": round(
                    float(average_elevation),
                    2,
                ),
                "maximum_elevation_m": round(
                    float(maximum_elevation),
                    2,
                ),
                "data_source": (
                    "Randolph Glacier Inventory 7.0"
                ),
            }

    # ========================================================
    # LARGEST GLACIERS
    # ========================================================

    def largest_glaciers(
        self,
        limit: int = 5,
    ) -> list[dict[str, Any]]:

        limit = max(
            1,
            min(int(limit), 100),
        )

        with SessionLocal() as session:

            rows = session.scalars(
                select(Glacier)
                .where(
                    Glacier.area_km2.is_not(None)
                )
                .order_by(
                    Glacier.area_km2.desc()
                )
                .limit(limit)
            ).all()

            return [
                self.glacier_to_dict(row)
                for row in rows
            ]

    # ========================================================
    # HIGHEST GLACIERS
    # ========================================================

    def highest_glaciers(
        self,
        limit: int = 5,
    ) -> list[dict[str, Any]]:

        limit = max(
            1,
            min(int(limit), 100),
        )

        with SessionLocal() as session:

            rows = session.scalars(
                select(Glacier)
                .where(
                    Glacier.elevation_max_m.is_not(None)
                )
                .order_by(
                    Glacier.elevation_max_m.desc()
                )
                .limit(limit)
            ).all()

            return [
                self.glacier_to_dict(row)
                for row in rows
            ]

    # ========================================================
    # GLACIER SEARCH
    # ========================================================

    def search_glaciers(
        self,
        region: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:

        limit = max(
            1,
            min(int(limit), 100),
        )

        with SessionLocal() as session:

            query = select(Glacier)

            if region:

                pattern = f"%{region}%"

                query = query.where(
                    (
                        Glacier.region.ilike(
                            pattern
                        )
                    )
                    |
                    (
                        Glacier.mountain_range.ilike(
                            pattern
                        )
                    )
                    |
                    (
                        Glacier.glacier_name.ilike(
                            pattern
                        )
                    )
                )

            rows = session.scalars(
                query.limit(limit)
            ).all()

            return [
                self.glacier_to_dict(row)
                for row in rows
            ]

    # ========================================================
    # LAKE STATISTICS
    # ========================================================

    def lake_statistics(
        self,
    ) -> dict[str, Any]:

        if GlacialLake is None:

            return {
                "status": "model_unavailable",
                "total_lakes": 0,
            }

        with SessionLocal() as session:

            total = session.scalar(
                select(
                    func.count(
                        GlacialLake.lake_id
                    )
                )
            ) or 0

            total_area = session.scalar(
                select(
                    func.sum(
                        GlacialLake.area_km2
                    )
                )
            ) or 0

            average_area = session.scalar(
                select(
                    func.avg(
                        GlacialLake.area_km2
                    )
                )
            ) or 0

            return {
                "total_lakes": int(total),
                "total_area_km2": round(
                    float(total_area),
                    4,
                ),
                "average_area_km2": round(
                    float(average_area),
                    4,
                ),
            }

    # ========================================================
    # GLOF CONTEXT
    # ========================================================

    def risk_context(
        self,
    ) -> dict[str, Any]:

        return {
            "engine": "XGBoost",
            "status": "model_ready",
            "prediction_available": False,
            "reason": (
                "Verified training labels and trained "
                "model are required before producing "
                "a real GLOF probability."
            ),
            "features": [
                "glacier characteristics",
                "glacial lake characteristics",
                "environmental observations",
                "weather observations",
                "sensor telemetry",
                "historical GLOF events",
            ],
        }

    # ========================================================
    # AI CONTEXT
    # ========================================================

    def ai_context(
        self,
    ) -> dict[str, Any]:

        return {
            "risk_model": "XGBoost",
            "anomaly_model": "Isolation Forest",
            "explainability": "SHAP",
            "forecasting": "Forecasting Engine",
            "copilot": "GLYAB AI Copilot",
            "status": "architecture_ready",
        }

    # ========================================================
    # HARDWARE CONTEXT
    # ========================================================

    def hardware_context(
        self,
    ) -> dict[str, Any]:

        return {
            "gateway": "ESP32",
            "protocol": "MQTT",
            "topic": "glyab/telemetry",
            "status": "integration_ready",
            "telemetry": [
                "water level",
                "temperature",
                "pressure",
                "vibration",
                "battery",
                "device health",
            ],
        }

    # ========================================================
    # ANSWER ENGINE
    # ========================================================

    def generate_answer(
        self,
        question: str,
        intent: IntentResult,
        context: dict[str, Any],
        user_context: dict[str, Any] | None = None,
    ) -> str:

        if context.get("status") == "context_error":

            return (
                "I detected your request, but the "
                "required GLYAB database context could "
                "not be retrieved. Please verify the "
                "backend and MySQL connection."
            )

        # ----------------------------------------------------
        # SYSTEM
        # ----------------------------------------------------

        if intent.intent == "SYSTEM":

            return (
                "I am GLYAB AI Copilot, the intelligence "
                "interface of the GLYAB cryosphere "
                "monitoring system. I can analyze glacier "
                "inventory data, glacial lakes, GLOF-risk "
                "architecture, AI models, environmental "
                "observations and hardware telemetry."
            )

        # ----------------------------------------------------
        # GLACIER STATISTICS
        # ----------------------------------------------------

        if intent.intent == "GLACIER_STATISTICS":

            return (
                f"GLYAB currently contains "
                f"{context['total_glaciers']:,} glacier "
                f"records from RGI 7.0. The mapped glacier "
                f"area is approximately "
                f"{context['total_area_km2']:,.2f} km². "
                f"The average glacier area is "
                f"{context['average_area_km2']:.4f} km² "
                f"and the average elevation is "
                f"{context['average_elevation_m']:,.1f} m. "
                f"The maximum glacier elevation in the "
                f"loaded inventory is "
                f"{context['maximum_elevation_m']:,.2f} m."
            )

        # ----------------------------------------------------
        # LARGEST
        # ----------------------------------------------------

        if intent.intent == "LARGEST_GLACIERS":

            glaciers = context.get(
                "largest_glaciers",
                [],
            )

            if not glaciers:
                return (
                    "No glacier records were found."
                )

            lines = [
                "Based on the current RGI 7.0 database, "
                "the largest glacier records are:"
            ]

            for index, glacier in enumerate(
                glaciers,
                1,
            ):

                lines.append(
                    f"{index}. "
                    f"{glacier['glacier_name']} — "
                    f"{glacier['area_km2']} km²"
                )

            return "\n".join(lines)

        # ----------------------------------------------------
        # HIGHEST
        # ----------------------------------------------------

        if intent.intent == "HIGHEST_GLACIERS":

            glaciers = context.get(
                "highest_glaciers",
                [],
            )

            if not glaciers:
                return (
                    "No glacier elevation records "
                    "were found."
                )

            lines = [
                "Based on the current RGI 7.0 database, "
                "the highest glacier records are:"
            ]

            for index, glacier in enumerate(
                glaciers,
                1,
            ):

                lines.append(
                    f"{index}. "
                    f"{glacier['glacier_name']} — "
                    f"{glacier['elevation_max_m']} m"
                )

            return "\n".join(lines)

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if intent.intent == "GLACIER_SEARCH":

            glaciers = context.get(
                "search_results",
                [],
            )

            if not glaciers:

                return (
                    "I could not find matching glacier "
                    "records in the current database."
                )

            lines = [
                f"I found {len(glaciers)} matching "
                "glacier records:"
            ]

            for glacier in glaciers:

                lines.append(
                    f"- {glacier['glacier_name']} | "
                    f"Area: {glacier['area_km2']} km² | "
                    f"Coordinates: "
                    f"{glacier['latitude']}, "
                    f"{glacier['longitude']}"
                )

            return "\n".join(lines)

        # ----------------------------------------------------
        # LAKES
        # ----------------------------------------------------

        if intent.intent == "GLACIAL_LAKES":

            total = context.get(
                "total_lakes",
                0,
            )

            if total == 0:

                return (
                    "The GLYAB glacial-lake table "
                    "currently contains no loaded records. "
                    "The validated lake dataset exists "
                    "locally, but the MySQL lake table "
                    "does not currently contain usable "
                    "records."
                )

            return (
                f"The GLYAB database currently contains "
                f"{total:,} glacial-lake records with a "
                f"combined mapped area of approximately "
                f"{context['total_area_km2']:,.4f} km²."
            )

        # ----------------------------------------------------
        # GLOF
        # ----------------------------------------------------

        if intent.intent == "GLOF_RISK":

            return (
                "GLYAB's GLOF intelligence engine will "
                "combine glacier characteristics, lake "
                "conditions, environmental observations, "
                "weather and sensor telemetry. The final "
                "XGBoost probability will only be shown "
                "after the verified historical GLOF labels "
                "and trained model are integrated. I will "
                "not fabricate a risk percentage."
            )

        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        if intent.intent == "AI_MODEL":

            return (
                "GLYAB uses a multi-layer AI architecture: "
                "XGBoost for GLOF-risk classification, "
                "Isolation Forest for anomaly detection, "
                "forecasting for environmental trends and "
                "SHAP for explainability. The Copilot is "
                "the reasoning interface that will combine "
                "these outputs with database context."
            )

        # ----------------------------------------------------
        # HARDWARE
        # ----------------------------------------------------

        if intent.intent == "HARDWARE":

            return (
                "The GLYAB hardware gateway is designed "
                "around ESP32 and MQTT. Expected telemetry "
                "includes water level, temperature, "
                "pressure, vibration, battery and device "
                "health. Once the MQTT gateway is connected, "
                "the Copilot can interpret live telemetry "
                "and AI alerts."
            )

        # ----------------------------------------------------
        # CLIMATE
        # ----------------------------------------------------

        if intent.intent == "CLIMATE":

            return (
                "GLYAB climate intelligence will combine "
                "verified weather and environmental "
                "observations with glacier and lake "
                "features. I will not invent a climate "
                "trend without corresponding observations."
            )

        # ----------------------------------------------------
        # NEWS
        # ----------------------------------------------------

        if intent.intent == "NEWS":

            return (
                "GLYAB News Intelligence is designed as "
                "a separate verified information layer. "
                "Live news will later be retrieved from "
                "trusted external sources and kept separate "
                "from scientific sensor and model data."
            )

        # ----------------------------------------------------
        # GENERAL
        # ----------------------------------------------------

        return (
            "I can analyze GLYAB glacier data, glacial "
            "lakes, GLOF-risk architecture, AI models, "
            "climate observations, hardware telemetry "
            "and system status. Try asking: "
            "\"How many glaciers are in GLYAB?\""
        )

    # ========================================================
    # GLACIER SERIALIZER
    # ========================================================

    def glacier_to_dict(
        self,
        glacier: Glacier,
    ) -> dict[str, Any]:

        return {
            "glacier_id": glacier.glacier_id,
            "glacier_code": glacier.glacier_code,
            "glacier_name": glacier.glacier_name,
            "country": glacier.country,
            "state_province": glacier.state_province,
            "region": glacier.region,
            "mountain_range": glacier.mountain_range,
            "latitude": self.safe_float(
                glacier.latitude
            ),
            "longitude": self.safe_float(
                glacier.longitude
            ),
            "elevation_min_m": self.safe_float(
                glacier.elevation_min_m
            ),
            "elevation_max_m": self.safe_float(
                glacier.elevation_max_m
            ),
            "mean_elevation_m": self.safe_float(
                glacier.mean_elevation_m
            ),
            "area_km2": self.safe_float(
                glacier.area_km2
            ),
            "data_source": glacier.data_source,
            "source_dataset_version":
                glacier.source_dataset_version,
        }

    # ========================================================
    # SAFE FLOAT
    # ========================================================

    @staticmethod
    def safe_float(
        value: Any,
    ) -> float | None:

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    # ========================================================
    # SCIENTIFIC STATUS
    # ========================================================

    def scientific_status(
        self,
    ) -> dict[str, Any]:

        return {
            "real_glacier_inventory": True,
            "rgi_version": "7.0",
            "mysql_backed": True,
            "synthetic_scientific_values": False,
            "glof_prediction_live": False,
            "hardware_live": False,
            "news_live": False,
        }

    # ========================================================
    # EMPTY RESPONSE
    # ========================================================

    def _empty_response(
        self,
    ) -> dict[str, Any]:

        return {
            "assistant": self.name,
            "version": self.VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "question": "",
            "intent": "EMPTY",
            "confidence": 1.0,
            "entities": {},
            "answer": (
                "Please ask me something about "
                "GLYAB, glaciers, glacial lakes, "
                "GLOF risk, AI or hardware."
            ),
            "context_used": False,
            "context": {},
            "scientific_status":
                self.scientific_status(),
        }


# ============================================================
# SINGLETON
# ============================================================

copilot = GLYABCopilot()


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def ask_glyab(
    question: str,
) -> dict[str, Any]:
    """
    Simple public interface for GLYAB Copilot.
    """

    return copilot.generate_response(question)
"""
GLYAB AI
Central API Router
"""

from fastapi import APIRouter

api_router = APIRouter()


# ============================================================
# GLOF ML PREDICTION
# ============================================================

try:
    from app.api.routes.predict import router as predict_router

    api_router.include_router(
        predict_router,
        prefix="/glof",
        tags=["GLOF Prediction"],
    )

except Exception as e:
    print(f"[WARNING] GLOF prediction route unavailable: {e}")


# ============================================================
# AI COPILOT
# ============================================================

try:
    from app.api.routes.copilot import router as copilot_router

    api_router.include_router(
        copilot_router,
        prefix="/copilot",
        tags=["AI Copilot"],
    )

except Exception as e:
    print(f"[WARNING] AI Copilot route unavailable: {e}")


# ============================================================
# API STATUS
# ============================================================

@api_router.get(
    "/status",
    tags=["System"],
)
async def api_status():

    return {
        "system": "GLYAB AI",
        "status": "online",
        "ml_engine": "available",
        "copilot": "available",
    }
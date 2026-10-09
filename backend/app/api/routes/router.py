"""
GLYAB AI
Central API Router

All API modules are registered here.
"""

from fastapi import APIRouter

from app.api.routes import copilot


# ============================================================
# MAIN API ROUTER
# ============================================================

api_router = APIRouter()


# ============================================================
# COPILOT
# ============================================================

api_router.include_router(
    copilot.router,
    prefix="/copilot",
    tags=["AI Copilot"],
)


# ============================================================
# SYSTEM ROUTE
# ============================================================

@api_router.get(
    "/status",
    tags=["System"],
)
async def api_status():
    return {
        "system": "GLYAB AI",
        "api": "online",
        "message": "GLYAB API is operational",
    }
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.copilot import copilot


router = APIRouter(
    prefix="/copilot",
    tags=["GLYAB AI Copilot"],
)


class CopilotRequest(BaseModel):
    message: str


@router.post("/chat")
def copilot_chat(request: CopilotRequest):
    """
    GLYAB AI Copilot chat endpoint.
    """

    result = copilot.generate_response(
        message=request.message
    )

    return result
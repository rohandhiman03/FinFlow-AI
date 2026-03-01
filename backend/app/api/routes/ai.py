from fastapi import APIRouter

from app.core.ai.factory import get_provider
from app.core.config import get_settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/providers")
def list_providers() -> dict[str, str | list[str]]:
    settings = get_settings()
    active = get_provider(settings)
    return {
        "active_provider": active.name,
        "supported_providers": list(settings.supported_ai_providers),
        "active_description": active.describe(),
    }

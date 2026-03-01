from fastapi import APIRouter

from app.core.ai.factory import get_provider
from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str | bool]:
    settings = get_settings()
    provider = get_provider(settings)
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
        "debug": settings.app_debug,
        "ai_provider": provider.name,
    }


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    # Lightweight readiness; DB init runs at startup.
    return {"status": "ready"}

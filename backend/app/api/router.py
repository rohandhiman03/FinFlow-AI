from fastapi import APIRouter

from app.api.routes import ai, health
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

router.include_router(health.router)
router.include_router(ai.router)

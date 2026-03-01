from fastapi import APIRouter

from app.api.routes import ai, health, onboarding, reports, statements, transactions
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

router.include_router(health.router)
router.include_router(ai.router)
router.include_router(onboarding.router)
router.include_router(transactions.router)
router.include_router(statements.router)
router.include_router(reports.router)

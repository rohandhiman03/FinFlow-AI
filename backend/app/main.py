from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import get_settings
from app.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, debug=settings.app_debug, lifespan=lifespan)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
    }

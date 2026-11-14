"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, model

api_router = APIRouter()
api_router.include_router(health.router, tags=["operations"])
api_router.include_router(model.router, tags=["model"])

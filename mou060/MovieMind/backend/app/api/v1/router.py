"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, model, movies

api_router = APIRouter()
api_router.include_router(health.router, tags=["operations"])
api_router.include_router(model.router, tags=["model"])
api_router.include_router(movies.router, tags=["movies"])

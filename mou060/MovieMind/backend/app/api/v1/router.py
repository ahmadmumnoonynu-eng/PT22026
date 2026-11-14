"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, model, movies, users

api_router = APIRouter()
api_router.include_router(health.router, tags=["operations"])
api_router.include_router(model.router, tags=["model"])
api_router.include_router(movies.router, tags=["movies"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(users.router, tags=["users"])

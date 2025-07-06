"""
API v1 router module.

This file aggregates all versioned API route modules into a single APIRouter,
making it easier to register them under a common prefix (e.g. /api/v1).
"""
from fastapi import APIRouter
from app.api import characters, starships, films


api_v1_router = APIRouter()
api_v1_router.include_router(characters.router, prefix="/characters", tags=["Characters"])
api_v1_router.include_router(starships.router, prefix="/starships", tags=["Starships"])
api_v1_router.include_router(films.router, prefix="/films", tags=["Films"])

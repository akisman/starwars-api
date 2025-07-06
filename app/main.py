"""
Main application entrypoint.

Initializes the FastAPI app and registers the API v1 router.
"""
from fastapi import FastAPI
from app.api.api_v1 import api_v1_router

app = FastAPI(title="Star Wars API", version="1.0")
app.include_router(api_v1_router, prefix="/api/v1")
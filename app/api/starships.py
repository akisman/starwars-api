"""
API routes for managing Star Wars starships.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.dependencies import enforce_json_content_type
from app.schemas.starship import PaginatedStarships, StarshipRead, StarshipCreate
from app.services.starship_service import get_starship, list_starships, create_starship


router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedStarships,
    summary="List all starships",
    description="Retrieve a paginated list of all starships in the database. Supports optional pagination with `skip` and `limit`, and `name` search."
)
def api_list_starships(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, le=100),
        name: str = Query(None, description="Search by name"),
        db: Session = Depends(get_db)
) -> PaginatedStarships:
    return list_starships(db, skip, limit, name)

@router.get(
    "/{starship_id}",
    response_model=StarshipRead,
    responses={
        404: {"description": "Character not found"},
    },
    summary="Get a starship by ID",
    description="Retrieve a single starship by their unique ID. Includes related characters and films if available."
)
def api_get_starship(starship_id: int, db: Session = Depends(get_db)) -> StarshipRead:
    return get_starship(db, starship_id)

@router.post(
    "/",
    response_model=StarshipRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_json_content_type)],
    summary="Create a new starship",
    description="Create a new starship with optional model, starship class, associated characters, and films. Returns the created starship object."
)
def api_create_starship(starship_in: StarshipCreate, db: Session = Depends(get_db)) -> StarshipRead:
    starship = create_starship(db, starship_in)
    return starship

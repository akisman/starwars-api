"""
API routes for managing Star Wars characters.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.dependencies import enforce_json_content_type
from app.schemas.character import PaginatedCharacters, CharacterRead, CharacterCreate
from app.services.character_service import create_character, list_characters, get_character


router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedCharacters,
    summary="List all characters",
    description="Retrieve a paginated list of all characters in the database. Supports optional pagination with `skip` and `limit`, and `name` search."
)
def api_list_characters(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(10, le=100, description="Maximum number of records to return"),
        name: str = Query(None, description="Search by name"),
        db: Session = Depends(get_db)
) -> PaginatedCharacters:
    return list_characters(db, skip, limit, name)

@router.get(
    "/{character_id}",
    response_model=CharacterRead,
    responses={
        404: {"description": "Character not found"},
    },
    summary="Get a character by ID",
    description="Retrieve a single character by their unique ID. Includes related films and starships if available."
)
def api_get_character(character_id: int, db: Session = Depends(get_db)) -> CharacterRead:
    return get_character(db, character_id)

@router.post(
    "/",
    response_model=CharacterRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_json_content_type)],
    summary="Create a new character",
    description="Create a new character with optional height, mass, associated films, and starships. Returns the created character object."
)
def api_create_character(character_in: CharacterCreate, db: Session = Depends(get_db)) -> CharacterRead:
    character = create_character(db, character_in)
    return character

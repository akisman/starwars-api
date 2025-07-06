"""
API routes for managing Star Wars films.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.dependencies import enforce_json_content_type
from app.schemas.film import PaginatedFilms, FilmRead, FilmCreate
from app.services.film_service import list_films, get_film, create_film


router = APIRouter()

@router.get(
    "/",
    response_model=PaginatedFilms,
    summary="List all films",
    description="Retrieve a paginated list of all films in the database. Supports optional pagination with `skip` and `limit`, and `title` search."
)
def api_list_films(
        skip: int = Query(0, ge=0),
        limit: int = Query(10, le=100),
        title: str = Query(None, description="Search by title"),
        db: Session = Depends(get_db)
) -> PaginatedFilms:
    return list_films(db, skip, limit, title)

@router.get(
    "/{film_id}",
    response_model=FilmRead,
    responses={
        404: {"description": "Character not found"},
    },
    summary="Get a film by ID",
    description="Retrieve a single film by their unique ID. Includes related characters and starships if available."
)
def api_get_films(film_id: int, db: Session = Depends(get_db)) -> FilmRead:
    return get_film(db, film_id)


@router.post(
    "/",
    response_model=FilmRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_json_content_type)],
    summary="Create a new film",
    description="Create a new film with optional opening, director, producer, release date, associated characters, and starships. Returns the created film object."
)
def api_create_film(film_in: FilmCreate, db: Session = Depends(get_db)):
    film = create_film(db, film_in)
    return film

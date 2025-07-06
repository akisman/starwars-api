"""
Service layer for Star Wars films.
Handles database logic for listing, retrieving, and creating films.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models import Film, Starship, Character
from app.schemas.film import FilmCreate


def list_films(db: Session, skip: int = 0, limit: int = 10, title: str | None = None):
    """
    Retrieve a paginated list of films, optionally filtered by title (case-insensitive).
    """
    query = db.query(Film).options(
        joinedload(Film.characters),
        joinedload(Film.starships)
    )
    if title:
        query = query.filter(func.lower(Film.title).ilike(f"%{title.lower()}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}

def get_film(db: Session, film_id: int) -> Film:
    """
    Retrieve a single film by ID, including related characters and starships.
    Raises 404 if not found.
    """
    film = (
        db.query(Film)
        .options(joinedload(Film.characters), joinedload(Film.starships))
        .filter(Film.id == film_id)
        .first()
    )
    if not film:
        raise HTTPException(status_code=404, detail="Film not found")
    return film

def create_film(db: Session, film_in: FilmCreate) -> Film:
    """
    Create a new film and associate it with existing characters and starships.
    Validates that all related character and starship IDs exist.
    """
    characters = db.query(Character).filter(Character.id.in_(film_in.character_ids)).all()
    if len(characters) != len(set(film_in.character_ids)):
        raise HTTPException(status_code=404, detail="One or more characters not found")

    starships = db.query(Starship).filter(Starship.id.in_(film_in.starship_ids)).all()
    if len(starships) != len(set(film_in.starship_ids)):
        raise HTTPException(status_code=404, detail="One or more starships not found")

    # Create and persist film
    film = Film(
        title=film_in.title,
        episode_id=film_in.episode_id,
        opening_crawl=film_in.opening_crawl,
        director=film_in.director,
        producer=film_in.producer,
        release_date=film_in.release_date,
        characters=characters,
        starships=starships
    )
    db.add(film)
    db.commit()
    db.refresh(film)
    return film

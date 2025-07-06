"""
Service layer for Star Wars starships.
Handles database logic for listing, retrieving, and creating starships.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models import Film, Starship, Character
from app.schemas.starship import StarshipCreate


def list_starships(db: Session, skip: int = 0, limit: int = 10, name: str | None = None):
    """
    Retrieve a paginated list of starship, optionally filtered by name (case-insensitive).
    """
    query = db.query(Starship).options(
        joinedload(Starship.films),
        joinedload(Starship.characters)
    )
    if name:
        query = query.filter(func.lower(Starship.name).ilike(f"%{name.lower()}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}

def get_starship(db: Session, starship_id: int) -> Starship:
    """
    Retrieve a single staship by ID, including related characters and films.
    Raises 404 if not found.
    """
    starship = (
        db.query(Starship)
        .options(joinedload(Starship.characters), joinedload(Starship.films))
        .filter(Starship.id == starship_id)
        .first()
    )
    if not starship:
        raise HTTPException(status_code=404, detail="Starship not found")
    return starship

def create_starship(db: Session, starship_in: StarshipCreate) -> Starship:
    """
    Create a new starship and associate it with existing films and characters.
    Validates that all related film and character IDs exist.
    """
    films = db.query(Film).filter(Film.id.in_(starship_in.film_ids)).all()
    if len(films) != len(set(starship_in.film_ids)):
        raise HTTPException(status_code=404, detail="One or more films not found")

    characters = db.query(Character).filter(Character.id.in_(starship_in.character_ids)).all()
    if len(characters) != len(set(starship_in.character_ids)):
        raise HTTPException(status_code=404, detail="One or more characters not found")

    # Create and persist starship
    starship = Starship(
        name=starship_in.name,
        model=starship_in.model,
        films=films,
        characters=characters
    )
    db.add(starship)
    db.commit()
    db.refresh(starship)
    return starship

"""
Service layer for Star Wars characters.
Handles database logic for listing, retrieving, and creating characters.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models import Film, Starship, Character
from app.schemas.character import CharacterCreate


def list_characters(db: Session, skip: int = 0, limit: int = 10, name: str | None = None):
    """
    Retrieve a paginated list of characters, optionally filtered by name (case-insensitive).
    """
    query = db.query(Character).options(
        joinedload(Character.films),
        joinedload(Character.starships)
    )
    if name:
        query = query.filter(func.lower(Character.name).ilike(f"%{name.lower()}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"total": total, "items": items}

def get_character(db: Session, character_id: int) -> Character:
    """
    Retrieve a single character by ID, including related films and starships.
    Raises 404 if not found.
    """
    character = (
        db.query(Character)
        .options(joinedload(Character.films), joinedload(Character.starships))
        .filter(Character.id == character_id)
        .first()
    )
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return character

def create_character(db: Session, character_in: CharacterCreate) -> Character:
    """
    Create a new character and associate it with existing films and starships.
    Validates that all related film and starship IDs exist.
    """
    films = db.query(Film).filter(Film.id.in_(character_in.film_ids)).all()
    if len(films) != len(set(character_in.film_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more films not found")

    starships = db.query(Starship).filter(Starship.id.in_(character_in.starship_ids)).all()
    if len(starships) != len(set(character_in.starship_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more starships not found")

    # Create and persist character
    character = Character(
        name=character_in.name,
        height=character_in.height,
        mass=character_in.mass,
        films=films,
        starships=starships
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    return character

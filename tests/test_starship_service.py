import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Film, Character
from app.schemas.starship import StarshipCreate
from app.services.starship_service import create_starship, get_starship, list_starships


@pytest.fixture
def sample_characters(db: Session):
    character1 = Character(id=1, name="John Doe")
    character2 = Character(id=2, name="Jane Doe")
    db.add_all([character1, character2])
    db.commit()
    return [character1, character2]

@pytest.fixture
def sample_films(db: Session):
    film1 = Film(id=1, title="Film 1", episode_id=4)
    film2 = Film(id=2, title="Film 2", episode_id=5)
    db.add_all([film1, film2])
    db.commit()
    return [film1, film2]

def make_starship_data(**overrides) -> dict:
    base_data = {
        "name": "Test Starship",
        "model": "Test Model",
        "character_ids": [],
        "film_ids": []
    }
    base_data.update(overrides)
    return base_data

def test_create_starship_success(db: Session, sample_films, sample_characters):
    starship_in = StarshipCreate(**make_starship_data(
        film_ids=[f.id for f in sample_films],
        character_ids=[c.id for c in sample_characters]
    ))
    starship = create_starship(db, starship_in)

    assert starship.id is not None
    assert starship.name == "Test Starship"
    assert len(starship.films) == 2
    assert len(starship.characters) == 2

def test_create_starship_film_not_found(db: Session, sample_characters):
    starship_in = StarshipCreate(**make_starship_data(
        film_ids=[999],  # Nonexistent Film
        character_ids=[c.id for c in sample_characters]
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_starship(db, starship_in)

    assert exc_info.value.status_code == 404
    assert "films" in exc_info.value.detail.lower()

def test_create_starship_character_not_found(db: Session, sample_films):
    starship_in = StarshipCreate(**make_starship_data(
        film_ids=[f.id for f in sample_films],
        character_ids=[999],  # Nonexistent Character
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_starship(db, starship_in)

    assert exc_info.value.status_code == 404
    assert "characters" in exc_info.value.detail.lower()

def test_get_starship_success(db: Session, sample_films, sample_characters):
    starship_in = StarshipCreate(**make_starship_data(
        film_ids=[f.id for f in sample_films],
        character_ids=[c.id for c in sample_characters]
    ))
    created = create_starship(db, starship_in)

    fetched = get_starship(db, created.id)

    assert fetched.id == created.id
    assert fetched.name == "Test Starship"

def test_get_starship_not_found(db: Session):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_starship(db, 999999)
    assert exc_info.value.status_code == 404

def test_list_starships(db: Session):
    StarshipCreate(**make_starship_data())
    result = list_starships(db)
    assert "total" in result
    assert "items" in result
    assert isinstance(result["items"], list)

def test_list_starships_with_name_filter(db: Session):
    # Create starships
    create_starship(db, StarshipCreate(**make_starship_data(name="John Doe Starship")))
    create_starship(db, StarshipCreate(**make_starship_data(name="Jane Doe Starship")))

    # Search for 'John'
    result = list_starships(db, name="john")
    assert result["total"] == 1
    assert result["items"][0].name == "John Doe Starship"

    # Search for 'Jane'
    result = list_starships(db, name="jane")
    assert result["total"] == 1
    assert result["items"][0].name == "Jane Doe Starship"

    # Search for both 'John' and 'Jane' Doe
    result = list_starships(db, name="doe")
    assert result["total"] == 2

    # Search for something nonexistent
    result = list_starships(db, name="Noone")
    assert result["total"] == 0
    assert result["items"] == []

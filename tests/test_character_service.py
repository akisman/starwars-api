import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Film, Starship
from app.schemas.character import CharacterCreate
from app.services.character_service import list_characters, get_character, create_character


@pytest.fixture
def sample_films(db: Session):
    film1 = Film(id=1, title="Film 1", episode_id=4)
    film2 = Film(id=2, title="Film 2", episode_id=5)
    db.add_all([film1, film2])
    db.commit()
    return [film1, film2]

@pytest.fixture
def sample_starships(db: Session):
    starship1 = Starship(id=1, name="Starship 1")
    starship2 = Starship(id=2, name="Starship 2")
    db.add_all([starship1, starship2])
    db.commit()
    return [starship1, starship2]

def make_character_data(**overrides) -> dict:
    base_data = {
        "name": "Test Character",
        "height": "172",
        "mass": "77",
        "film_ids": [],
        "starship_ids": [],
    }
    base_data.update(overrides)
    return base_data

def test_create_character_success(db: Session, sample_films, sample_starships):
    character_in = CharacterCreate(**make_character_data(
        film_ids=[f.id for f in sample_films],
        starship_ids=[s.id for s in sample_starships]
    ))
    character = create_character(db, character_in)

    assert character.id is not None
    assert character.name == "Test Character"
    assert len(character.films) == 2
    assert len(character.starships) == 2

def test_create_character_film_not_found(db: Session, sample_starships):
    character_in = CharacterCreate(**make_character_data(
        film_ids=[999],  # Nonexistent Film
        starship_ids=[s.id for s in sample_starships]
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_character(db, character_in)

    assert exc_info.value.status_code == 404
    assert "films" in exc_info.value.detail.lower()

def test_create_character_starship_not_found(db: Session, sample_films):
    character_in = CharacterCreate(**make_character_data(
        film_ids=[f.id for f in sample_films],
        starship_ids=[999],  # Nonexistent Starship
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_character(db, character_in)

    assert exc_info.value.status_code == 404
    assert "starships" in exc_info.value.detail.lower()

def test_get_character_success(db: Session, sample_films, sample_starships):
    character_in = CharacterCreate(**make_character_data(
        film_ids=[f.id for f in sample_films],
        starship_ids=[s.id for s in sample_starships]
    ))
    created = create_character(db, character_in)

    fetched = get_character(db, created.id)

    assert fetched.id == created.id
    assert fetched.name == "Test Character"

def test_get_character_not_found(db: Session):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_character(db, 999999)
    assert exc_info.value.status_code == 404

def test_list_characters(db: Session):
    CharacterCreate(**make_character_data())
    result = list_characters(db)
    assert "total" in result
    assert "items" in result
    assert isinstance(result["items"], list)

def test_list_characters_with_name_filter(db: Session):
    # Create characters
    create_character(db, CharacterCreate(**make_character_data(name="John Doe")))
    create_character(db, CharacterCreate(**make_character_data(name="Jane Doe")))

    # Search for 'John'
    result = list_characters(db, name="john")
    assert result["total"] == 1
    assert result["items"][0].name == "John Doe"

    # Search for 'Jane'
    result = list_characters(db, name="jane")
    assert result["total"] == 1
    assert result["items"][0].name == "Jane Doe"

    # Search for both 'John' and 'Jane' Doe
    result = list_characters(db, name="doe")
    assert result["total"] == 2

    # Search for something nonexistent
    result = list_characters(db, name="Noone")
    assert result["total"] == 0
    assert result["items"] == []

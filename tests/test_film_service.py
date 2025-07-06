import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.film import FilmCreate
from app.models import Character, Starship
from app.services.film_service import create_film, get_film, list_films


@pytest.fixture
def sample_characters(db: Session):
    character1 = Character(id=1, name="John Doe")
    character2 = Character(id=2, name="Jane Doe")
    db.add_all([character1, character2])
    db.commit()
    return [character1, character2]

@pytest.fixture
def sample_starships(db: Session):
    starship1 = Starship(id=1, name="Starship 1")
    starship2 = Starship(id=2, name="Starship 2")
    db.add_all([starship1, starship2])
    db.commit()
    return [starship1, starship2]

def make_film_data(**overrides) -> dict:
    base_data = {
        "title": "Test Film",
        "episode_id": 10,
        "opening_crawl": "Test Crawl",
        "director": "Test Director",
        "producer": "Test Producer",
        "release_date": "2025-07-05",
        "character_ids": [],
        "starship_ids": []
    }
    base_data.update(overrides)
    return base_data

def test_create_film_success(db: Session, sample_characters, sample_starships):
    film_in = FilmCreate(**make_film_data(
        character_ids=[c.id for c in sample_characters],
        starship_ids=[s.id for s in sample_starships]
    ))
    film = create_film(db, film_in)

    assert film.id is not None
    assert film.title == "Test Film"
    assert len(film.characters) == 2
    assert len(film.starships) == 2

def test_create_film_character_not_found(db: Session, sample_starships):
    film_in = FilmCreate(**make_film_data(
        character_ids=[999],  # Nonexistent Character
        starship_ids=[s.id for s in sample_starships]
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_film(db, film_in)

    assert exc_info.value.status_code == 404
    assert "characters" in exc_info.value.detail.lower()

def test_create_film_starship_not_found(db: Session, sample_characters):
    film_in = FilmCreate(**make_film_data(
        character_ids=[c.id for c in sample_characters],
        starship_ids=[999]  # Nonexistent Starship
    ))

    with pytest.raises(HTTPException) as exc_info:
        create_film(db, film_in)

    assert exc_info.value.status_code == 404
    assert "starships" in exc_info.value.detail.lower()

def test_get_film_success(db: Session, sample_characters, sample_starships):
    film_in = FilmCreate(**make_film_data(
        character_ids=[c.id for c in sample_characters],
        starship_ids=[s.id for s in sample_starships]
    ))
    created = create_film(db, film_in)

    fetched = get_film(db, created.id)

    assert fetched.id == created.id
    assert fetched.title == "Test Film"

def test_get_character_not_found(db: Session):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        get_film(db, 999999)
    assert exc_info.value.status_code == 404

def test_list_films(db: Session):
    FilmCreate(**make_film_data())
    result = list_films(db)
    assert "total" in result
    assert "items" in result
    assert isinstance(result["items"], list)

def test_list_films_with_title_filter(db: Session):
    # Create films
    create_film(db, FilmCreate(**make_film_data(title="John Doe Film")))
    create_film(db, FilmCreate(**make_film_data(title="Jane Doe Film")))

    # Search for 'John'
    result = list_films(db, title="john")
    assert result["total"] == 1
    assert result["items"][0].title == "John Doe Film"

    # Search for 'Jane'
    result = list_films(db, title="jane")
    assert result["total"] == 1
    assert result["items"][0].title == "Jane Doe Film"

    # Search for both 'John' and 'Jane' Doe
    result = list_films(db, title="doe")
    assert result["total"] == 2

    # Search for something nonexistent
    result = list_films(db, title="Noone")
    assert result["total"] == 0
    assert result["items"] == []

import pytest
from unittest.mock import AsyncMock, patch
from app.cli import sync_films_logic, sync_starships_logic, sync_characters_logic
from app.models import Film, Starship, Character


@pytest.mark.asyncio
@patch("app.cli.fetch_films", new_callable=AsyncMock)
async def test_sync_films_logic(mock_fetch, db):
    mock_fetch.return_value = [
        {
            "url": "https://swapi.info/api/films/1/",
            "title": "A New Hope",
            "episode_id": 4,
            "opening_crawl": "It is a period of civil war...",
            "producer": "Gary Kurtz",
            "director": "George Lucas",
            "release_date": "1977-05-25"
        }
    ]
    await sync_films_logic(db)
    film = db.query(Film).filter_by(id=1).first()
    assert film is not None
    assert film.title == "A New Hope"

@pytest.mark.asyncio
@patch("app.cli.fetch_starships", new_callable=AsyncMock)
@patch("app.cli.fetch_films", new_callable=AsyncMock)
async def test_sync_starships_logic(mock_films, mock_starships, db):
    mock_films.return_value = [{
        "url": "https://swapi.info/api/films/1/",
        "title": "A New Hope",
        "episode_id": 4,
        "opening_crawl": "...",
        "producer": "Gary Kurtz",
        "director": "George Lucas",
        "release_date": "1977-05-25"
    }]
    await sync_films_logic(db)

    mock_starships.return_value = [
        {
            "url": "https://swapi.info/api/starships/9/",
            "name": "Death Star",
            "model": "DS-1 Orbital Battle Station",
            "starship_class": "Deep Space Mobile Battlestation",
            "films": ["https://swapi.info/api/films/1/"]
        }
    ]
    await sync_starships_logic(db)
    starship = db.query(Starship).filter_by(id=9).first()
    assert starship is not None
    assert starship.name == "Death Star"
    assert len(starship.films) == 1

@pytest.mark.asyncio
@patch("app.cli.fetch_characters", new_callable=AsyncMock)
@patch("app.cli.fetch_starships", new_callable=AsyncMock)
@patch("app.cli.fetch_films", new_callable=AsyncMock)
async def test_sync_characters_logic(mock_films, mock_starships, mock_characters, db):
    mock_films.return_value = [{
        "url": "https://swapi.info/api/films/1/",
        "title": "A New Hope",
        "episode_id": 4,
        "opening_crawl": "...",
        "producer": "Gary Kurtz",
        "director": "George Lucas",
        "release_date": "1977-05-25"
    }]
    mock_starships.return_value = [{
        "url": "https://swapi.info/api/starships/9/",
        "name": "X-Wing",
        "model": "T-65 X-wing",
        "starship_class": "Starfighter",
        "films": ["https://swapi.info/api/films/1/"]
    }]
    mock_characters.return_value = [{
        "url": "https://swapi.info/api/people/1/",
        "name": "Luke Skywalker",
        "height": "172",
        "mass": "77",
        "films": ["https://swapi.info/api/films/1/"],
        "starships": ["https://swapi.info/api/starships/9/"]
    }]

    # Pre-sync films and starships (since characters link to them)
    await sync_films_logic(db)
    await sync_starships_logic(db)
    await sync_characters_logic(db)

    character = db.query(Character).filter_by(id=1).first()
    assert character is not None
    assert character.name == "Luke Skywalker"
    assert len(character.films) == 1
    assert len(character.starships) == 1

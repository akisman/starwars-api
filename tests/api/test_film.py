import pytest
from fastapi.testclient import TestClient
from app.models import Starship, Character


@pytest.fixture
def setup_test_data(db):
    # Create characters
    character1 = Character(id=1, name="John Doe")
    character2 = Character(id=2, name="Jane Doe")
    db.add_all([character1, character2])

    # Create starships
    starship1 = Starship(id=1, name="Starship 1")
    starship2 = Starship(id=2, name="Starship 2")
    db.add_all([starship1, starship2])
    db.commit()
    yield

def test_create_film_api_success(client: TestClient, setup_test_data):
    payload = {
        "title": "Yet Another Star Wars Movie",
        "episode_id": 50,
        "producer": "George Lucas",
        "director": "George Lucas",
        "release_date": "2025-07-06",
        "character_ids": [1, 2],
        "starship_ids": [1, 2]
    }
    response = client.post("/api/v1/films/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Yet Another Star Wars Movie"
    assert len(data["characters"]) == 2
    assert len(data["starships"]) == 2

def test_create_film_api_character_not_found(client: TestClient, setup_test_data):
    payload = {
        "title": "Yet Another Star Wars Movie",
        "episode_id": 50,
        "producer": "George Lucas",
        "director": "George Lucas",
        "release_date": "2025-07-06",
        "character_ids": [999],
        "starship_ids": [1, 2]
    }
    response = client.post("/api/v1/films/", json=payload)
    assert response.status_code == 404
    assert "characters" in response.json()["detail"].lower()

def test_get_film_api(client: TestClient, setup_test_data):
    payload = {
        "title": "Yet Another Star Wars Movie",
        "episode_id": 50,
        "producer": "George Lucas",
        "director": "George Lucas",
        "release_date": "2025-07-06",
        "character_ids": [1, 2],
        "starship_ids": [1, 2]
    }
    create_resp = client.post("/api/v1/films/", json=payload)
    assert create_resp.status_code == 201
    film_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/films/{film_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Yet Another Star Wars Movie"

def test_list_films_api(client: TestClient, setup_test_data):
    payload = {
        "title": "Yet Another Star Wars Movie",
        "episode_id": 50,
        "producer": "George Lucas",
        "director": "George Lucas",
        "release_date": "2025-07-06",
        "character_ids": [1, 2],
        "starship_ids": [1, 2]
    }
    create_resp = client.post("/api/v1/films/", json=payload)
    assert create_resp.status_code == 201

    response = client.get("/api/v1/films/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

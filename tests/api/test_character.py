import pytest
from fastapi.testclient import TestClient
from app.models import Film, Starship


@pytest.fixture
def setup_test_data(db):
    # Create films
    film1 = Film(id=1, title="Film 1", episode_id=4)
    film2 = Film(id=2, title="Film 2", episode_id=5)
    db.add_all([film1, film2])

    # Create starships
    starship1 = Starship(id=1, name="Starship 1")
    starship2 = Starship(id=2, name="Starship 2")
    db.add_all([starship1, starship2])
    db.commit()
    yield

def test_create_character_api_success(client: TestClient, setup_test_data):
    payload = {
        "name": "API Test Character",
        "height": "172",
        "mass": "77",
        "film_ids": [1, 2],
        "starship_ids": [1, 2]
    }
    response = client.post("/api/v1/characters/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test Character"
    assert len(data["films"]) == 2
    assert len(data["starships"]) == 2

def test_create_character_api_film_not_found(client: TestClient, setup_test_data):
    payload = {
        "name": "API Test Character",
        "height": "150",
        "mass": "49",
        "film_ids": [999],  # Invalid
        "starship_ids": [1]
    }
    response = client.post("/api/v1/characters/", json=payload)
    assert response.status_code == 404
    assert "films" in response.json()["detail"].lower()

def test_get_character_api(client: TestClient, setup_test_data):
    payload = {
        "name": "API Test Character",
        "height": "180",
        "mass": "85",
        "film_ids": [1],
        "starship_ids": [2]
    }
    create_resp = client.post("/api/v1/characters/", json=payload)
    assert create_resp.status_code == 201
    character_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/characters/{character_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Test Character"

def test_list_characters_api(client: TestClient, setup_test_data):
    payload = {
        "name": "API Test Character",
        "height": "150",
        "mass": "49",
        "film_ids": [1],
        "starship_ids": [1]
    }
    create_resp = client.post("/api/v1/characters/", json=payload)
    assert create_resp.status_code == 201

    response = client.get("/api/v1/characters/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) >= 1

# FastAPI Star Wars Backend

A simple FastAPI backend for managing Star Wars characters, films, and starships.
It syncs data from the external [SWAPI](https://swapi.info/) and exposes a RESTful API for interacting with that data locally.

---

## Project Structure

```
├── app
│   ├── api/                # FastAPI route handlers by resource
│   ├── cli.py              # CLI commands for DB initialization & data syncing
│   ├── db/                 # Database session and dependency injection
│   ├── main.py             # FastAPI app entrypoint
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic models for request/response validation
│   └── services/           # Business logic & external API client
├── tests/                  # Test suite organized by feature
├── Dockerfile              # Docker container config (optional)
├── requirements.txt        # Python dependencies
└── README.md               # This documentation
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. Create and activate a virtual environment:

    ```bash
   python -m venv venv
   source /venv/bin/activate
    ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Initialize Database

Create database tables. Use `--drop` to reset:

```bash
python -m app.cli init-db
# or to drop existing tables:
python -m app.cli init-db --drop
```

### Sync Data from SWAPI

Fetch and store films, characters, and starships from the external Star Wars API:

```bash
python -m app.cli sync-all
```

### Run Development Server

Start FastAPI with hot-reload for local development with:

```bash
fastapi dev app/main.py
```

or:

```bash
uvicorn app.main:app --reload
```

API will be available at `http://localhost:8000` and the Swagger documentation at `http://localhost:8000/docs`.

---

## Testing

Run the test suite with coverage reporting:

```bash
pytest --cov=app tests/
```

Generate an HTML coverage report:

```bash
pytest --cov=app --cov-report=html tests/
```

Open `htmlcov/index.html` in your browser to see detailed coverage.

---

## API Endpoints

* `/api/v1/characters/` — Star Wars characters 
* `/api/v1/films/` — Star Wars films
* `/api/v1/starships/` — Star Wars starships

All three resource endpoints support:

* **Search** by `name` (characters, starships) or `title` (films)
* **Pagination** using the query parameters:

  * `skip`: how many results to skip (default: `0`)
  * `limit`: max number of results to return (default: `10`)

### Examples:

* `/api/v1/characters?name=luke`
* `/api/v1/films?title=hope&skip=10&limit=5`
* `/api/v1/starships?name=death&limit=3`

(Refer to the Swagger documentation at `http://localhost:8000/docs` for additional details and examples)

### Example Usage

#### Get all characters

```http
GET http://localhost:8000/api/v1/characters
```

#### Get a specific character

```http
GET http://localhost:8000/api/v1/characters/1
```

#### Search for a film by title

```http
GET http://localhost:8000/api/v1/films?title=hope
```

#### Get paginated starships (e.g. skip 5, limit to 10)

```http
GET http://localhost:8000/api/v1/starships?skip=5&limit=10
```

#### Create a new film

```http
POST http://localhost:8000/api/v1/films/
Content-Type: application/json

{
  "title": "Best Movie",
  "episode_id": 7,
  "opening_crawl": "Something",
  "director": "Akis",
  "producer": "Bob",
  "release_date": "2024-10-10",
  "character_ids": [1],
  "starship_ids": [12]
}
```

---

## Docker Support

This project includes a `Dockerfile` that can be used to build a production-ready image.

### Build the Docker Image

```bash
docker build -t starwars-api .
```

### Example Docker Compose (with Reverse Proxy)

You can easily integrate this app behind a reverse proxy in a `docker-compose.yml` environment. Example with Caddy serving as a reverse proxy with automatic SSL:

```yaml
version: '3.8'

services:
  starwars-api:
    image: starwars-api
    restart: unless-stopped
    depends_on:
      - reverse-proxy
    networks:
      - app-network

  reverse-proxy:
    image: caddy:2.8.4-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/caddy/Caddyfile:/etc/caddy/Caddyfile
    networks:
      - app-network

networks:
  app-network:
```

## License

This project is licensed under the [MIT License](LICENSE).


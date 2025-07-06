"""
CLI tool for initializing the database and syncing data from SWAPI.

Usage:
    python -m app.cli init-db [--drop]
    python -m app.cli sync-all
"""
import asyncio
import typer
from app.db.session import Base, engine, SessionLocal
from app.models import Character
from app.models.film import Film
from app.models.starship import Starship
from app.services.swapi_client import fetch_characters, fetch_films, fetch_starships

cli = typer.Typer()

@cli.command()
def init_db(drop: bool = typer.Option(False, "--drop", help="Drop existing tables before creating")) -> None:
    """
    Initialize the database schema.
    Use --drop to reset the database before creating tables.
    """
    if drop:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database initialized" + (" (dropped and recreated)" if drop else ""))

def extract_id_from_url(url: str) -> int:
    """
    Extract the numeric ID from a SWAPI resource URL.
    Example: "https://swapi.info/api/films/1/" → 1
    """
    return int(url.rstrip("/").split("/")[-1])

async def sync_films_logic(db) -> None:
    """
    Fetch and store films from SWAPI.
    If the film already exists, it is updated.
    """
    films = await fetch_films()
    for film in films:
        film_id = extract_id_from_url(film["url"])
        existing = db.query(Film).filter_by(id=film_id).first()
        if existing:
            existing.title = film["title"]
            existing.episode_id = film["episode_id"]
            existing.opening_crawl = film["opening_crawl"]
            existing.producer = film["producer"]
            existing.director = film["director"]
            existing.release_date = film["release_date"]
        else:
            db.add(Film(
                id=film_id,
                title=film["title"],
                episode_id=film["episode_id"],
                opening_crawl=film["opening_crawl"],
                producer=film["producer"],
                director=film["director"],
                release_date=film["release_date"]
            ))
    db.commit()

async def sync_starships_logic(db) -> None:
    """
    Fetch and store starships from SWAPI, including related films.
    """
    starships = await fetch_starships()
    for s in starships:
        starship_id = extract_id_from_url(s["url"])
        existing = db.query(Starship).filter_by(id=starship_id).first()

        if existing:
            existing.name = s["name"]
            existing.model = s["model"]
            existing.starship_class = s["starship_class"]
            starship_obj = existing
        else:
            starship_obj = Starship(
                id=starship_id,
                name=s["name"],
                model=s["model"],
                starship_class=s["starship_class"]
            )
            db.add(starship_obj)
            db.commit()
            db.refresh(starship_obj)

        # Link to Films
        films = []
        for film_url in s.get("films", []):
            film_id = extract_id_from_url(film_url)
            film = db.query(Film).filter_by(id=film_id).first()
            if film:
                films.append(film)
        starship_obj.films = films
    db.commit()


async def sync_characters_logic(db) -> None:
    """
    Fetch and store characters from SWAPI, including related films and starships.
    """
    characters = await fetch_characters()
    for c in characters:
        char_id = extract_id_from_url(c["url"])
        existing = db.query(Character).filter_by(id=char_id).first()

        if existing:
            existing.name = c["name"]
            existing.height = c["height"]
            existing.mass = c["mass"]
            char_obj = existing
        else:
            char_obj = Character(
                id=char_id,
                name=c["name"],
                height=c["height"],
                mass=c["mass"]
            )
            db.add(char_obj)
            db.commit()
            db.refresh(char_obj)

        # Link to Films
        films = []
        for film_url in c.get("films", []):
            film_id = extract_id_from_url(film_url)
            film = db.query(Film).filter_by(id=film_id).first()
            if film:
                films.append(film)
        char_obj.films = films

        # Link to Starships
        starships = []
        for starship_url in c.get("starships", []):
            starship_id = extract_id_from_url(starship_url)
            starship = db.query(Starship).filter_by(id=starship_id).first()
            if starship:
                starships.append(starship)
        char_obj.starships = starships
    db.commit()

@cli.command()
def sync_all():
    """
    Sync films, starships, and characters from SWAPI into the local database.
    """
    db = SessionLocal()
    asyncio.run(sync_films_logic(db))
    asyncio.run(sync_starships_logic(db))
    asyncio.run(sync_characters_logic(db))
    db.close()
    print("All data synced")

if __name__ == "__main__":
    cli()

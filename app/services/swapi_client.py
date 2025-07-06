"""
Client module for fetching data from the external SWAPI (https://swapi.info/api).
Handles asynchronous retrieval of films, starships, and characters.
"""
import httpx

BASE_URL = "https://swapi.info/api"

async def fetch_films():
    """
    Fetch all films from SWAPI.
    """
    return await fetch_all("films")

async def fetch_starships():
    """
    Fetch all starships from SWAPI.
    """
    return await fetch_all("starships")

async def fetch_characters():
    """
    Fetch all characters (people) from SWAPI.
    """
    return await fetch_all("people")

async def fetch_all(resource: str):
    """
    Generic SWAPI fetcher for a given resource.
    Raises an error if the response is not a list.
    """
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/{resource}")
        res.raise_for_status()
        data = res.json()
        if not isinstance(data, list):
            raise ValueError(f"Expected a list from SWAPI, got: {type(data)} — {data}")
        return data

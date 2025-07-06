import pytest
from httpx import Response, Request, HTTPStatusError
from app.services import swapi_client


@pytest.mark.asyncio
async def test_fetch_all_success(monkeypatch):
    # Simulate a successful HTTP response returning a list of characters
    class MockResponse:
        def raise_for_status(self):
            # Simulate no HTTP error (status is 200)
            pass
        def json(self):
            # Return a valid list (the expected format)
            return [{"name": "Luke Skywalker"}]

    # Simulate an httpx.AsyncClient instance
    class MockClient:
        async def __aenter__(self):
            return self  # So it works with `async with`
        async def __aexit__(self, *args):
            pass
        async def get(self, url):
            return MockResponse()  # Return the mock response above

    # Replace `httpx.AsyncClient` inside the `swapi_client` module with our mock
    monkeypatch.setattr(swapi_client.httpx, "AsyncClient", lambda: MockClient())

    # Call the function under test
    data = await swapi_client.fetch_all("people")

    assert isinstance(data, list)
    assert data[0]["name"] == "Luke Skywalker"

@pytest.mark.asyncio
async def test_fetch_all_raises_for_status(monkeypatch):
    class MockResponse:
        def raise_for_status(self): raise HTTPStatusError("error", request=Request("GET", "url"), response=Response(400))
        def json(self): return []

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url): return MockResponse()

    monkeypatch.setattr(swapi_client.httpx, "AsyncClient", lambda: MockClient())

    with pytest.raises(HTTPStatusError):
        await swapi_client.fetch_all("films")

@pytest.mark.asyncio
async def test_fetch_all_returns_non_list(monkeypatch):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self): return {"message": "Not a list"}

    class MockClient:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, url): return MockResponse()

    monkeypatch.setattr(swapi_client.httpx, "AsyncClient", lambda: MockClient())

    with pytest.raises(ValueError, match="Expected a list from SWAPI"):
        await swapi_client.fetch_all("people")

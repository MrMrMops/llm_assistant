# tests/conftest.py
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from httpx import ASGITransport

@pytest_asyncio.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

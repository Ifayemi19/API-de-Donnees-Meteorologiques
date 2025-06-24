import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport
from jsonschema import validate

# 🔧 Chemin vers la racine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from main import app
from app.schemas.weather_schema import weather_response_schema

@pytest.mark.asyncio
async def test_contract_weather_response():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/weather/current/Paris")
        assert response.status_code == 200

        data = response.json()
        validate(instance=data, schema=weather_response_schema)

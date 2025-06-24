import sys
import os
import pytest
from httpx import AsyncClient, ASGITransport

# Ajouter le chemin vers le dossier racine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from main import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_get_current_weather():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/current/Paris")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"
        assert "temperature" in data
        assert "current" in data["temperature"]

@pytest.mark.asyncio
async def test_city_not_found():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/current/FakeCity")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_missing_city():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/current/")
        assert response.status_code == 404  # URL incomplète

@pytest.mark.asyncio
async def test_forecast_weather():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/forecast/Paris")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"
        assert "forecast" in data

@pytest.mark.asyncio
async def test_historical_weather():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/history/Paris")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "Paris"
        assert "history" in data

@pytest.mark.asyncio
async def test_sources_aggregation():
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/weather/current/Paris")
        assert response.status_code == 200
        data = response.json()

        # Vérifie la présence de la clé 'sources'
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "open-meteo" in data["sources"]
        assert "openweather" in data["sources"]

        # Vérifie que la température est bien présente
        assert "temperature" in data
        assert "current" in data["temperature"]
        assert isinstance(data["temperature"]["current"], (int, float))

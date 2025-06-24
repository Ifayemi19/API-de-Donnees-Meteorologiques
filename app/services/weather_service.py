import httpx
import os
import asyncio
from datetime import datetime, timedelta

# Coordonnées de quelques villes en dur (pour test)
city_coords = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "New York": {"lat": 40.7128, "lon": -74.0060}
}

def get_coordinates(city: str):
    return city_coords.get(city)

# 🔸 OpenWeatherMap
async def get_openweathermap_data(city: str):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    return {
        "source": "openweather",
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }

# 🔹 Open-Meteo (extrait uniquement pour usage dans l’agrégation)
async def get_open_meteo_data(coords: dict, city: str):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current_weather": True
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    if "current_weather" not in data:
        return None

    return {
        "source": "open-meteo",
        "temperature": data["current_weather"]["temperature"],
        "humidity": None,
        "description": None,
        "timestamp": data["current_weather"]["time"]
    }

# 🔹 1. Météo actuelle agrégée
async def get_current_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None  # Ville non supportée

    # Appels parallèles aux deux services météo
    results = await asyncio.gather(
        get_open_meteo_data(coords, city),
        get_openweathermap_data(city),
        return_exceptions=True
    )

    valid_results = [r for r in results if isinstance(r, dict)]

    if not valid_results:
        return None

    # Moyenne de température entre les sources valides
    avg_temp = sum(r["temperature"] for r in valid_results) / len(valid_results)
    sources = [r["source"] for r in valid_results]

    return {
        "city": city,
        "temperature": {
            "current": round(avg_temp, 1),
            "unit": "celsius"
        },
        "sources": sources
    }

# 🔹 2. Prévisions sur 5 jours
async def get_forecast_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": ["temperature_2m_min", "temperature_2m_max"],
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    if "daily" not in data or "time" not in data["daily"]:
        return None

    forecast = []
    for i in range(len(data["daily"]["time"])):
        forecast.append({
            "date": data["daily"]["time"][i],
            "temp_min": data["daily"]["temperature_2m_min"][i],
            "temp_max": data["daily"]["temperature_2m_max"][i]
        })

    return {
        "city": city,
        "forecast": forecast
    }

# 🔹 3. Historique sur 5 jours précédents
async def get_historical_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=5)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": str(start_date),
        "end_date": str(end_date),
        "daily": ["temperature_2m_min", "temperature_2m_max"],
        "timezone": "auto"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    if "daily" not in data or "time" not in data["daily"]:
        return None

    history = []
    for i in range(len(data["daily"]["time"])):
        history.append({
            "date": data["daily"]["time"][i],
            "temp_min": data["daily"]["temperature_2m_min"][i],
            "temp_max": data["daily"]["temperature_2m_max"][i]
        })

    return {
        "city": city,
        "history": history
    }

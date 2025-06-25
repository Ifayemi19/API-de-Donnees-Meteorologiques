import httpx
import os
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache

# Coordonnées de quelques villes en dur
city_coords = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "New York": {"lat": 40.7128, "lon": -74.0060}
}

@lru_cache(maxsize=100)
def get_coordinates(city: str):
    return city_coords.get(city)

# Cache local en mémoire pour les résultats API
temp_cache = {}
CACHE_TTL_SECONDS = 60  # Durée de vie des données en cache

def is_cache_valid(entry):
    return datetime.now() < entry['expiry']

def get_from_cache(key):
    entry = temp_cache.get(key)
    return entry['value'] if entry and is_cache_valid(entry) else None

def set_to_cache(key, value):
    temp_cache[key] = {
        'value': value,
        'expiry': datetime.now() + timedelta(seconds=CACHE_TTL_SECONDS)
    }

# ----------------------------- SERVICES -----------------------------

async def get_openweathermap_data(city: str):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None

    cache_key = f"openweathermap::{city}"
    cached = get_from_cache(cache_key)
    if cached:
        return cached

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    result = {
        "source": "openweather",
        "temperature": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "description": data.get("weather", [{}])[0].get("description")
    }
    set_to_cache(cache_key, result)
    return result


async def get_open_meteo_data(coords: dict, city: str):
    cache_key = f"openmeteo::{city}"
    cached = get_from_cache(cache_key)
    if cached:
        return cached

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

    current = data.get("current_weather")
    if not current or current.get("temperature") is None:
        return None

    result = {
        "source": "open-meteo",
        "temperature": current["temperature"],
        "humidity": None,
        "description": None,
        "timestamp": current.get("time"),
        "wind_speed": current.get("windspeed")
    }
    set_to_cache(cache_key, result)
    return result


async def get_current_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None

    results = await asyncio.gather(
        get_open_meteo_data(coords, city),
        get_openweathermap_data(city),
        return_exceptions=True
    )

    valid_results = [r for r in results if isinstance(r, dict) and r.get("temperature") is not None]
    if not valid_results:
        return None

    avg_temp = sum(r["temperature"] for r in valid_results) / len(valid_results)
    sources = [r["source"] for r in valid_results]
    base = valid_results[0]

    return {
        "city": city,
        "temperature": {
            "current": round(avg_temp, 1),
            "unit": "celsius"
        },
        "sources": sources,
        "timestamp": base.get("timestamp"),
        "wind_speed": base.get("wind_speed")
    }


async def get_forecast_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None

    cache_key = f"forecast::{city}"
    cached = get_from_cache(cache_key)
    if cached:
        return cached

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
        min_temp = data["daily"]["temperature_2m_min"][i]
        max_temp = data["daily"]["temperature_2m_max"][i]

        if min_temp is None or max_temp is None:
            continue

        forecast.append({
            "date": data["daily"]["time"][i],
            "temp_min": min_temp,
            "temp_max": max_temp
        })

    result = {
        "city": city,
        "forecast": forecast
    }
    set_to_cache(cache_key, result)
    return result


async def get_historical_weather(city: str):
    coords = get_coordinates(city)
    if coords is None:
        return None

    cache_key = f"history::{city}"
    cached = get_from_cache(cache_key)
    if cached:
        return cached

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
        min_temp = data["daily"]["temperature_2m_min"][i]
        max_temp = data["daily"]["temperature_2m_max"][i]

        if min_temp is None or max_temp is None:
            continue

        history.append({
            "date": data["daily"]["time"][i],
            "temp_min": min_temp,
            "temp_max": max_temp
        })

    result = {
        "city": city,
        "history": history
    }
    set_to_cache(cache_key, result)
    return result

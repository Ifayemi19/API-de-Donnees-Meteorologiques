from fastapi import APIRouter, HTTPException
from app.services.weather_service import (
    get_current_weather,
    get_forecast_weather,
    get_historical_weather
)
from app.schemas.weather_schema import (
    WeatherResponse,
    ForecastResponse,
    HistoryResponse
)
import httpx
from typing import Callable, Any

router = APIRouter()

# Fonction utilitaire pour centraliser la gestion des erreurs
async def handle_weather_request(func: Callable[[str], Any], city: str, not_found_message: str):
    if not city:
        raise HTTPException(status_code=400, detail="City is required")
    
    try:
        data = await func(city)
        if data is None:
            raise HTTPException(status_code=404, detail=not_found_message)
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/current/{city}", response_model=WeatherResponse)
async def current_weather(city: str):
    return await handle_weather_request(get_current_weather, city, "City not found")


@router.get("/forecast/{city}", response_model=ForecastResponse)
async def forecast_weather(city: str):
    return await handle_weather_request(get_forecast_weather, city, "Forecast not found")


@router.get("/history/{city}", response_model=HistoryResponse)
async def historical_weather(city: str):
    return await handle_weather_request(get_historical_weather, city, "Historical data not found")

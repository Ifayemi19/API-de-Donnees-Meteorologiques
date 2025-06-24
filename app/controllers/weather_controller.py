from fastapi import APIRouter, HTTPException
from app.services.weather_service import (
    get_current_weather,
    get_forecast_weather,
    get_historical_weather
)
import httpx

router = APIRouter()

@router.get("/current/{city}")
async def current_weather(city: str):
    if not city:
        raise HTTPException(status_code=400, detail="City is required")
    
    data = await get_current_weather(city)
    if data is None:
        raise HTTPException(status_code=404, detail="City not found")

    try:
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/forecast/{city}")
async def forecast_weather(city: str):
    if not city:
        raise HTTPException(status_code=400, detail="City is required")
    
    data = await get_forecast_weather(city)
    if data is None:
        raise HTTPException(status_code=404, detail="Forecast not found")

    try:
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/history/{city}")
async def historical_weather(city: str):
    if not city:
        raise HTTPException(status_code=400, detail="City is required")
    
    data = await get_historical_weather(city)
    if data is None:
        raise HTTPException(status_code=404, detail="Historical data not found")

    try:
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="External API error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

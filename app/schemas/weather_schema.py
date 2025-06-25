from pydantic import BaseModel
from typing import List, Optional

class Temperature(BaseModel):
    current: float
    unit: str

class WeatherResponse(BaseModel):
    city: str
    temperature: Temperature
    sources: List[str]
    timestamp: Optional[str] = None  # Si présent dans la réponse
    wind_speed: Optional[float] = None  # Si présent dans la réponse

class ForecastDay(BaseModel):
    date: str
    temp_min: float
    temp_max: float

class ForecastResponse(BaseModel):
    city: str
    forecast: List[ForecastDay]

class HistoryDay(BaseModel):
    date: str
    temp_min: Optional[float]  # ✅ autoriser les valeurs None
    temp_max: Optional[float]  # ✅ autoriser les valeurs None

class HistoryResponse(BaseModel):
    city: str
    history: List[HistoryDay]


# ✅ Ajout du schéma brut JSON pour le test de contrat
weather_response_schema = {
    "type": "object",
    "required": ["city", "temperature", "sources"],
    "properties": {
        "city": {"type": "string"},
        "temperature": {
            "type": "object",
            "required": ["current", "unit"],
            "properties": {
                "current": {"type": "number"},
                "unit": {"type": "string"}
            }
        },
        "sources": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "timestamp": {"type": "string"},
        "wind_speed": {"type": "number"}
    }
}

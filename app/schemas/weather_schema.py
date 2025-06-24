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
        }
    }
}

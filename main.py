from fastapi import FastAPI
from app.controllers.weather_controller import router as weather_router  # ← import du router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Inclusion du routeur avec le préfixe /weather
app.include_router(weather_router, prefix="/weather")  # ← crucial

@app.get("/health")
def health_check():
    return {"status": "ok"}

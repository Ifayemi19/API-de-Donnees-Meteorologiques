from fastapi import FastAPI
from app.controllers.weather_controller import router as weather_router
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()

app = FastAPI()

# Monitoring Prometheus
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Inclusion du routeur météo
app.include_router(weather_router, prefix="/weather")

@app.get("/health")
def health_check():
    return {"status": "ok"}

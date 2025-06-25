from fastapi import FastAPI
from app.controllers.weather_controller import router as weather_router
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator

# Charger les variables d’environnement
load_dotenv()

# Création de l'application FastAPI
app = FastAPI(title="Weather API")

# Ajout du middleware Prometheus pour les métriques
Instrumentator().instrument(app).expose(app)

# Inclusion du routeur météo
app.include_router(weather_router, prefix="/weather")

# Endpoint de vérification de santé
@app.get("/health")
def health_check():
    return {"status": "ok"}

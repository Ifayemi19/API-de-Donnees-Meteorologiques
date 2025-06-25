# Weather API - Projet FastAPI 

Une API REST de météo utilisant **FastAPI**, interrogeant les services **Open-Meteo** et **OpenWeatherMap**, et disposant de tests, supervision et monitoring.



##  Stack Technique

* **FastAPI**
* **httpx** pour les requêtes async
* **Docker / docker-compose**
* **PostgreSQL + Redis** (placeholder pour une future persistance)
* **Pytest** pour les tests
* **Prometheus + Grafana** pour le monitoring
* **Locust** pour les tests de charge



##  Installation & Lancement

# Cloner le repo
git clone <url-du-repo>
cd weather-api

# Créer un fichier .env
cp .env.example .env

# Lancer le projet
docker-compose up --build


Accéder à l'API : [http://localhost:8000/docs](http://localhost:8000/docs)



##  Endpoints disponibles

| Route                      | Description                   |
| -------------------------- | ----------------------------- |
| `/weather/current/{city}`  | Météo actuelle (agrégée)      |
| `/weather/forecast/{city}` | Prévision 5 jours             |
| `/weather/history/{city}`  | Historique 5 jours précédents |
| `/health`                  | Endpoint de santé             |

### Exemple de réponse `/weather/current/Paris`

```json
{
  "city": "Paris",
  "temperature": {
    "current": 19.5,
    "unit": "celsius"
  },
  "sources": ["openweather", "open-meteo"],
  "timestamp": "2025-06-21T12:00",
  "wind_speed": 10.5
}
```



##  Tests

### Lancer tous les tests unitaires et fonctionnels :


pytest


### Test de contrat JSON :


pytest app/tests/test_contract.py



##  Monitoring Prometheus & Grafana

* **Prometheus** scrape : [http://localhost:9090](http://localhost:9090)
* **Grafana** : [http://localhost:3000](http://localhost:3000)
  Login par défaut : `admin / admin`

### Panels créés :

* Histogramme des durées `http_request_duration_seconds`
* Compteur de requêtes `weather_api_requests_total`
* Taux d'échec `http_request_failed_ratio`

Dashboard exportable au format JSON depuis Grafana ⚙️ > Export



##  Test de charge (Locust)

### Lancer le test locust :


locust -f app/tests/locustfile.py --host=http://localhost:8000


Puis ouvrir [http://localhost:8089](http://localhost:8089) dans le navigateur.

### locustfile.py contient :

* `/weather/current/{city}` : pondération 3
* `/weather/forecast/Paris` : pondération 2
* `/weather/history/Paris` : pondération 1



from locust import HttpUser, task, between
import random

class WeatherAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_current_weather(self):
        city = random.choice(["Paris", "London", "Tokyo", "New York"])
        self.client.get(f"/weather/current/{city}", name="/weather/current")

    @task(2)
    def get_forecast(self):
        self.client.get("/weather/forecast/Paris", name="/weather/forecast")

    @task(1)
    def get_history(self):
        self.client.get("/weather/history/Paris", name="/weather/history")

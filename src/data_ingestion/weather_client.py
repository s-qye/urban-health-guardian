import requests
from datetime import datetime
from pydantic import BaseModel
from src.config import api_config, BOSTON_LAT, BOSTON_LON

class WeatherData(BaseModel):
    timestamp: datetime
    temperature_f: float
    feels_like_f: float
    humidity: int
    wind_speed_mph: float
    weather_condition: str
    weather_description: str
    cloud_coverage: int
    visibility_miles: float
    pressure_hpa: int

class WeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self):
        self.api_key = api_config.openweather_api_key
    
    def get_current_weather(self, lat=BOSTON_LAT, lon=BOSTON_LON) -> WeatherData:
        response = requests.get(
            f"{self.BASE_URL}/weather",
            params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "imperial"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        return WeatherData(
            timestamp=datetime.fromtimestamp(data["dt"]),
            temperature_f=data["main"]["temp"],
            feels_like_f=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            wind_speed_mph=data["wind"]["speed"],
            weather_condition=data["weather"][0]["main"],
            weather_description=data["weather"][0]["description"],
            cloud_coverage=data["clouds"]["all"],
            visibility_miles=data.get("visibility", 10000) / 1609.34,
            pressure_hpa=data["main"]["pressure"],
        )
import requests
from datetime import datetime
from pydantic import BaseModel
from src.config import api_config, BOSTON_LAT, BOSTON_LON

class AirQualityData(BaseModel):
    timestamp: datetime
    primary_aqi: int
    primary_pollutant: str
    category: str
    reporting_area: str

class AirQualityClient:
    BASE_URL = "https://www.airnowapi.org/aq"

    def __init__(self):
        self.api_key = api_config.airnow_api_key
    
    def get_current_air_quality(self, lat=BOSTON_LAT, lon=BOSTON_LON) -> AirQualityData:
        response = requests.get(
            f"{self.BASE_URL}/observation/latLong/current/",
            params={
                "format": "application/json",
                "latitute": lat, "longitude": lon,
                "distance": 25, "API_KEY": self.api_key
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        primary = max(data, key=lambda x: x["AQI"])

        return AirQualityData(
            timestamp=datetime.now(),
            primary_aqi=primary['AQI'],
            primary_pollutant=primary['ParameterName'],
            category=primary['Category']['Name'],
            reporting_area=primary['ReportingArea']
        )
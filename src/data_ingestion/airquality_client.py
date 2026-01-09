import requests
from datetime import datetime
from typing import Optional
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
    
    def get_current_aqi(self, lat: float = BOSTON_LAT, lon: float = BOSTON_LON) -> Optional[AirQualityData]:
        """Fetch current AQI. Returns None if no data available."""
        
        if not self.api_key:
            raise ValueError("AirNow API key not configured")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/observation/latLong/current/",
                params={
                    "format": "application/json",
                    "latitude": lat,
                    "longitude": lon,
                    "distance": 25,
                    "API_KEY": self.api_key
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            primary = max(data, key=lambda x: x.get("AQI", 0))
            
            return AirQualityData(
                timestamp=datetime.now(),
                primary_aqi=primary.get("AQI", 0),
                primary_pollutant=primary.get("ParameterName", "Unknown"),
                category=primary.get("Category", {}).get("Name", "Unknown"),
                reporting_area=primary.get("ReportingArea", "Unknown"),
            )
        
        except Exception as e:
            print(f"AirQuality API error: {e}")
            return None
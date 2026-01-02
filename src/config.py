import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / "data" / "cache"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "briefings"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BOSTON_LAT = 42.3601
BOSTON_LON = -71.0589

class APIConfig(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    airnow_api_key: str = os.getenv("AIRNOW_API_KEY", "")
    
    def validate_keys(self) -> dict[str, bool]:
        return {
            "openai": bool(self.openai_api_key),
            "openweather": bool(self.openweather_api_key),
            "airnow": bool(self.airnow_api_key),
        }

api_config = APIConfig()
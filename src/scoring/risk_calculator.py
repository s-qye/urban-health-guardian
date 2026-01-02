# src/scoring/risk_calculator.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class RiskAssessment:
    overall_score: float
    risk_level: RiskLevel
    confidence: str
    primary_concerns: list[str]

class RiskCalculator:
    WEIGHTS = {
        "air_quality": 0.35,
        "temperature": 0.25,
        "precipitation": 0.15,
        "wind": 0.10,
        "visibility": 0.15,
    }
    
    def calculate(self, weather, air_quality) -> RiskAssessment:
        scores = []
        concerns = []
        
        # Air Quality Score
        if air_quality is not None:
            aqi = air_quality.primary_aqi
            if aqi <= 50:
                aqi_score = aqi * 0.4
            elif aqi <= 100:
                aqi_score = 20 + (aqi - 50) * 0.6
                concerns.append(f"AQI moderate ({aqi})")
            elif aqi <= 150:
                aqi_score = 50 + (aqi - 100) * 0.6
                concerns.append(f"AQI unhealthy for sensitive groups ({aqi})")
            else:
                aqi_score = 80 + (aqi - 150) * 0.4
                concerns.append(f"AQI unhealthy ({aqi})")
            scores.append(("air_quality", min(aqi_score, 100)))
        
        # Temperature Score
        if weather is not None:
            temp = weather.feels_like_f
            
            if temp < 20:
                temp_score = 70
                concerns.append(f"Very cold ({temp:.0f}°F)")
            elif temp < 32:
                temp_score = 50
                concerns.append(f"Freezing ({temp:.0f}°F)")
            elif temp > 100:
                temp_score = 90
                concerns.append(f"Extreme heat ({temp:.0f}°F)")
            elif temp > 90:
                temp_score = 60
                concerns.append(f"Hot weather ({temp:.0f}°F)")
            elif temp > 80:
                temp_score = 30
            else:
                temp_score = abs(temp - 70) * 2
            scores.append(("temperature", min(temp_score, 100)))
            
            # Wind score
            wind = weather.wind_speed_mph
            if wind > 30:
                wind_score = 60
                concerns.append(f"High winds ({wind:.0f} mph)")
            elif wind > 20:
                wind_score = 30
            else:
                wind_score = wind
            scores.append(("wind", min(wind_score, 100)))
            
            # Visibility score
            visibility = weather.visibility_miles
            if visibility < 1:
                vis_score = 70
                concerns.append(f"Low visibility ({visibility:.1f} mi)")
            elif visibility < 3:
                vis_score = 40
            else:
                vis_score = 0
            scores.append(("visibility", vis_score))
        
        # Calculate overall score
        if scores:
            total_weight = sum(self.WEIGHTS.get(s[0], 0.1) for s in scores)
            overall = sum(s[1] * self.WEIGHTS.get(s[0], 0.1) for s in scores) / total_weight
        else:
            overall = 0
        
        # Determine risk level
        level = self._get_level(overall)
        
        # Determine confidence
        confidence = "high" if len(scores) >= 3 else "medium" if len(scores) >= 1 else "low"
        
        return RiskAssessment(
            overall_score=overall,
            risk_level=level,
            confidence=confidence,
            primary_concerns=concerns[:5],
        )
    
    def _get_level(self, score: float) -> RiskLevel:
        if score < 30:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MODERATE
        elif score < 70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
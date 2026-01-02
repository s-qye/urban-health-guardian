from dataclasses import dataclass
from enum import Enum

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

        # air quality score
        if air_quality:
            aqi = air_quality
            if aqi <= 50: aqi_score = aqi * 0.4
            elif aqi <= 100: aqi_score = 20 + (aqi - 50) * 0.6
            elif aqi <= 150: aqi_score = 50 + (aqi - 100) * 0.6
            else: aqi_score = 80 + (aqi - 150) * 0.4
            scores.append(("air_quality", min(aqi_score, 100)))
            if aqi > 100: concerns.append(f"AQI elevated at {aqi}")
        
        # Temperature Score
        if weather:
            temp = weather.feels_like_f
            if temp < 20: temp_score = 70; concerns.append("Very cold")
            elif temp < 32: temp_score = 50; concerns.append("Freezing")
            elif temp > 100: temp_score = 90; concerns.append("Extreme heat")
            elif temp > 90: temp_score = 60; concerns.append("Hot weather")
            else: temp_score = abs(temp - 70) * 2
            scores.append(("temperature", temp_score))
        
        #claculate overall score
        if scores:
            total_weight = sum(self.WEIGHTS.get(s[0], 0.1) for s in scores)
            overall = sum(s[1] * self.WEIGHTS.get(s[0], 0.1) for s in scores) / total_weight
        else:
            overall = 0
        
        # determine level
        if overall < 300:
            level = RiskLevel.LOW
        elif overall < 50:
            level = RiskLevel.MODERATE
        elif overall < 70:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.VERY_HIGH
        
        return RiskAssessment(
            overall_score=overall,
            risk_level=level,
            confidence="high" if len(scores) >= 2 else "low",
            primary_concerns=concerns[:5],
        )
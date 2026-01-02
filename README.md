<!-- README.md -->

# 🏥 Urban Health Guardian

> An autonomous environmental risk scoring + action agent for Boston commuters.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red)

## Overview

Urban Health Guardian is an intelligent agent that automatically:
- Collects real-time weather and air quality data
- Calculates health risk scores with confidence levels  
- Makes autonomous decisions about trend analysis
- Generates personalized daily briefings

## Architecture
[Weather API] & [AirNow API] → [Data Ingestion] → [Risk Scoring] → [Action Generation] → [LangGraph Agent] → [LLM Briefing] → [Streamlit UI]

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API Keys: OpenWeather, AirNow, OpenAI

### Installation
```bash
git clone https://github.com/yourusername/urban-health-guardian.git
cd urban-health-guardian
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
```

### Run
```bash
streamlit run app.py      # Web UI
python -m src.main --save # CLI
```

## 📊 Sample Outputs

### 🟢 Low Risk
Good morning! Excellent conditions for outdoor activities.
🌡️ 72°F, clear skies | 💨 AQI 35 (Good)
✅ Perfect for exercise | ✅ No mask needed

### 🔴 High Risk
⚠️ ALERT: Multiple hazards detected.
🌡️ 98°F (feels 108°F) | 💨 AQI 165 (Unhealthy)
🚨 Stay indoors 11am-3pm | 😷 Wear N95 outdoors

## Testing
```bash
pytest tests/ -v --cov=src
```

## License
MIT
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.data_ingestion.weather_client import WeatherClient
from src.data_ingestion.airquality_client import AirQualityClient
from src.scoring.risk_calculator import RiskCalculator
from src.scoring.action_generator import ActionGenerator
from src.config import api_config

weather_client = WeatherClient()
aqi_client = AirQualityClient()
calculator = RiskCalculator()
generator = ActionGenerator()

def collect_data(state):
    """Node: Collect environmental data."""
    print(f"[{state['run_id']}] Collecting data...")
    errors = list(state.get("errors", []))
    weather_data = None
    aqi_data = None
    
    try:
        weather = weather_client.get_current_weather()
        if weather:
            weather_data = weather.model_dump()
    except Exception as e:
        errors.append(f"Weather error: {e}")
    
    try:
        aqi = aqi_client.get_current_aqi()
        if aqi:
            aqi_data = aqi.model_dump()
    except Exception as e:
        errors.append(f"AQI error: {e}")
    
    sources_available = sum([weather_data is not None, aqi_data is not None])
    completeness = sources_available / 2
    
    return {
        "phase": "collecting_data",
        "weather_data": weather_data,
        "air_quality_data": aqi_data,
        "data_quality": {"completeness": completeness},
        "errors": errors,
    }

def analyze_risk(state):
    """Node: Calculate risk score."""
    print(f"{state['run_id']} Analyzing risk...")

    from src.data_ingestion.weather_client import WeatherData
    from src.data_ingestion.airquality_client import AirQualityData

    weather = WeatherData(**state["weather_data"]) if state.get("weather_data") else None
    aqi = AirQualityData(**state["air_quality_data"]) if state.get("air_quality_data") else None

    assessment = calculator.calculate(weather, aqi)

    return {
        "phase": "analyzing_risk",
        "risk_score": assessment.overall_score,
        "risk_level": assessment.risk_level.value,
        "confidence": assessment.confidence,
        "trend_check_needed": assessment.overall_score >= 50,
    }

def check_trends(state):
    """Node: Check for anomalies (optional)."""
    print(f"[{state['run_id']}] Checking trends...")
    return {
        "phase": "checking_trends",
        "trend_alert": state.get("risk_score", 0) >= 70,
    }

def skip_trends(state):
    """Node: Skip trend check for low risk."""
    print(f"[{state['run_id']}] Skipping trend check...")
    return {
        "phase": "checking_trends",
        "trend_alert": False,
    }

def generate_actions(state):
    """Node: Generate action plan."""
    print(f"[{state['run_id']}] Generating actions...")

    from src.scoring.risk_calculator import RiskAssessment, RiskLevel

    assessment = RiskAssessment(
        overall_score=state["risk_score"],
        risk_level=RiskLevel(state["risk_level"]),
        confidence=state["confidence"],
        primary_concerns=[],
    )

    plan = generator.generate(assessment)
    briefing_type = "high_risk" if state["risk_score"] >= 70 else "moderate" if state["risk_score"] >= 40 else "short"

    return {
        "phase": "generating_actions",
        "action_plan": {
            "summary": plan.summary,
            "actions": plan.actions,
            "outdoor_exercise_safe": plan.outdoor_exercise_safe,
            "mask_recommended": plan.mask_recommended,
        },
        "briefing_type": briefing_type,
    }

def draft_briefing(state):
    """Node: Generate LLM briefing."""
    print(f"[{state['run_id']}] ✍️ Drafting briefing...")
    
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_config.openai_api_key)
    
    weather_summary = "N/A"
    if state.get("weather_data"):
        w = state["weather_data"]
        weather_summary = f"{w['temperature_f']}°F, {w['weather_description']}"
    
    aqi_summary = "N/A"
    if state.get("air_quality_data"):
        a = state["air_quality_data"]
        aqi_summary = f"AQI {a['primary_aqi']} ({a['category']})"
    
    prompt = f"""Generate a brief Boston health briefing:
    
Weather: {weather_summary}
Air Quality: {aqi_summary}
Risk Score: {state.get('risk_score', 0):.0f}/100 ({state.get('risk_level')})

{"HIGH RISK: Be urgent" if state.get('risk_score', 0) >= 70 else "Keep it brief and friendly."}
Include 2-3 recommendations. Under 100 words."""

    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "phase": "complete",
        "briefing_text": response.content,
    }

def should_check_trends(state):
    if state.get("trend_check_needed", False):
        return "check_trends"
    return "skip_trends"
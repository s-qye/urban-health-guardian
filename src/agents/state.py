from typing import TypedDict, Optional, Annotated
from datetime import datetime
from enum import Enum
from langgraph.graph.message import add_messages

class AgentPhase(str, Enum):
    COLLECTING_DATA = "collecting_data"
    ANALYZING_RISK = "analyzing_risk"
    CHECKING_TRENDS = "checking_trends"
    GENERATING_ACTIONS = "generating_actions"
    DRAFTING_BRIEFING = "drafting_briefing"
    COMPLETE = "complete"

class UrbanHealthState(TypedDict):
    run_id: str
    timestamp: datetime
    phase: AgentPhase

    weather_data: Optional[dict]
    air_quality_data: Optional[dict]
    data_quality: dict

    risk_score: float
    risk_level: str
    confidence: str

    trend_check_needed: bool
    trend_alert: bool

    action_plan: Optional[dict]
    briefing_text: str
    briefing_type: str

    errors: list[str]
    messages: Annotated[list, add_messages]

def create_initial_state() -> UrbanHealthState:
    import uuid
    return UrbanHealthState(
        run_id=str(uuid.uuid4())[:8],
        timestamp=datetime.now(),
        phase=AgentPhase.COLLECTING_DATA,
        weather_data=None,
        air_quality_data=None,
        data_quality={},
        risk_score=0.0,
        risk_level="unknown",
        confidence="unknown",
        trend_check_needed=False,
        trend_alert=False,
        action_plan=None,
        briefing_text="",
        briefing_type="short",
        errors=[],
        messages=[],
    )
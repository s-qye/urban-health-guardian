import pytest
from src.agents.graph import run_health_guardian
from src.scoring.risk_calculator import RiskCalculator, RiskLevel

def test_risk_calculator_low():
    calc = RiskCalculator()
    # Mock low-risk conditions
    result = calc.calculate(None, None)
    assert result.overall_score == 0

def test_risk_levels():
    calc = RiskCalculator()
    assert calc._get_level(25) == RiskLevel.LOW
    assert calc._get_level(45) == RiskLevel.MODERATE
    assert calc._get_level(65) == RiskLevel.HIGH
    assert calc._get_level(85) == RiskLevel.VERY_HIGH

@pytest.mark.integration
def test_full_agent():
    result = run_health_guardian()
    assert "briefing_text" in result
    assert result.get("phase") == "complete"
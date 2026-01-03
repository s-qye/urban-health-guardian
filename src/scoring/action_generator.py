from dataclasses import dataclass

@dataclass
class ActionPlan:
    summary: str
    actions: list[dict]
    ourdoor_exercise_safe: bool
    mask_recommended: bool

class ActionGenerator:
    def generate(self, assessment) -> ActionPlan:
        actions = []
        outdoor_safe = True
        mask_needed = False

        if assessment.overall_score >= 70:
            actions.append({"priority": "critical", "action": "Stay indoors if possible!"})
            outdoor_safe = False
        elif assessment.overall_score >= 50:
            actions.append({"priority": "high", "action": "Limit outdoor exposure."})

        for concern in assessment.primary_concerns:
            if "AQI" in concern:
                mask_needed = True
                actions.append({"priority": "high", "action": "Wear N95 mask outdoors."})
            if "heat" in concern.lower():
                actions.append({"priority": "medium", "action": "Stay hydrated"})
        
        summary = f"{'🔴' if assessment.overall_score >= 70 else '🟡' if assessment.overall_score >= 40 else '🟢'} Risk: {assessment.overall_score:.0f}/100"

        return ActionPlan(
            summary=summary,
            actions=actions,
            outdoor_exercise_safe=outdoor_safe,
            mask_recommended=mask_needed,
        )

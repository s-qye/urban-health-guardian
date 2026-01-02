import json
from datetime import datetime, timedelta
from pathlib import Path
from src.config import CACHE_DIR, OUTPUT_DIR

class BriefingHistory:
    def __init__(self):
        self.output_dir = OUTPUT_DIR
    
    def save(self, state: dict) -> Path:
        timestamp = state.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        filename = f"briefing_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        record = {
            "timestamp": timestamp.isoformat(),
            "risk_score": state.get("risk_score"),
            "risk_level": state.get("risk_level"),
            "briefing_text": state.get("briefing_text"),
        }
        
        with open(filepath, "w") as f:
            json.dump(record, f, indent=2)
        
        return filepath
    
    def get_recent(self, days=7) -> list[dict]:
        cutoff = datetime.now() - timedelta(days=days)
        briefings = []
        
        for fp in sorted(self.output_dir.glob("briefing_*.json"), reverse=True):
            with open(fp) as f:
                record = json.load(f)
            if datetime.fromisoformat(record["timestamp"]) >= cutoff:
                briefings.append(record)
        
        return briefings

briefing_history = BriefingHistory()
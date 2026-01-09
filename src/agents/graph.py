from langgraph.graph import StateGraph, END
from src.agents.state import UrbanHealthState, create_initial_state
from src.agents.nodes import (
    collect_data, analyze_risk, check_trends, skip_trends,
    generate_actions, draft_briefing, should_check_trends
)

def build_health_guardian_graph():
    """
    Graph Structure:
    
    [collect_data] → [analyze_risk] → {trend check?}
                                          ↓
                    [check_trends] or [skip_trends]
                                          ↓
                              [generate_actions]
                                          ↓
                               [draft_briefing]
                                          ↓
                                        [END]
    """
    graph = StateGraph(UrbanHealthState)
    
    graph.add_node("collect_data", collect_data)
    graph.add_node("analyze_risk", analyze_risk)
    graph.add_node("check_trends", check_trends)
    graph.add_node("skip_trends", skip_trends)
    graph.add_node("generate_actions", generate_actions)
    graph.add_node("draft_briefing", draft_briefing)
    
    graph.set_entry_point("collect_data")
    graph.add_edge("collect_data", "analyze_risk")
    
    graph.add_conditional_edges(
        "analyze_risk",
        should_check_trends,
        {"check_trends": "check_trends", "skip_trends": "skip_trends"}
    )
    
    graph.add_edge("check_trends", "generate_actions")
    graph.add_edge("skip_trends", "generate_actions")
    graph.add_edge("generate_actions", "draft_briefing")
    graph.add_edge("draft_briefing", END)
    
    return graph.compile()

health_guardian_agent = build_health_guardian_graph()

def run_health_guardian() -> dict:
    """Run the agent and return final state."""
    initial_state = create_initial_state()
    print(f"\n{'='*50}")
    print(f"🏃 Running Urban Health Guardian")
    print(f"   Run ID: {initial_state['run_id']}")
    print(f"{'='*50}\n")
    
    final_state = health_guardian_agent.invoke(initial_state)
    
    print(f"\n{'='*50}")
    print(f"✅ Complete!")
    print(f"{'='*50}\n")
    
    return final_state

if __name__ == "__main__":
    result = run_health_guardian()
    print("BRIEFING:")
    print(result.get("briefing_text"))
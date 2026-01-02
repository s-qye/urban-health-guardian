import streamlit as st
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Urban Health Guardian",
    page_icon="🏥",
    layout="wide",
)

# Add after st.set_page_config()

st.markdown("""
<style>
    /* Mobile-friendly */
    @media (max-width: 768px) {
        .stButton button {
            width: 100%;
            padding: 1rem;
            font-size: 1.2rem;
        }
    }
    
    /* Risk colors */
    .risk-low { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .risk-high { background: linear-gradient(135deg, #eb3349, #f45c43); }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

from src.agents.graph import run_health_guardian
from src.utils.cache import briefing_history
from src.config import api_config

def check_api_status():
    return api_config.validate_keys()

def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🏥 Urban Health Guardian")
        st.caption("Environmental Risk Assessment for Boston Commuters")
    with col2:
        st.markdown(f"**📍 Boston, MA**")
        st.markdown(f"🕐 {datetime.now().strftime('%I:%M %p')}")

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Status")
        
        # API Status
        st.subheader("API Connections")
        for api, ok in check_api_status().items():
            if ok:
                st.success(f"✅ {api.title()}")
            else:
                st.error(f"❌ {api.title()}")
        
        st.divider()
        
        # Recent stats
        st.subheader("📊 Recent Stats")
        recent = briefing_history.get_recent(days=7)
        if recent:
            avg = sum(b.get("risk_score", 0) for b in recent) / len(recent)
            st.metric("Avg Risk Score (7d)", f"{avg:.1f}")
            st.metric("Briefings Generated", len(recent))
        else:
            st.info("No recent briefings")

def render_main():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate = st.button(
            "🚀 Generate Today's Briefing",
            type="primary",
            use_container_width=True,
        )
    
    if generate:
        with st.spinner("🔄 Analyzing conditions..."):
            try:
                result = run_health_guardian()
                st.session_state["latest"] = result
                st.session_state["latest_time"] = datetime.now()
                briefing_history.save(result)
            except Exception as e:
                st.error(f"Error: {e}")
                return
    
    if "latest" in st.session_state:
        render_briefing(st.session_state["latest"])
    else:
        st.info("👆 Click to generate today's briefing")

def render_briefing(result):
    st.divider()
    
    # Risk score cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = result.get("risk_score", 0)
        level = result.get("risk_level", "unknown")
        color = "🟢" if score < 40 else "🟡" if score < 70 else "🔴"
        
        st.metric("Risk Score", f"{score:.0f}/100")
        st.markdown(f"{color} **{level.title()} Risk**")
    
    with col2:
        st.metric("Confidence", result.get("confidence", "N/A").title())
        completeness = result.get("data_quality", {}).get("completeness", 0)
        st.progress(completeness, text=f"Data: {completeness*100:.0f}%")
    
    with col3:
        time = st.session_state.get("latest_time", datetime.now())
        st.metric("Generated", time.strftime("%I:%M %p"))
    
    st.divider()
    
    # Briefing text
    st.subheader("Today's Briefing")
    st.markdown(result.get("briefing_text", "No briefing available"))
    
    # Details expanders
    with st.expander("Detailed Analysis"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Weather")
            if result.get("weather_data"):
                w = result["weather_data"]
                st.write(f"🌡️ Temp: {w.get('temperature_f')}°F")
                st.write(f"💧 Humidity: {w.get('humidity')}%")
                st.write(f"💨 Wind: {w.get('wind_speed_mph')} mph")
            else:
                st.warning("Unavailable")
        
        with col2:
            st.subheader("Air Quality")
            if result.get("air_quality_data"):
                a = result["air_quality_data"]
                st.write(f"📊 AQI: {a.get('primary_aqi')}")
                st.write(f"📍 Category: {a.get('category')}")
            else:
                st.warning("Unavailable")
    
    with st.expander("📝 Action Plan"):
        if result.get("action_plan"):
            plan = result["action_plan"]
            
            col1, col2 = st.columns(2)
            with col1:
                if plan.get("outdoor_exercise_safe"):
                    st.success("✅ Outdoor exercise safe")
                else:
                    st.error("❌ Limit outdoor exercise")
            with col2:
                if plan.get("mask_recommended"):
                    st.warning("😷 Mask recommended")
            
            for action in plan.get("actions", []):
                priority = action.get("priority", "info")
                if priority == "critical":
                    st.error(action.get("action"))
                elif priority == "high":
                    st.warning(action.get("action"))
                else:
                    st.info(action.get("action"))
    
    # Errors
    if result.get("errors"):
        with st.expander("⚠️ Errors", expanded=True):
            for error in result["errors"]:
                st.error(error)

def main():
    render_header()
    render_sidebar()
    render_main()
    
    st.divider()
    st.caption("Built with ❤️ for Boston | Powered by LangGraph")

if __name__ == "__main__":
    main()

# Add to app.py - tab-based navigation

import plotly.express as px
import pandas as pd

def render_tabs():
    tab1, tab2, tab3 = st.tabs(["🏠 Today", "📈 History", "⚙️ Settings"])
    
    with tab1:
        render_main()
    with tab2:
        render_history()
    with tab3:
        render_settings()

def render_history():
    st.header("📈 Briefing History")
    
    recent = briefing_history.get_recent(days=14)
    if not recent:
        st.info("No briefings yet!")
        return
    
    df = pd.DataFrame(recent)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    # Line chart
    st.subheader("Risk Score Trend")
    fig = px.line(df, x="timestamp", y="risk_score", markers=True)
    fig.add_hline(y=40, line_dash="dash", line_color="yellow")
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribution pie
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Distribution")
        counts = df["risk_level"].value_counts()
        fig = px.pie(values=counts.values, names=counts.index)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Recent Briefings")
        for _, row in df.tail(5).iterrows():
            color = "🟢" if row["risk_score"] < 40 else "🟡" if row["risk_score"] < 70 else "🔴"
            st.markdown(f"{color} **{row['timestamp'].strftime('%b %d')}** - Score: {row['risk_score']:.0f}")

def render_settings():
    st.header("⚙️ Settings")
    
    st.subheader("📍 Location")
    st.text_input("City", value="Boston", disabled=True)
    st.caption("Multi-city support coming soon!")
    
    st.subheader("📊 Data")
    if st.button("📥 Export History"):
        recent = briefing_history.get_recent(30)
        if recent:
            import json
            st.download_button(
                "Download JSON",
                data=json.dumps(recent, indent=2, default=str),
                file_name="briefing_history.json"
            )

# Update main() to use render_tabs() instead of render_main()
def add_auto_refresh():
    with st.sidebar:
        st.divider()
        st.subheader("🔄 Auto-Refresh")
        
        if st.checkbox("Enable auto-refresh"):
            interval = st.slider("Minutes", 5, 60, 30)
            
            if "last_refresh" not in st.session_state:
                st.session_state["last_refresh"] = datetime.now()
            
            elapsed = (datetime.now() - st.session_state["last_refresh"]).seconds / 60
            remaining = max(0, interval - elapsed)
            
            st.progress(1 - remaining / interval)
            st.caption(f"Next: {remaining:.0f} min")
            
            if remaining <= 0:
                st.session_state["last_refresh"] = datetime.now()
                st.rerun()
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import io
import json

st.set_page_config(page_title="Preschool Lesson Planner", layout="wide")

# Better mobile styling
st.markdown("""
<style>
    .stApp { max-width: 100%; }
    .block-container { padding-top: 1rem; }
    table { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.title("🧸 Preschool Weekly Lesson Planner")
st.caption("Creative Curriculum + Heggerty • Optimized for iPad")

# Sidebar (collapsible on mobile)
with st.sidebar:
    st.header("Week Settings")
    start_date = st.date_input("Week Start Date", datetime.now().date())
    days_off_input = st.text_area("Days Off (YYYY-MM-DD, comma separated)", 
                                  placeholder="2026-07-15,2026-07-16")
    theme = st.text_input("Main Theme / Study", "Exploring Balls")
    science_topic = st.text_input("Monthly Science Topic", "Plant Growth")

    if st.button("Generate This Week"):
        st.session_state.generate = True
        st.session_state.current_start = start_date
        st.session_state.theme = theme
        st.session_state.science = science_topic
        st.session_state.days_off = days_off_input

# Load previous plans if any
if "plans" not in st.session_state:
    st.session_state.plans = {}

# Generation logic
if st.session_state.get("generate"):
    # ... (same logic as before, but cleaner)
    off_dates = set()
    if st.session_state.days_off.strip():
        try:
            off_dates = {datetime.strptime(d.strip(), "%Y-%m-%d").date() 
                        for d in st.session_state.days_off.split(",")}
        except:
            st.error("Date format error")
    
    plan_days = []
    current = st.session_state.current_start
    while len(plan_days) < 4:
        if current.weekday() < 5 and current not in off_dates:
            plan_days.append(current)
        current += timedelta(days=1)
    
    df = pd.DataFrame({
        "Day": [d.strftime("%A, %b %d") for d in plan_days],
        "Math": ["Counting / Number concepts (Creative Curriculum)" for _ in plan_days],
        "Language": ["Vocabulary + shared writing" for _ in plan_days],
        "Story Time": ["Read-aloud + discussion" for _ in plan_days],
        "Circle Time": ["Greeting, calendar, songs" for _ in plan_days],
        "Heggerty": ["Daily 10-min phonemic awareness" for _ in plan_days]
    })
    
    st.subheader(f"Week of {plan_days[0].strftime('%b %d, %Y')}")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.subheader("Weekly Specials")
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("**Gym (3x)**\n1. Obstacle course\n2. Ball skills\n3. Dance/movement")
    with col2: st.markdown(f"**Art**\n{st.session_state.theme} creative project")
    with col3: st.markdown(f"**Science**\n{st.session_state.science}")
    
    # Save to session
    week_key = plan_days[0].isoformat()
    st.session_state.plans[week_key] = {
        "theme": st.session_state.theme,
        "df": df.to_dict(),
        "science": st.session_state.science
    }
    
    # DOCX Download
    if st.button("📥 Download Word (.docx)"):
        doc = Document()
        doc.add_heading(f"Lesson Plan - {st.session_state.theme}", 0)
        # ... (table creation same as before)
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        st.download_button("Download file", bio, f"plan_{week_key}.docx", 
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Show saved weeks
if st.session_state.plans:
    st.divider()
    st.subheader("Saved Weeks")
    for key, data in st.session_state.plans.items():
        st.write(f"📅 {key} — {data['theme']}")

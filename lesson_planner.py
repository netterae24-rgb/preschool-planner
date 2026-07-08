import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import io

st.set_page_config(page_title="Preschool Lesson Planner", layout="wide")
st.title("🧸 Preschool Weekly Lesson Planner")
st.markdown("**Creative Curriculum Guided Edition + Heggerty**")

# Sidebar
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Week Start Date", datetime.now().date())
days_off = st.sidebar.text_area("Days Off (YYYY-MM-DD, comma separated)", 
                                help="e.g. 2026-07-15,2026-07-16")
theme = st.sidebar.text_input("Main Theme", "Exploring Balls")
science_topic = st.sidebar.text_input("Monthly Science Topic", "Plants and Growth")

if st.sidebar.button("Generate Weekly Plan"):
    off_dates = []
    if days_off.strip():
        off_dates = [datetime.strptime(d.strip(), "%Y-%m-%d").date() for d in days_off.split(",")]
    
    plan_days = []
    current = start_date
    while len(plan_days) < 4:
        if current.weekday() < 5 and current not in off_dates:
            plan_days.append(current)
        current += timedelta(days=1)
    
    if not plan_days:
        st.error("No valid days found. Check your dates.")
    else:
        st.success(f"Planning for: {plan_days[0]} to {plan_days[-1]}")
        
        df = pd.DataFrame({
            "Day": [d.strftime("%A, %b %d") for d in plan_days],
            "Math Lesson": ["Counting objects / Number concepts (Creative Curriculum)" for _ in plan_days],
            "Language Lesson": ["Vocabulary building / Shared reading" for _ in plan_days],
            "Story Time": ["Read-aloud + discussion" for _ in plan_days],
            "Circle Time": ["Morning greeting, calendar, weather, song" for _ in plan_days],
            "Heggerty": ["Daily 10-min: Rhyming / Syllables / Initial Sounds" for _ in plan_days]
        })
        
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Weekly Special Activities")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Gym (3x)**\n1. Obstacle course\n2. Ball skills\n3. Dance & movement")
        with col2:
            st.write(f"**Art**\nTheme-related: {theme}")
        with col3:
            st.write(f"**Science**\n{science_topic}")
        
        # Store for download
        st.session_state.plan_days = plan_days
        st.session_state.df = df
        st.session_state.theme = theme
        st.session_state.science_topic = science_topic

# Download button
if st.session_state.get("plan_days") is not None:
    if st.button("📥 Download Full Word Document"):
        doc = Document()
        doc.add_heading(f"Lesson Plan - {st.session_state.theme}", 0)
        doc.add_paragraph(f"Week of: {st.session_state.plan_days[0]} to {st.session_state.plan_days[-1]}")
        
        table = doc.add_table(rows=1, cols=6)
        hdr_cells = table.rows[0].cells
        headers = ["Day", "Math Lesson", "Language Lesson", "Story Time", "Circle Time", "Heggerty"]
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
        
        for _, row in st.session_state.df.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
        
        doc.add_heading("Special Activities", level=1)
        doc.add_paragraph("Gym: Obstacle course, Ball skills, Dance & movement")
        doc.add_paragraph(f"Art Project: {st.session_state.theme} themed")
        doc.add_paragraph(f"Science: {st.session_state.science_topic}")
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.download_button(
            label="✅ Click here to download .docx",
            data=bio.getvalue(),
            file_name=f"lesson_plan_{st.session_state.plan_days[0]}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.info("Generate a plan first, then click the download button below it.")

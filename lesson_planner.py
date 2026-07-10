import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from docx import Document
import io

st.set_page_config(page_title="Preschool Lesson Planner", layout="wide")
st.title("🧸 Preschool Weekly Lesson Planner")
st.markdown("**Creative Curriculum + Heggerty + Pocket of Preschool**")

# Creative Curriculum Themes
creative_themes = [
    "Exploring Balls", "Buildings", "Trees", "Gardening", "Music Making", 
    "Reduce, Reuse, Recycle", "Pets", "Roads", "Simple Machines", "Insects",
    "Clothes", "Sand and Water", "Exercise", "Transportation", "All About Me"
]

# Pocket of Preschool Topics
pocket_topics = [
    "All About Me", "Transportation", "Community Helpers", "Farm", "Ocean", 
    "Zoo Animals", "Dinosaurs", "Space", "Seasons", "Weather", "Fall", 
    "Winter", "Spring", "Summer", "Pirates", "Construction", "Bugs & Insects"
]

# Sidebar
st.sidebar.header("Week Settings")
start_date = st.sidebar.date_input("Week Start Date", datetime.now().date())
days_off_input = st.sidebar.text_area("Days Off (YYYY-MM-DD, comma separated)", 
                                      placeholder="2026-07-15,2026-07-16")
theme = st.sidebar.selectbox("Main Theme (Creative Curriculum)", creative_themes)
pocket_topic = st.sidebar.selectbox("Pocket of Preschool Activities", pocket_topics)

if st.sidebar.button("Generate Weekly Plan"):
    off_dates = set()
    if days_off_input.strip():
        try:
            off_dates = {datetime.strptime(d.strip(), "%Y-%m-%d").date() for d in days_off_input.split(",")}
        except:
            st.error("Invalid date format")

    # Generate Mon-Thu only, with NO SCHOOL handling
    plan_days = []
    current = start_date
    while len(plan_days) < 4:
        if current.weekday() <= 3:  # Mon=0 ... Thu=3
            plan_days.append(current)
        current += timedelta(days=1)

    # Build rows
    rows = []
    for day in plan_days:
        if day in off_dates:
            rows.append({
                "Day": day.strftime("%A, %b %d"),
                "Math Lesson": "NO SCHOOL",
                "Language Lesson": "NO SCHOOL",
                "Story Time": "NO SCHOOL",
                "Circle Time": "NO SCHOOL",
                "Heggerty": "NO SCHOOL"
            })
        else:
            rows.append({
                "Day": day.strftime("%A, %b %d"),
                "Math Lesson": f"Counting / Number concepts - {theme}",
                "Language Lesson": f"Vocabulary & shared writing - {theme}",
                "Story Time": f"Read-aloud + discussion - {theme}",
                "Circle Time": f"Greeting, calendar, songs - {theme}",
                "Heggerty": "Daily 10-min phonemic awareness"
            })

    df = pd.DataFrame(rows)
    st.success(f"Week of {plan_days[0].strftime('%b %d')} — {plan_days[-1].strftime('%b %d')}")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Weekly Special Activities")
    st.write(f"**Art Project**: {theme} themed")
    st.write(f"**Pocket of Preschool Activities**: {pocket_topic} centers & ideas")
    st.write("**Gym (3x)**: Obstacle course, Ball skills, Dance & movement")

    # Save to session state
    st.session_state.plan_days = plan_days
    st.session_state.df = df
    st.session_state.theme = theme
    st.session_state.pocket_topic = pocket_topic

# Download
if st.session_state.get("plan_days") is not None:
    if st.button("📥 Download as Word Document"):
        doc = Document()
        doc.add_heading(f"Lesson Plan - {st.session_state.theme}", 0)
        doc.add_paragraph(f"Week of: {st.session_state.plan_days[0]} to {st.session_state.plan_days[-1]}")
        
        table = doc.add_table(rows=1, cols=6)
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(["Day", "Math Lesson", "Language Lesson", "Story Time", "Circle Time", "Heggerty"]):
            hdr_cells[i].text = col
        
        for _, row in st.session_state.df.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
        
        doc.add_heading("Special Activities", level=1)
        doc.add_paragraph(f"Art Project: {st.session_state.theme} themed")
        doc.add_paragraph(f"Pocket of Preschool: {st.session_state.pocket_topic}")
        doc.add_paragraph("Gym: Obstacle course, Ball skills, Dance & movement")
        
        bio = io.BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        st.download_button(
            label="✅ Download .docx",
            data=bio.getvalue(),
            file_name=f"lesson_plan_{st.session_state.plan_days[0]}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

st.info("You can expand the dropdown lists anytime — just tell me more themes/topics to add!")

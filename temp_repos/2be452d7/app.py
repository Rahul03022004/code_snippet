import streamlit as st

from parser.resume_parser import extract_resume_text
from parser.jd_parser import extract_jd_text
from models.skill_extractor import extract_skills
from engine.skill_graph import build_skill_graph
from engine.gap_analysis import find_skill_gap
from engine.path_generator import generate_learning_path
from utils.reasoning import generate_reasoning
from utils.graph_viz import visualize_graph
from utils.time_estimator import estimate_learning_time
from utils.course_recommender import recommend_courses
from utils.chatbot import mentor_chat

# ------------------ CSS ------------------ #
def load_css():
    st.markdown("""
    <style>
    body { background-color: #f3f6f8; }

    .main-title {
        font-size: 34px;
        font-weight: bold;
        color: #0a66c2;
    }

    .card {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }

    .skill-tag {
        display: inline-block;
        background-color: #e7f3ff;
        color: #0a66c2;
        padding: 6px 12px;
        margin: 5px;
        border-radius: 10px;
    }

    .gap-tag {
        display: inline-block;
        background-color: #ffe7e7;
        color: red;
        padding: 6px 12px;
        margin: 5px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ------------------ HEADER ------------------ #
st.markdown('<div class="main-title">🚀 AI Onboarding Engine</div>', unsafe_allow_html=True)

# ------------------ SIDEBAR ------------------ #
with st.sidebar:
    st.header("📄 Upload")
    resume_file = st.file_uploader("Resume")
    jd_file = st.file_uploader("Job Description")

# ------------------ MAIN ------------------ #
if resume_file and jd_file:

    with st.spinner("Analyzing..."):

        resume_text = extract_resume_text(resume_file)
        jd_text = extract_jd_text(jd_file)

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(jd_text)

        gaps = find_skill_gap(resume_skills, jd_skills)
        graph = build_skill_graph()
        path = generate_learning_path(graph, gaps)
        reasoning = generate_reasoning(gaps)

        # 🎯 Hire Score
        score = int((len(resume_skills) / len(jd_skills)) * 100) if jd_skills else 0
        score = min(score, 100)

        # ⏱️ Time Estimation
        total_time, time_breakdown = estimate_learning_time(path)

        # 📚 Courses
        courses = recommend_courses(gaps)

    # ------------------ SCORE ------------------ #
    st.markdown("### 🎯 Hire Readiness Score")
    st.progress(score / 100)
    st.write(f"**{score}% match with job requirements**")

    # ------------------ LAYOUT ------------------ #
    col1, col2 = st.columns(2)

    # -------- LEFT -------- #
    with col1:
        st.markdown("### 👤 Skills")
        html = '<div class="card">'
        for s in resume_skills:
            html += f'<span class="skill-tag">{s}</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("### ❌ Gaps")
        html = '<div class="card">'
        for g in gaps:
            html += f'<span class="gap-tag">{g}</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # -------- RIGHT -------- #
    with col2:
        st.markdown("### 🧭 Learning Path")
        html = '<div class="card">'
        for i, p in enumerate(path):
            html += f"<p><b>Step {i+1}:</b> {p}</p>"
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("### 🧠 Reasoning")
        html = '<div class="card">'
        for r in reasoning:
            html += f"<p>👉 {r}</p>"
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # ------------------ GRAPH ------------------ #
    st.markdown("### 🔥 Skill Graph")
    graph_file = visualize_graph(graph, highlight_nodes=gaps)
    st.components.v1.html(open(graph_file, "r").read(), height=450)

    # ------------------ PROGRESS ------------------ #
    st.markdown("### 📊 Skill Match Breakdown")
    for skill in jd_skills[:10]:
        if skill.lower() in [s.lower() for s in resume_skills]:
            st.progress(1.0, text=f"{skill} ✅")
        else:
            st.progress(0.3, text=f"{skill} ❌")

    # ------------------ TIME ESTIMATION ------------------ #
    st.markdown("### ⏱️ Learning Time Estimate")
    st.write(f"**Total Time Required: {total_time} hours**")

    for skill, t in time_breakdown.items():
        st.write(f"{skill}: {t} hrs")

    # ------------------ COURSES ------------------ #
    st.markdown("### 📚 Recommended Courses")
    for skill, course in courses.items():
        st.write(f"👉 {skill}: {course}")

    # ------------------ CHATBOT ------------------ #
    st.markdown("### 🤖 AI Career Mentor")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Ask career advice...")

    if user_input:
        response = mentor_chat(user_input)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", response))

    for sender, msg in st.session_state.chat_history:
        st.write(f"**{sender}:** {msg}")

else:
    st.info("Upload both files to start")
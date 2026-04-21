import streamlit as st
import sys, os, time, json, datetime
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

from database.emotion_store import (
    init_db, create_session, log_emotion,
    get_emotion_timeline, get_session_emotions)
from recommender.context_engine import ContextAwareRecommender
from collections import Counter
import plotly.graph_objects as go

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="EmoSense — Emotion Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# ── Session State Init ────────────────────────────────────────
defaults = {
    'active_module':    'overview',
    'user_name':        '',
    'user_id':          None,
    'all_sessions':     [],
    'current_session':  None,
    'permission_given': False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Emotion Meta ──────────────────────────────────────────────
EMOTION_META = {
    'happy':    {'color':'#F59E0B','light':'#FEF3C7','icon':'😊','text':'Happy'},
    'sad':      {'color':'#3B82F6','light':'#DBEAFE','icon':'😢','text':'Sad'},
    'angry':    {'color':'#EF4444','light':'#FEE2E2','icon':'😠','text':'Angry'},
    'neutral':  {'color':'#6B7280','light':'#F3F4F6','icon':'😐','text':'Neutral'},
    'fear':     {'color':'#8B5CF6','light':'#EDE9FE','icon':'😨','text':'Fear'},
    'fearful':  {'color':'#8B5CF6','light':'#EDE9FE','icon':'😨','text':'Fearful'},
    'surprise': {'color':'#06B6D4','light':'#CFFAFE','icon':'😲','text':'Surprise'},
    'surprised':{'color':'#06B6D4','light':'#CFFAFE','icon':'😲','text':'Surprised'},
    'disgust':  {'color':'#10B981','light':'#D1FAE5','icon':'🤢','text':'Disgust'},
    'calm':     {'color':'#14B8A6','light':'#CCFBF1','icon':'😌','text':'Calm'},
}

def get_dominant(readings):
    if not readings: return 'neutral'
    return Counter(r['emotion'] for r in readings).most_common(1)[0][0]

def get_avg_conf(readings):
    if not readings: return 0
    return sum(r['confidence'] for r in readings) / len(readings)

def clean_layout(fig, height=260):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#6B7280', size=11),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6',
                     zeroline=False,
                     tickfont=dict(size=10, color='#9CA3AF'))
    fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6',
                     zeroline=False,
                     tickfont=dict(size=10, color='#9CA3AF'))
    return fig

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #F8F7F4 !important;
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer { visibility: hidden; }

.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}

[data-testid="stSidebar"] {
    background: #1C1C1E !important;
    border-right: none !important;
}

.sidebar-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: #FFFFFF;
    line-height: 1;
    padding: 1.5rem 0 0.3rem 0;
}

.sidebar-tagline {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.nav-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 1rem 0 0.4rem 0;
}

.user-chip {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
}

.user-chip-name {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: #FFFFFF;
}

.user-chip-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: rgba(255,255,255,0.35);
    margin-top: 0.2rem;
}

.page-hdr {
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 2px solid #E5E5E7;
}

.page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #1C1C1E;
    line-height: 1.1;
}

.page-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #9CA3AF;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

.card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 1.4rem;
    border: 1px solid #E5E5E7;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04),
                0 4px 12px rgba(0,0,0,0.04);
}

.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.05rem;
    color: #1C1C1E;
    margin-bottom: 0.2rem;
}

.card-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #9CA3AF;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.stat-tile {
    background: white;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #E5E5E7;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.stat-tile-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}

.stat-val {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: #1C1C1E;
    line-height: 1;
    margin: 0.3rem 0;
}

.stat-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #9CA3AF;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.stat-icon { font-size: 1.3rem; margin-bottom: 0.3rem; }

.hero-dark {
    background: #1C1C1E;
    border-radius: 22px;
    padding: 2.2rem 2.8rem;
    color: white;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.5rem;
}

.hero-dark::after {
    content: '🧠';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.1;
}

.hero-greeting {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.hero-name {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: white;
    line-height: 1.1;
}

.hero-sub {
    font-family: 'DM Sans', sans-serif;
    color: rgba(255,255,255,0.45);
    font-size: 0.88rem;
    margin-top: 0.5rem;
}

.sess-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    border: 1px solid #E5E5E7;
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.55rem;
    transition: all 0.2s;
}

.sess-row:hover {
    border-color: #1C1C1E;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.sess-num {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #D1D5DB;
    width: 2rem;
}

.sess-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.88rem;
    color: #1C1C1E;
}

.sess-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #9CA3AF;
    margin-top: 0.1rem;
}

.emo-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.75rem;
    border-radius: 50px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 0.78rem;
}

.reco-card {
    background: white;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    border: 1px solid #E5E5E7;
    border-left: 4px solid #1C1C1E;
    margin-bottom: 0.7rem;
    transition: all 0.2s;
}

.reco-card:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.07);
    transform: translateX(3px);
}

.reco-type {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
    font-weight: 500;
}

.reco-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #1C1C1E;
    font-size: 0.92rem;
    margin-bottom: 0.45rem;
}

.reco-item {
    font-size: 0.8rem;
    color: #6B7280;
    padding: 0.18rem 0 0.18rem 1rem;
    position: relative;
}

.reco-item::before {
    content: '→';
    position: absolute;
    left: 0;
    color: #D1D5DB;
}

.perm-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #F8F7F4;
    border: 1px solid #E5E5E7;
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin: 0.5rem 0;
}

.perm-strong {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #1C1C1E;
    font-size: 0.88rem;
}

.perm-sub {
    font-family: 'DM Sans', sans-serif;
    color: #6B7280;
    font-size: 0.78rem;
    margin-top: 0.1rem;
}

.detect-box {
    background: white;
    border-radius: 22px;
    padding: 2.5rem;
    border: 1px solid #E5E5E7;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
}

.detect-timer {
    font-family: 'DM Serif Display', serif;
    font-size: 6rem;
    color: #1C1C1E;
    line-height: 1;
}

.detect-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #9CA3AF;
    margin-top: 0.5rem;
}

.dot-trail {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 0.7rem 0;
}

.dot-e {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    transition: transform 0.15s;
    cursor: default;
}

.dot-e:hover { transform: scale(1.2); }

.divider {
    height: 1px;
    background: #E5E5E7;
    margin: 1.4rem 0;
}

.tip-row {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid #F3F4F6;
}

.tip-icon { font-size: 1.1rem; }

.tip-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    color: #1C1C1E;
}

.tip-desc {
    font-size: 0.76rem;
    color: #9CA3AF;
    margin-top: 0.1rem;
}

.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
    border: 1.5px solid #E5E5E7 !important;
    background: white !important;
    color: #1C1C1E !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
}

.stButton > button:hover {
    border-color: #1C1C1E !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    transform: translateY(-1px) !important;
}

.stSelectbox > div > div {
    background: white !important;
    border: 1.5px solid #E5E5E7 !important;
    border-radius: 10px !important;
}

.stTextInput > div > div > input {
    background: white !important;
    border: 1.5px solid #E5E5E7 !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #F3F4F6; }
::-webkit-scrollbar-thumb {
    background: #D1D5DB; border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:

    st.markdown("""
    <div class="sidebar-logo">EmoSense</div>
    <div class="sidebar-tagline">
        Emotion Intelligence System
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.user_name:
        st.markdown(
            '<div class="nav-label">Setup</div>',
            unsafe_allow_html=True)
        name = st.text_input(
            "Name", placeholder="Your name...",
            label_visibility="collapsed")
        if st.button("Enter →") and name.strip():
            st.session_state.user_name = name.strip()
            st.session_state.user_id = (
                name.strip().lower().replace(" ","_"))
            st.rerun()
        st.stop()

    # User chip
    total_s = len(st.session_state.all_sessions)
    total_r = sum(len(s['readings'])
                  for s in st.session_state.all_sessions)
    st.markdown(f"""
    <div class="user-chip">
        <div class="user-chip-name">
            👤 {st.session_state.user_name}
        </div>
        <div class="user-chip-sub">
            {total_s} sessions · {total_r} readings
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav
    st.markdown(
        '<div class="nav-label">Modules</div>',
        unsafe_allow_html=True)

    MODULES = [
        ("🏠", "overview",        "Overview"),
        ("🎥", "detection",       "Detection"),
        ("📊", "analytics",       "Daily Analytics"),
        ("🎯", "recommendations", "Recommendations"),
        ("📋", "sessions",        "All Sessions"),
        ("⚙️", "settings",       "Settings"),
    ]

    for icon, key, label in MODULES:
        if st.button(f"{icon}  {label}", key=f"nav_{key}"):
            st.session_state.active_module = key
            st.rerun()

    # Quick dominant
    all_r = [r for s in st.session_state.all_sessions
             for r in s['readings']]
    if all_r:
        dom  = get_dominant(all_r)
        meta = EMOTION_META.get(dom, EMOTION_META['neutral'])
        st.markdown(f"""
        <div style="margin-top:1.5rem;
             background:rgba(255,255,255,0.06);
             border-radius:12px;padding:0.8rem 1rem;">
            <div style="font-family:'JetBrains Mono',
                 monospace;font-size:0.58rem;
                 color:rgba(255,255,255,0.3);
                 letter-spacing:0.15em;
                 text-transform:uppercase;">
                Overall Mood
            </div>
            <div style="font-family:'DM Serif Display',
                 serif;font-size:1.3rem;
                 color:white;margin-top:0.2rem;">
                {meta['icon']} {meta['text']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div style="height:1rem"></div>',
        unsafe_allow_html=True)
    if st.button("↩ Switch User"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()


# ══════════════════════════════════════════════════════════════
# MODULE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
if st.session_state.active_module == 'overview':

    sessions    = st.session_state.all_sessions
    all_readings = [r for s in sessions for r in s['readings']]

    hour = datetime.datetime.now().hour
    greeting = ("Good morning" if hour < 12
                else "Good afternoon" if hour < 17
                else "Good evening")

    if all_readings:
        dom   = get_dominant(all_readings)
        meta  = EMOTION_META.get(dom, EMOTION_META['neutral'])
        h_sub = (f"Across {len(sessions)} sessions, "
                 f"you've been mostly "
                 f"{meta['icon']} {meta['text']}")
    else:
        h_sub = ("No sessions yet — go to Detection "
                 "to record your first session")

    st.markdown(f"""
    <div class="hero-dark">
        <div class="hero-greeting">{greeting}</div>
        <div class="hero-name">
            {st.session_state.user_name}
        </div>
        <div class="hero-sub">{h_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    avg_c      = get_avg_conf(all_readings)
    unique_emo = len(set(
        r['emotion'] for r in all_readings))

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, lbl, color in [
        (c1,"🗓️",str(len(sessions)),
         "Sessions","#1C1C1E"),
        (c2,"📊",str(len(all_readings)),
         "Total Readings","#3B82F6"),
        (c3,"🎯",f"{avg_c*100:.0f}%",
         "Avg Confidence","#10B981"),
        (c4,"🌈",str(unique_emo),
         "Emotions Seen","#F59E0B"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-tile">
                <div class="stat-tile-bar"
                     style="background:{color}">
                </div>
                <div class="stat-icon">{icon}</div>
                <div class="stat-val">{val}</div>
                <div class="stat-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True)

    if sessions and all_readings:
        cl, cr = st.columns([1.3, 1])

        with cl:
            st.markdown("""
            <div class="card-title">
                Emotion Distribution
            </div>
            <div class="card-sub">
                All sessions combined
            </div>
            """, unsafe_allow_html=True)

            counts = Counter(
                r['emotion'] for r in all_readings)
            emos   = list(counts.keys())
            vals   = list(counts.values())
            colors = [EMOTION_META.get(
                e, EMOTION_META['neutral'])['color']
                for e in emos]
            lights = [EMOTION_META.get(
                e, EMOTION_META['neutral'])['light']
                for e in emos]

            fig = go.Figure(go.Bar(
                x=vals, y=emos, orientation='h',
                marker=dict(
                    color=lights,
                    line=dict(color=colors, width=2)),
                text=vals, textposition='outside',
                textfont=dict(
                    family='DM Sans', size=11,
                    color='#6B7280'),
            ))
            clean_layout(fig, 280)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(
                fig, use_container_width=True,
                config={'displayModeBar': False})

        with cr:
            st.markdown("""
            <div class="card-title">Recent Sessions</div>
            <div class="card-sub">Latest activity</div>
            """, unsafe_allow_html=True)

            for i, s in enumerate(
                    reversed(sessions[-5:])):
                n    = len(sessions) - i
                dom  = get_dominant(s['readings'])
                meta = EMOTION_META.get(
                    dom, EMOTION_META['neutral'])
                conf = get_avg_conf(s['readings'])
                st.markdown(f"""
                <div class="sess-row">
                    <div style="display:flex;
                         align-items:center;gap:0.8rem;">
                        <div class="sess-num">
                            {n:02d}
                        </div>
                        <div>
                            <div class="sess-title">
                                {s['label']}
                            </div>
                            <div class="sess-meta">
                                {len(s['readings'])} readings ·
                                {conf*100:.0f}% conf ·
                                {s['timestamp']}
                            </div>
                        </div>
                    </div>
                    <span class="emo-pill"
                        style="background:{meta['light']};
                               color:{meta['color']}">
                        {meta['icon']} {meta['text']}
                    </span>
                </div>
                """, unsafe_allow_html=True)

        if len(sessions) >= 2:
            st.markdown(
                '<div class="divider"></div>',
                unsafe_allow_html=True)
            st.markdown("""
            <div class="card-title">
                Confidence Across Sessions
            </div>
            <div class="card-sub">
                Detection reliability per session
            </div>
            """, unsafe_allow_html=True)

            x  = [f"S{i+1}" for i in range(len(sessions))]
            yc = [get_avg_conf(s['readings'])*100
                  for s in sessions]
            sc = [EMOTION_META.get(
                get_dominant(s['readings']),
                EMOTION_META['neutral'])['color']
                for s in sessions]

            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=x, y=yc,
                mode='lines+markers',
                line=dict(color='#1C1C1E', width=2.5),
                marker=dict(
                    size=9, color=sc,
                    line=dict(color='white', width=2)),
                fill='tozeroy',
                fillcolor='rgba(28,28,30,0.05)',
            ))
            clean_layout(fig3, 180)
            fig3.update_yaxes(
                range=[0,105],
                title_text="Confidence %")
            st.plotly_chart(
                fig3, use_container_width=True,
                config={'displayModeBar': False})

    else:
        st.markdown("""
        <div class="card" style="text-align:center;
             padding:3rem 2rem;">
            <div style="font-size:3rem;
                 margin-bottom:1rem;">📭</div>
            <div class="card-title">
                No sessions recorded yet
            </div>
            <div style="color:#9CA3AF;font-size:0.88rem;
                 margin-top:0.5rem;">
                Go to <strong>Detection</strong> to record
                your first 30-second session
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Start Detection"):
            st.session_state.active_module = 'detection'
            st.rerun()


# ══════════════════════════════════════════════════════════════
# MODULE 2 — DETECTION
# ══════════════════════════════════════════════════════════════
elif st.session_state.active_module == 'detection':

    st.markdown("""
    <div class="page-hdr">
        <div class="page-title">Detection</div>
        <div class="page-sub">
            30-second multimodal emotion recording
        </div>
    </div>
    """, unsafe_allow_html=True)

    sessions = st.session_state.all_sessions
    n_sess   = len(sessions)

    cl, cr = st.columns([1.4, 1])

    with cl:
        if not st.session_state.permission_given:
            st.markdown("""
            <div class="detect-box">
                <div style="font-size:2.5rem;
                     margin-bottom:0.8rem">🔐</div>
                <div style="font-family:'DM Serif Display',
                     serif;font-size:1.7rem;
                     color:#1C1C1E;margin-bottom:0.5rem;">
                    Permission Required
                </div>
                <div style="color:#6B7280;font-size:0.88rem;
                     margin-bottom:1.5rem;
                     max-width:360px;margin-left:auto;
                     margin-right:auto;line-height:1.6;">
                    EmoSense needs camera and microphone
                    access to detect emotions during the
                    30-second session.
                </div>
            """, unsafe_allow_html=True)

            for icon, strong, sub in [
                ("📷","Camera Access",
                 "Facial expression analysis"),
                ("🎤","Microphone Access",
                 "Voice emotion detection"),
                ("🔒","Local Only",
                 "Data never leaves your device"),
            ]:
                st.markdown(f"""
                <div class="perm-row">
                    <span style="font-size:1.4rem">
                        {icon}
                    </span>
                    <div>
                        <div class="perm-strong">
                            {strong}
                        </div>
                        <div class="perm-sub">{sub}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(
                '<div style="height:0.8rem"></div>',
                unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                        "✓ Grant Permission",
                        use_container_width=True):
                    st.session_state.permission_given = True
                    st.rerun()
            with c2:
                if st.button(
                        "✕ Deny",
                        use_container_width=True):
                    st.warning("Camera & mic required.")

        else:
            st.markdown(f"""
            <div class="detect-box">
                <div style="font-family:'JetBrains Mono',
                     monospace;font-size:0.65rem;
                     color:#9CA3AF;letter-spacing:0.2em;
                     text-transform:uppercase;
                     margin-bottom:0.8rem;">
                    Session {n_sess + 1} Ready
                </div>
                <div class="detect-timer">30</div>
                <div class="detect-status">
                    seconds · face + voice detection
                </div>
                <div style="background:#F3F4F6;
                     border-radius:50px;height:5px;
                     margin:1.2rem 0;">
                    <div style="width:100%;height:100%;
                         background:#1C1C1E;
                         border-radius:50px;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                '<div style="height:0.8rem"></div>',
                unsafe_allow_html=True)

            if st.button(
                    f"▶  Start Session {n_sess+1}  "
                    f"(30 seconds)",
                    use_container_width=True):

                with st.spinner(
                        "Loading AI models..."):
                    from inference.realtime_pipeline \
                        import RealtimePipeline
                    pipeline = RealtimePipeline()

                new_sid = create_session(
                    st.session_state.user_id
                    or 'default')

                status = st.empty()
                status.info(
                    "✅ Ready! Webcam window opening... "
                    "Look at the camera naturally.")
                time.sleep(1)

                with st.spinner(
                        "🎥 Recording... "
                        "Watch the webcam window!"):
                    readings = (
                        pipeline.run_timed_session(
                            duration=30,
                            session_id=new_sid))

                if readings:
                    dom  = get_dominant(readings)
                    meta = EMOTION_META.get(
                        dom, EMOTION_META['neutral'])

                    st.session_state.all_sessions\
                        .append({
                        'session_id': new_sid,
                        'label':      f"Session {n_sess+1}",
                        'readings':   readings,
                        'timestamp':  (
                            datetime.datetime.now()
                            .strftime("%H:%M")),
                        'dominant':   dom,
                    })

                    status.success(
                        f"✅ Session {n_sess+1} complete! "
                        f"{len(readings)} readings · "
                        f"Dominant: "
                        f"{meta['icon']} {meta['text']}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    status.error(
                        "❌ No face detected. Check "
                        "lighting and try again.")

    with cr:
        st.markdown("""
        <div class="card-title">Recorded Sessions</div>
        <div class="card-sub">This run</div>
        """, unsafe_allow_html=True)

        if sessions:
            for i, s in enumerate(sessions):
                dom  = get_dominant(s['readings'])
                meta = EMOTION_META.get(
                    dom, EMOTION_META['neutral'])
                conf = get_avg_conf(s['readings'])
                st.markdown(f"""
                <div class="sess-row">
                    <div style="display:flex;
                         align-items:center;gap:0.8rem;">
                        <div class="sess-num">
                            {i+1:02d}
                        </div>
                        <div>
                            <div class="sess-title">
                                {s['label']}
                            </div>
                            <div class="sess-meta">
                                {len(s['readings'])} readings ·
                                {conf*100:.0f}% ·
                                {s['timestamp']}
                            </div>
                        </div>
                    </div>
                    <span class="emo-pill"
                        style="background:{meta['light']};
                               color:{meta['color']}">
                        {meta['icon']} {meta['text']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:2rem;
                 color:#9CA3AF;font-size:0.85rem;">
                No sessions yet.<br>
                Start your first above.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(
            '<div class="divider"></div>',
            unsafe_allow_html=True)

        st.markdown("""
        <div class="card-title">Recording Tips</div>
        """, unsafe_allow_html=True)

        for icon, title, desc in [
            ("💡","Good Lighting",
             "Face a light source"),
            ("📏","Distance",
             "30–60 cm from camera"),
            ("🎭","Be Natural",
             "Don't pose, just be yourself"),
            ("🔇","Quiet Space",
             "Reduce background noise"),
            ("⏱️","Multiple Sessions",
             "3+ sessions = better insights"),
        ]:
            st.markdown(f"""
            <div class="tip-row">
                <span class="tip-icon">{icon}</span>
                <div>
                    <div class="tip-title">{title}</div>
                    <div class="tip-desc">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MODULE 3 — ANALYTICS
# ══════════════════════════════════════════════════════════════
elif st.session_state.active_module == 'analytics':

    st.markdown("""
    <div class="page-hdr">
        <div class="page-title">Daily Analytics</div>
        <div class="page-sub">
            Emotion patterns and trend analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

    sessions    = st.session_state.all_sessions
    all_readings = [r for s in sessions
                    for r in s['readings']]

    if not all_readings:
        st.markdown("""
        <div class="card" style="text-align:center;
             padding:3rem;">
            <div style="font-size:3rem">📊</div>
            <div class="card-title"
                 style="margin-top:1rem;">
                No data to analyze
            </div>
            <div style="color:#9CA3AF;margin-top:0.5rem;">
                Complete at least one detection session
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    counts  = Counter(r['emotion'] for r in all_readings)
    dom     = counts.most_common(1)[0][0]
    d_meta  = EMOTION_META.get(dom, EMOTION_META['neutral'])
    avg_c   = get_avg_conf(all_readings)

    # Stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:{d_meta['color']}">
            </div>
            <div style="font-size:2rem">
                {d_meta['icon']}
            </div>
            <div class="stat-val">{d_meta['text']}</div>
            <div class="stat-lbl">Dominant Emotion</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:#3B82F6"></div>
            <div style="font-size:2rem">📈</div>
            <div class="stat-val">
                {avg_c*100:.1f}%
            </div>
            <div class="stat-lbl">Avg Confidence</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:#10B981"></div>
            <div style="font-size:2rem">🎬</div>
            <div class="stat-val">{len(sessions)}</div>
            <div class="stat-lbl">Total Sessions</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True)

    # Charts row
    ca, cb = st.columns(2)
    emos   = list(counts.keys())
    vals   = list(counts.values())
    pcts   = [v/sum(vals)*100 for v in vals]
    colors = [EMOTION_META.get(
        e, EMOTION_META['neutral'])['color']
        for e in emos]
    lights = [EMOTION_META.get(
        e, EMOTION_META['neutral'])['light']
        for e in emos]

    with ca:
        st.markdown("""
        <div class="card-title">Emotion Frequency</div>
        <div class="card-sub">
            How often each emotion appeared
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Bar(
            x=emos, y=pcts,
            marker=dict(
                color=lights,
                line=dict(color=colors, width=2)),
            text=[f"{p:.0f}%" for p in pcts],
            textposition='outside',
            textfont=dict(
                family='DM Sans', size=11,
                color='#6B7280'),
        ))
        clean_layout(fig, 250)
        fig.update_yaxes(
            range=[0, max(pcts)*1.25],
            title_text="% of readings")
        st.plotly_chart(
            fig, use_container_width=True,
            config={'displayModeBar': False})

    with cb:
        st.markdown("""
        <div class="card-title">
            Emotion Composition
        </div>
        <div class="card-sub">
            Share of total readings
        </div>
        """, unsafe_allow_html=True)

        fig2 = go.Figure(go.Pie(
            labels=[
                f"{EMOTION_META.get(e,EMOTION_META['neutral'])['icon']} {e}"
                for e in emos],
            values=vals,
            hole=0.52,
            marker=dict(
                colors=colors,
                line=dict(color='white', width=3)),
            textfont=dict(family='DM Sans', size=11),
        ))
        fig2.update_layout(
            height=250,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans', color='#6B7280'),
            showlegend=True,
            legend=dict(
                font=dict(
                    family='DM Sans',
                    size=10, color='#6B7280'),
                bgcolor='rgba(0,0,0,0)',
            ),
        )
        st.plotly_chart(
            fig2, use_container_width=True,
            config={'displayModeBar': False})

    # Per session bar
    if len(sessions) >= 2:
        st.markdown(
            '<div class="divider"></div>',
            unsafe_allow_html=True)
        st.markdown("""
        <div class="card-title">
            Session-by-Session Breakdown
        </div>
        <div class="card-sub">
            Dominant emotion and confidence per session
        </div>
        """, unsafe_allow_html=True)

        xlabels, yconf, bcolors, icons = [], [], [], []
        for i, s in enumerate(sessions):
            de   = get_dominant(s['readings'])
            meta = EMOTION_META.get(
                de, EMOTION_META['neutral'])
            xlabels.append(f"S{i+1}")
            yconf.append(
                get_avg_conf(s['readings'])*100)
            bcolors.append(meta['color'])
            icons.append(meta['icon'])

        fig3 = go.Figure(go.Bar(
            x=xlabels, y=yconf,
            marker=dict(
                color=bcolors,
                line=dict(color='white', width=2),
                opacity=0.85),
            text=[f"{e}<br>{c:.0f}%"
                  for e, c in zip(icons, yconf)],
            textposition='outside',
            textfont=dict(family='DM Sans', size=11),
        ))
        clean_layout(fig3, 210)
        fig3.update_yaxes(
            range=[0, 115],
            title_text="Confidence %")
        st.plotly_chart(
            fig3, use_container_width=True,
            config={'displayModeBar': False})

    # Full trail
    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True)
    st.markdown("""
    <div class="card-title">Full Emotion Trail</div>
    <div class="card-sub">
        Every reading across all sessions
    </div>
    """, unsafe_allow_html=True)

    dots = '<div class="dot-trail">'
    for r in all_readings:
        e      = r['emotion']
        meta   = EMOTION_META.get(e, EMOTION_META['neutral'])
        bg     = meta['light']
        icon   = meta['icon']
        conf   = r['confidence'] * 100
        dots  += (
            f'<div class="dot-e" '
            f'style="background:{bg};" '
            f'title="{e} — {conf:.0f}%">'
            f'{icon}</div>')
    dots += '</div>'
    st.markdown(dots, unsafe_allow_html=True)

    # Confidence wave
    confs  = [r['confidence']*100 for r in all_readings]
    ecols  = [EMOTION_META.get(
        r['emotion'], EMOTION_META['neutral'])['color']
        for r in all_readings]

    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=list(range(1, len(confs)+1)),
        y=confs,
        mode='lines+markers',
        line=dict(color='#1C1C1E', width=1.5),
        marker=dict(
            size=6, color=ecols,
            line=dict(color='white', width=1.5)),
        fill='tozeroy',
        fillcolor='rgba(28,28,30,0.05)',
    ))
    clean_layout(fig4, 180)
    fig4.update_yaxes(
        range=[0, 105], title_text="Confidence %")
    fig4.update_xaxes(title_text="Reading #")
    st.plotly_chart(
        fig4, use_container_width=True,
        config={'displayModeBar': False})


# ══════════════════════════════════════════════════════════════
# MODULE 4 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
elif st.session_state.active_module == 'recommendations':

    st.markdown("""
    <div class="page-hdr">
        <div class="page-title">Recommendations</div>
        <div class="page-sub">
            Context-aware personalized suggestions
        </div>
    </div>
    """, unsafe_allow_html=True)

    sessions = st.session_state.all_sessions
    if not sessions:
        st.markdown("""
        <div class="card" style="text-align:center;
             padding:3rem;">
            <div style="font-size:3rem">🎯</div>
            <div class="card-title"
                 style="margin-top:1rem;">
                No data yet
            </div>
            <div style="color:#9CA3AF;margin-top:0.5rem;">
                Complete detection sessions first
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Selector
    opts = ["All Sessions Combined"] + [
        f"{s['label']} — {s['timestamp']}"
        for s in sessions
    ]
    sel = st.selectbox(
        "Analyze which session?", opts, index=0)

    if sel == "All Sessions Combined":
        target_sid = sessions[-1]['session_id']
        all_r      = [r for s in sessions
                      for r in s['readings']]
        label      = "All Sessions Combined"
    else:
        idx        = opts.index(sel) - 1
        target_sid = sessions[idx]['session_id']
        all_r      = sessions[idx]['readings']
        label      = sessions[idx]['label']

    if not all_r:
        st.warning("No readings in selected session.")
        st.stop()

    rec    = ContextAwareRecommender()
    result = rec.analyze_context(target_sid)
    ctx    = result.get('context', {})

    dom    = get_dominant(all_r)
    meta   = EMOTION_META.get(dom, EMOTION_META['neutral'])
    avg_c  = get_avg_conf(all_r)
    traj   = ctx.get('trajectory', 'stable')
    recent = ctx.get('recent_emotion', dom)
    r_meta = EMOTION_META.get(
        recent, EMOTION_META['neutral'])

    traj_color = {
        'improving':'#10B981',
        'declining':'#EF4444',
        'stable':   '#6B7280'
    }.get(traj, '#6B7280')
    traj_icon = {
        'improving':'📈','declining':'📉',
        'stable':'➡️'}.get(traj,'➡️')

    # Stat tiles
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:{meta['color']}">
            </div>
            <div style="font-size:2rem">
                {meta['icon']}
            </div>
            <div class="stat-val">{meta['text']}</div>
            <div class="stat-lbl">Dominant Emotion</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:{r_meta['color']}">
            </div>
            <div style="font-size:2rem">
                {r_meta['icon']}
            </div>
            <div class="stat-val">{r_meta['text']}</div>
            <div class="stat-lbl">Recent Emotion</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-bar"
                 style="background:{traj_color}">
            </div>
            <div style="font-size:2rem">
                {traj_icon}
            </div>
            <div class="stat-val"
                 style="font-size:1.7rem;">
                {traj.capitalize()}
            </div>
            <div class="stat-lbl">Mood Trajectory</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True)

    # Summary
    st.markdown(f"""
    <div style="background:{meta['light']};
         border:1px solid {meta['color']}30;
         border-left:4px solid {meta['color']};
         border-radius:14px;padding:1.2rem 1.5rem;
         margin-bottom:1.2rem;">
        <div style="font-family:'JetBrains Mono',
             monospace;font-size:0.6rem;
             color:{meta['color']};
             letter-spacing:0.15em;
             text-transform:uppercase;
             margin-bottom:0.4rem;">
            Analysis — {label}
        </div>
        <div style="font-family:'DM Sans',sans-serif;
             font-size:0.95rem;color:#1C1C1E;
             line-height:1.6;">
            {result['summary']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Reco cards
    st.markdown("""
    <div class="card-title">Personalized Suggestions</div>
    <div class="card-sub">
        Based on your emotional context
    </div>
    """, unsafe_allow_html=True)

    T_COLORS = {
        "music":"#8B5CF6","activity":"#10B981",
        "content":"#3B82F6","wellbeing":"#F59E0B"}
    T_ICONS  = {
        "music":"🎵","activity":"🏃",
        "content":"📺","wellbeing":"💚"}

    recos = result.get('recommendations', [])
    if recos:
        rcols = st.columns(min(len(recos), 2))
        for i, r in enumerate(recos):
            rtype  = r['type']
            color  = T_COLORS.get(rtype, '#1C1C1E')
            icon   = T_ICONS.get(rtype, '💡')
            items  = ''.join([
                f'<div class="reco-item">{it}</div>'
                for it in r['items']
            ])
            with rcols[i % 2]:
                st.markdown(f"""
                <div class="reco-card"
                     style="border-left-color:{color}">
                    <div class="reco-type"
                         style="color:{color}">
                        {icon} {rtype.upper()}
                    </div>
                    <div class="reco-title">
                        {r['title']}
                    </div>
                    {items}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(
            "Not enough data for recommendations yet.")

    # Download
    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True)

    lines = [
        f"EmoSense Report — {label}",
        f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f"User: {st.session_state.user_name}",
        "=" * 40,
        f"Dominant : {meta['text']}",
        f"Recent   : {r_meta['text']}",
        f"Trend    : {traj.capitalize()}",
        f"Readings : {len(all_r)}",
        f"Conf     : {avg_c*100:.1f}%",
        "=" * 40, "",
        result['summary'], "",
        "RECOMMENDATIONS:",
    ]
    for r in recos:
        lines.append(
            f"\n[{r['type'].upper()}] {r['title']}")
        for item in r['items']:
            lines.append(f"  • {item}")

    st.download_button(
        "⬇ Download Report",
        "\n".join(lines),
        file_name=(
            f"emosense_{st.session_state.user_name}_"
            f"{datetime.datetime.now():%Y%m%d_%H%M}.txt"),
        mime="text/plain",
        use_container_width=True)


# ══════════════════════════════════════════════════════════════
# MODULE 5 — ALL SESSIONS
# ══════════════════════════════════════════════════════════════
elif st.session_state.active_module == 'sessions':

    st.markdown("""
    <div class="page-hdr">
        <div class="page-title">All Sessions</div>
        <div class="page-sub">
            Complete history of all recorded sessions
        </div>
    </div>
    """, unsafe_allow_html=True)

    sessions = st.session_state.all_sessions
    if not sessions:
        st.markdown("""
        <div class="card" style="text-align:center;
             padding:3rem;">
            <div style="font-size:3rem">📋</div>
            <div class="card-title"
                 style="margin-top:1rem;">
                No sessions recorded
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    for i, sess in enumerate(sessions):
        dom   = get_dominant(sess['readings'])
        meta  = EMOTION_META.get(
            dom, EMOTION_META['neutral'])
        reads = sess['readings']
        avg_c = get_avg_conf(reads)
        cnts  = Counter(r['emotion'] for r in reads)

        with st.expander(
                f"Session {i+1}  ·  "
                f"{meta['icon']} {meta['text']}  ·  "
                f"{sess['timestamp']}  ·  "
                f"{len(reads)} readings",
                expanded=(i == len(sessions)-1)):

            ca, cb = st.columns([1, 1.4])

            with ca:
                st.markdown(f"""
                <div class="stat-tile"
                     style="margin-bottom:1rem;">
                    <div class="stat-tile-bar"
                         style="background:{meta['color']}">
                    </div>
                    <div style="display:flex;
                         align-items:center;gap:0.8rem;">
                        <div style="font-size:2rem">
                            {meta['icon']}
                        </div>
                        <div>
                            <div class="stat-val"
                                 style="font-size:1.5rem">
                                {meta['text']}
                            </div>
                            <div class="stat-lbl">
                                Dominant
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                sm1, sm2 = st.columns(2)
                with sm1:
                    st.metric("Readings", len(reads))
                with sm2:
                    st.metric(
                        "Confidence",
                        f"{avg_c*100:.1f}%")

                st.markdown("""
                <div class="card-sub"
                     style="margin-top:1rem;">
                    Emotion Breakdown
                </div>
                """, unsafe_allow_html=True)

                for emo, cnt in cnts.most_common():
                    m   = EMOTION_META.get(
                        emo, EMOTION_META['neutral'])
                    pct = cnt / len(reads) * 100
                    st.markdown(f"""
                    <div style="display:flex;
                         align-items:center;
                         gap:0.7rem;padding:0.35rem 0;
                         border-bottom:1px solid #F3F4F6;">
                        <span>{m['icon']}</span>
                        <span style="flex:1;
                             font-size:0.83rem;
                             color:#1C1C1E;">
                            {m['text']}
                        </span>
                        <div style="width:70px;
                             background:#F3F4F6;
                             border-radius:50px;
                             height:5px;">
                            <div style="width:{pct}%;
                                 height:100%;
                                 background:{m['color']};
                                 border-radius:50px;">
                            </div>
                        </div>
                        <span style="font-family:
                             'JetBrains Mono',monospace;
                             font-size:0.65rem;
                             color:#9CA3AF;
                             width:2.2rem;text-align:right;">
                            {pct:.0f}%
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

            with cb:
                confs  = [r['confidence']*100
                          for r in reads]
                ecols  = [EMOTION_META.get(
                    r['emotion'],
                    EMOTION_META['neutral'])['color']
                    for r in reads]

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(confs)+1)),
                    y=confs,
                    mode='lines+markers',
                    line=dict(
                        color=meta['color'], width=2),
                    marker=dict(
                        size=7, color=ecols,
                        line=dict(
                            color='white', width=1.5)),
                    fill='tozeroy',
                    fillcolor=f"{meta['color']}15",
                ))
                clean_layout(fig, 200)
                fig.update_yaxes(
                    range=[0,105],
                    title_text="Confidence %")
                fig.update_xaxes(
                    title_text="Reading #")
                st.plotly_chart(
                    fig, use_container_width=True,
                    config={'displayModeBar': False})

                st.markdown("""
                <div class="card-sub">Emotion Trail</div>
                """, unsafe_allow_html=True)
                dots = '<div class="dot-trail">'
                for r in reads:
                    m    = EMOTION_META.get(
                        r['emotion'],
                        EMOTION_META['neutral'])
                    c    = r['confidence'] * 100
                    bg   = m['light']
                    ico  = m['icon']
                    emo  = r['emotion']
                    dots += (
                        f'<div class="dot-e" '
                        f'style="background:{bg}" '
                        f'title="{emo} {c:.0f}%">'
                        f'{ico}</div>')
                dots += '</div>'
                st.markdown(dots, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MODULE 6 — SETTINGS
# ══════════════════════════════════════════════════════════════
elif st.session_state.active_module == 'settings':

    st.markdown("""
    <div class="page-hdr">
        <div class="page-title">Settings</div>
        <div class="page-sub">
            System configuration and information
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="card-title">System Info</div>
        <div class="card-sub">Model performance</div>
        """, unsafe_allow_html=True)

        for label, val, sub in [
            ("Face Model","EfficientNet-B3",
             "69.98% accuracy"),
            ("Audio Model","Wav2Vec2 + BiLSTM",
             "92.36% accuracy"),
            ("Fusion Method","Late Fusion",
             "Confidence-weighted"),
            ("Detection Interval","1.5 seconds",
             "Per reading"),
            ("Session Duration","30 seconds",
             "Per session"),
            ("Storage","SQLite",
             "Local database"),
        ]:
            st.markdown(f"""
            <div style="display:flex;
                 justify-content:space-between;
                 align-items:center;
                 padding:0.75rem 0;
                 border-bottom:1px solid #F3F4F6;">
                <div>
                    <div style="font-family:'DM Sans',
                         sans-serif;font-weight:500;
                         font-size:0.86rem;color:#1C1C1E;">
                        {label}
                    </div>
                    <div style="font-family:'JetBrains Mono',
                         monospace;font-size:0.6rem;
                         color:#9CA3AF;margin-top:0.1rem;">
                        {sub}
                    </div>
                </div>
                <div style="font-family:'JetBrains Mono',
                     monospace;font-size:0.75rem;
                     color:#1C1C1E;font-weight:500;">
                    {val}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card-title">Current User</div>
        <div class="card-sub">Session information</div>
        """, unsafe_allow_html=True)

        sessions = st.session_state.all_sessions
        st.markdown(f"""
        <div style="padding:0.5rem 0 1rem 0;">
            <div style="font-family:'DM Sans',sans-serif;
                 font-size:0.8rem;color:#9CA3AF;
                 margin-bottom:0.2rem;">Name</div>
            <div style="font-family:'DM Serif Display',
                 serif;font-size:1.6rem;color:#1C1C1E;">
                {st.session_state.user_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

        s1, s2 = st.columns(2)
        with s1:
            st.metric("Sessions", len(sessions))
        with s2:
            st.metric("Total Readings", sum(
                len(s['readings']) for s in sessions))

        st.markdown(
            '<div style="height:0.8rem"></div>',
            unsafe_allow_html=True)

        if sessions:
            if st.button(
                    "🗑 Clear All Sessions",
                    use_container_width=True):
                st.session_state.all_sessions  = []
                st.session_state.current_session = None
                st.success("Cleared.")
                st.rerun()

        if st.button(
                "↩ Switch User",
                use_container_width=True):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()

        st.markdown(
            '<div class="divider"></div>',
            unsafe_allow_html=True)

        st.markdown("""
        <div class="card-title">How to Use</div>
        """, unsafe_allow_html=True)

        for num, title, desc in [
            ("1","Detection",
             "Record a 30-second session"),
            ("2","Repeat",
             "Record multiple sessions over time"),
            ("3","Analytics",
             "View patterns across sessions"),
            ("4","Recommendations",
             "Get personalized AI suggestions"),
        ]:
            st.markdown(f"""
            <div style="display:flex;gap:1rem;
                 padding:0.55rem 0;
                 border-bottom:1px solid #F3F4F6;">
                <div style="font-family:'DM Serif Display',
                     serif;font-size:1.4rem;
                     color:#D1D5DB;width:1.3rem;">
                    {num}
                </div>
                <div>
                    <div style="font-family:'DM Sans',
                         sans-serif;font-weight:600;
                         font-size:0.86rem;color:#1C1C1E;">
                        {title}
                    </div>
                    <div style="font-size:0.76rem;
                         color:#9CA3AF;margin-top:0.1rem;">
                        {desc}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

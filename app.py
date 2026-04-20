# app.py — streamlit run app.py
import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Code Snippet Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS — white theme ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

#MainMenu, footer, header { visibility: hidden; }

html, body, .stApp {
    background-color: #F4F6FA !important;
    font-family: 'Inter', sans-serif !important;
    color: #0F1C2E !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Main area padding ── */
[data-testid="stMainBlockContainer"] {
    padding: 2rem 2.5rem 4rem !important;
    max-width: 1100px !important;
    background: #F4F6FA !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important;
    color: #0F1C2E !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84rem !important;
    padding: 11px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #3D7EF5 !important;
    box-shadow: 0 0 0 3px rgba(61,126,245,0.12) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #94A3B8 !important; }
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label { display: none !important; }

/* ── Primary button ── */
[data-testid="stButton"] button {
    background: #3D7EF5 !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 20px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(61,126,245,0.25) !important;
}
[data-testid="stButton"] button:hover {
    background: #2563EB !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(61,126,245,0.35) !important;
}
[data-testid="stButton"] button:disabled {
    background: #CBD5E1 !important;
    color: #94A3B8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Shortcut / secondary buttons (inside columns) ── */
div[data-testid="column"] [data-testid="stButton"] button {
    background: #FFFFFF !important;
    color: #475569 !important;
    border: 1.5px solid #CBD5E1 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
}
div[data-testid="column"] [data-testid="stButton"] button:hover {
    border-color: #3D7EF5 !important;
    color: #3D7EF5 !important;
    background: #EFF6FF !important;
    transform: none !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #F8FAFC !important;
    color: #475569 !important;
    border: 1.5px solid #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    width: 100% !important;
    box-shadow: none !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #3D7EF5 !important;
    color: #3D7EF5 !important;
    background: #EFF6FF !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div {
    background: #E2E8F0 !important;
    border-radius: 6px !important;
    height: 5px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #3D7EF5, #22C797) !important;
    border-radius: 6px !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
}

/* ── Code block ── */
[data-testid="stCode"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background: #F8FAFF !important;
}
pre { background: #F8FAFF !important; color: #0F1C2E !important; }

/* ── Tabs ── */
[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
}
[aria-selected="true"] { color: #3D7EF5 !important; font-weight: 600 !important; }
[data-baseweb="tab-list"] { border-bottom-color: #E2E8F0 !important; }

/* ── Expander ── */
[data-testid="stExpander"] summary {
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    color: #475569 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}

/* ── Selectbox ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #F8FAFC !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #0F1C2E !important;
    font-size: 0.82rem !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] * { color: #3D7EF5 !important; }

/* divider */
hr { border-color: #E2E8F0 !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────
from backend.rag.repo_loader      import load_repository
from backend.agents.snippet_agent import generate_snippet

# ── Session state ─────────────────────────────────────────────
for k, v in [("repo_data", None), ("output", None),
              ("logs", []), ("history", []),
              ("pipeline_step", 0), ("active_module", "load")]:
    if k not in st.session_state:
        st.session_state[k] = v

repo_done   = st.session_state.repo_data is not None
output_done = st.session_state.output    is not None


# ════════════════════════════════════════════════════════════
# SIDEBAR — Separate module cards for each action
# ════════════════════════════════════════════════════════════
PIPELINE_STEPS = [
    ("RAG Retrieval",    "Semantic search"),
    ("Prompt Builder",   "Framework context"),
    ("Ollama Generate",  "llama3.1 local"),
    ("AST Validate",     "Syntax check"),
    ("Smell Detector",   "Quality analysis"),
    ("Quality Scorer",   "4-axis scoring"),
]

def build_sidebar():
    active_pipe = st.session_state.pipeline_step
    active_mod  = st.session_state.active_module

    steps_html = ""
    for i, (name, desc) in enumerate(PIPELINE_STEPS):
        n = i + 1
        if active_pipe == n:   state = "active"
        elif output_done:      state = "done"
        elif active_pipe > n:  state = "done"
        else:                  state = "idle"

        icon_html = ""
        if state == "done":
            icon_html = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>'
        elif state == "active":
            icon_html = '<div class="spin-dot"></div>'
        else:
            icon_html = f'<span class="pipe-num">{n}</span>'

        steps_html += f"""
        <div class="pipe-row {state}">
          <div class="pipe-icon">{icon_html}</div>
          <div class="pipe-info">
            <div class="pipe-name">{name}</div>
            <div class="pipe-desc">{desc}</div>
          </div>
          {'<div class="pipe-active-label">RUNNING</div>' if state == "active" else ''}
        </div>
        {'<div class="pipe-connector ' + state + '"></div>' if n < 6 else ''}
        """

    # Module nav items
    modules = [
        ("load",     "01", "Load Repository",   "Clone + RAG index",      repo_done),
        ("generate", "02", "Generate Snippet",  "Intent-driven code gen", repo_done),
        ("history",  "03", "History",           "Past generations",       len(st.session_state.history) > 0),
        ("settings", "04", "Settings",          "Model configuration",    True),
    ]

    nav_html = ""
    for mod_id, num, title, desc, enabled in modules:
        is_active = active_mod == mod_id
        cls = "nav-active" if is_active else ("nav-disabled" if not enabled else "nav-item")
        badge = f'<span class="nav-badge">{len(st.session_state.history)}</span>' if mod_id == "history" and st.session_state.history else ""
        done_dot = '<span class="nav-done-dot"></span>' if (mod_id == "load" and repo_done) or (mod_id == "generate" and output_done) else ""
        nav_html += f"""
        <div class="{cls}" onclick="window.parent.postMessage({{type:'streamlit:setComponentValue', value:'{mod_id}'}}, '*')" data-mod="{mod_id}">
          <div class="nav-num">{num}</div>
          <div class="nav-text">
            <div class="nav-title">{title} {done_dot} {badge}</div>
            <div class="nav-desc">{desc}</div>
          </div>
          <svg class="nav-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </div>
        """

    hist_html = ""
    if st.session_state.history:
        for h in reversed(st.session_state.history[-4:]):
            tc = "#16A34A" if h["score"] >= 80 else "#D97706" if h["score"] >= 60 else "#DC2626"
            hist_html += f"""
            <div class="hist-row">
              <div class="hist-top">
                <span class="hist-fw">{h['framework'].upper()}</span>
                <span class="hist-score" style="color:{tc};background:{tc}18">{h['score']}/100</span>
              </div>
              <div class="hist-intent">{h['intent'][:52]}...</div>
            </div>"""
    else:
        hist_html = '<div class="hist-empty">No generations yet</div>'

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
* {{ margin:0;padding:0;box-sizing:border-box; }}
html,body {{ background:#FFFFFF;font-family:'Inter',sans-serif;overflow-x:hidden; }}

.sidebar {{ padding:0;height:100%;display:flex;flex-direction:column; }}

/* ── Brand ── */
.brand {{
    padding:20px 20px 16px;
    border-bottom:1px solid #F1F5F9;
    display:flex;align-items:center;gap:10px;
}}
.brand-icon {{
    width:36px;height:36px;border-radius:10px;
    background:linear-gradient(135deg,#3D7EF5,#2050C8);
    display:flex;align-items:center;justify-content:center;
    flex-shrink:0;
}}
.brand-icon svg {{ width:18px;height:18px; }}
.brand-name {{
    font-size:0.95rem;font-weight:700;color:#0F1C2E;line-height:1.1;
}}
.brand-sub {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.58rem;color:#94A3B8;letter-spacing:0.08em;margin-top:2px;
}}
.brand-badge {{
    margin-left:auto;
    font-family:'JetBrains Mono',monospace;
    font-size:0.55rem;color:#16A34A;
    background:#F0FDF4;border:1px solid #86EFAC;
    border-radius:10px;padding:2px 8px;white-space:nowrap;
}}

/* ── Section label ── */
.sec-label {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.56rem;font-weight:600;
    letter-spacing:0.18em;text-transform:uppercase;
    color:#94A3B8;padding:16px 20px 8px;
}}

/* ── Module nav cards ── */
.nav-item, .nav-active, .nav-disabled {{
    display:flex;align-items:center;gap:12px;
    padding:10px 16px;margin:2px 8px;
    border-radius:10px;cursor:pointer;
    transition:all 0.15s;border:1.5px solid transparent;
}}
.nav-item {{ background:#FFFFFF; }}
.nav-item:hover {{ background:#F0F7FF;border-color:#BFDBFE; }}
.nav-active {{
    background:#EFF6FF;border-color:#93C5FD;
    box-shadow:0 1px 4px rgba(61,126,245,0.15);
}}
.nav-disabled {{ opacity:0.4;cursor:not-allowed; }}

.nav-num {{
    width:28px;height:28px;border-radius:7px;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    font-family:'JetBrains Mono',monospace;font-size:0.62rem;font-weight:600;
    background:#F1F5F9;color:#64748B;
    transition:all 0.15s;
}}
.nav-active .nav-num {{ background:#3D7EF5;color:#fff; }}

.nav-text {{ flex:1;min-width:0; }}
.nav-title {{
    font-size:0.8rem;font-weight:600;color:#1E293B;
    display:flex;align-items:center;gap:5px;
}}
.nav-active .nav-title {{ color:#1D4ED8; }}
.nav-disabled .nav-title {{ color:#94A3B8; }}

.nav-desc {{ font-size:0.68rem;color:#94A3B8;margin-top:1px; }}
.nav-active .nav-desc {{ color:#60A5FA; }}

.nav-arrow {{ color:#CBD5E1;flex-shrink:0;transition:color 0.15s; }}
.nav-active .nav-arrow {{ color:#3D7EF5; }}
.nav-item:hover .nav-arrow {{ color:#3D7EF5; }}

.nav-done-dot {{
    width:6px;height:6px;border-radius:50%;
    background:#16A34A;display:inline-block;flex-shrink:0;
}}
.nav-badge {{
    background:#3D7EF5;color:#fff;
    font-size:0.55rem;font-weight:700;
    padding:1px 6px;border-radius:10px;
    font-family:'JetBrains Mono',monospace;
}}

/* ── Agent Pipeline ── */
.pipe-list {{ padding:0 12px; }}

.pipe-row {{
    display:flex;align-items:center;gap:10px;
    padding:8px 10px;border-radius:8px;
    transition:all 0.3s;
}}
.pipe-row.idle   {{ opacity:0.35; }}
.pipe-row.done   {{ opacity:0.75; }}
.pipe-row.active {{
    background:#EFF6FF;
    border:1px solid #BFDBFE;
    box-shadow:0 0 12px rgba(61,126,245,0.12);
    animation:rowGlow 2s ease-in-out infinite;
    opacity:1;
}}
@keyframes rowGlow {{
    0%,100% {{ box-shadow:0 0 12px rgba(61,126,245,0.1); }}
    50%      {{ box-shadow:0 0 20px rgba(61,126,245,0.22); }}
}}

.pipe-icon {{
    width:26px;height:26px;border-radius:7px;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    background:#F1F5F9;border:1px solid #E2E8F0;
    transition:all 0.3s;
}}
.pipe-row.active .pipe-icon {{
    background:#EFF6FF;border-color:#93C5FD;
    box-shadow:0 0 8px rgba(61,126,245,0.3);
}}
.pipe-row.done .pipe-icon {{
    background:#F0FDF4;border-color:#86EFAC;
}}

.pipe-num {{ font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#94A3B8; }}
.spin-dot {{
    width:8px;height:8px;border-radius:50%;background:#3D7EF5;
    animation:dotPulse 1s ease-in-out infinite;
}}
@keyframes dotPulse {{
    0%,100%{{transform:scale(1);opacity:1}}
    50%{{transform:scale(1.5);opacity:0.6}}
}}

.pipe-info {{ flex:1;min-width:0; }}
.pipe-name {{ font-size:0.72rem;font-weight:600;color:#334155;transition:color 0.3s; }}
.pipe-row.active .pipe-name {{ color:#1D4ED8; }}
.pipe-row.done .pipe-name {{ color:#16A34A; }}
.pipe-desc {{ font-family:'JetBrains Mono',monospace;font-size:0.56rem;color:#CBD5E1;margin-top:1px; }}
.pipe-row.active .pipe-desc {{ color:#93C5FD; }}

.pipe-active-label {{
    font-family:'JetBrains Mono',monospace;font-size:0.54rem;
    color:#3D7EF5;letter-spacing:0.08em;flex-shrink:0;
    animation:labelBlink 1.2s ease-in-out infinite;
}}
@keyframes labelBlink {{ 0%,100%{{opacity:1}}50%{{opacity:0.4}} }}

.pipe-connector {{
    width:1px;height:6px;background:#E2E8F0;
    margin-left:23px;transition:background 0.4s;
}}
.pipe-connector.done   {{ background:#86EFAC; }}
.pipe-connector.active {{ background:#93C5FD; }}

/* ── History ── */
.hist-section {{ padding:0 12px 12px; }}
.hist-row {{
    padding:8px 10px;margin-bottom:4px;
    background:#F8FAFC;border:1px solid #F1F5F9;
    border-radius:8px;
}}
.hist-top {{ display:flex;align-items:center;justify-content:space-between;margin-bottom:3px; }}
.hist-fw {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.58rem;color:#94A3B8;letter-spacing:0.08em;
}}
.hist-score {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.62rem;font-weight:700;
    padding:1px 8px;border-radius:10px;
}}
.hist-intent {{ font-size:0.7rem;color:#475569;line-height:1.4; }}
.hist-empty {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.62rem;color:#CBD5E1;padding:8px 10px;
}}

/* ── Status footer ── */
.sidebar-footer {{
    margin-top:auto;padding:14px 20px;
    border-top:1px solid #F1F5F9;
    display:flex;align-items:center;gap:8px;
}}
.footer-dot {{ width:7px;height:7px;border-radius:50%;background:#16A34A;flex-shrink:0;animation:fpulse 2s infinite; }}
@keyframes fpulse {{ 0%,100%{{opacity:1}}50%{{opacity:0.4}} }}
.footer-text {{ font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#94A3B8; }}
.footer-text span {{ color:#3D7EF5;font-weight:600; }}
</style>
</head>
<body>
<div class="sidebar">

  <!-- Brand -->
  <div class="brand">
    <div class="brand-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5">
        <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
      </svg>
    </div>
    <div>
      <div class="brand-name">SnippetAgent</div>
      <div class="brand-sub">AI CODE GENERATOR</div>
    </div>
    <div class="brand-badge">LIVE</div>
  </div>

  <!-- Modules -->
  <div class="sec-label">Modules</div>
  <div style="margin-bottom:4px">
    {nav_html}
  </div>

  <!-- Agent Pipeline -->
  <div class="sec-label">Agent Pipeline</div>
  <div class="pipe-list">
    {steps_html}
  </div>

  <!-- History -->
  <div class="sec-label">Recent</div>
  <div class="hist-section">
    {hist_html}
  </div>

  <!-- Footer -->
  <div class="sidebar-footer">
    <div class="footer-dot"></div>
    <div class="footer-text">Ollama &nbsp;·&nbsp; <span>{llm_model}</span> &nbsp;·&nbsp; LOCAL</div>
  </div>

</div>
</body>
</html>
""", height=900, scrolling=True)


# ════════════════════════════════════════════════════════════
# HTML COMPONENTS — Main content
# ════════════════════════════════════════════════════════════

def render_header():
    repo_done_   = st.session_state.repo_data is not None
    output_done_ = st.session_state.output is not None
    cur_step     = 4 if output_done_ else 2 if repo_done_ else 1

    steps = [
        ("01", "Load Repository", "Clone + RAG"),
        ("02", "Generate",        "Intent-driven"),
        ("03", "Validate",        "AST + Smells"),
        ("04", "Review",          "Score + Export"),
    ]
    pills = ""
    for i, (num, title, desc) in enumerate(steps):
        s = i + 1
        if s < cur_step:   cls = "done"
        elif s == cur_step: cls = "active"
        else:              cls = "idle"
        icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#16A34A" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>' if cls == "done" else f'<span class="pnum">{num}</span>'
        pills += f"""
        <div class="pill {cls}">
          <div class="pill-icon">{icon}</div>
          <div>
            <div class="pill-title">{title}</div>
            <div class="pill-desc">{desc}</div>
          </div>
        </div>
        {"<div class='pill-sep'><div class='pill-line'></div></div>" if i < 3 else ""}
        """

    st.markdown(f"""
<style>
@keyframes hdrFadeUp {{ from{{opacity:0;transform:translateY(10px)}} to{{opacity:1;transform:translateY(0)}} }}
@keyframes livePulse {{ 0%,100%{{box-shadow:0 0 0 0 rgba(22,163,74,0.4)}} 50%{{box-shadow:0 0 0 6px rgba(22,163,74,0)}} }}

.csa-hdr {{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:16px;
    padding:32px 40px 28px;
    margin-bottom:20px;
    position:relative;overflow:hidden;
    box-shadow:0 1px 4px rgba(0,0,0,0.06);
}}
.csa-hdr::before {{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,#3D7EF5 0%,#22C797 60%,#A78BFA 100%);
}}
.csa-hdr-badge {{
    display:inline-flex;align-items:center;gap:7px;
    background:#F0FDF4;border:1px solid #86EFAC;
    border-radius:20px;padding:4px 14px;
    font-family:'JetBrains Mono',monospace;
    font-size:0.64rem;color:#15803D;letter-spacing:0.08em;
    margin-bottom:16px;animation:hdrFadeUp 0.4s ease both;
}}
.csa-live-dot {{
    width:7px;height:7px;border-radius:50%;background:#16A34A;
    animation:livePulse 2s ease-in-out infinite;display:inline-block;
}}
.csa-hdr-title {{
    font-family:'Inter',sans-serif;
    font-size:2.6rem;font-weight:700;
    letter-spacing:-0.04em;line-height:1;
    color:#0F1C2E;margin-bottom:10px;
    animation:hdrFadeUp 0.4s ease 0.08s both;
}}
.csa-hdr-title .tb {{ color:#3D7EF5; }}
.csa-hdr-title .tg {{ color:#22C797; }}
.csa-hdr-sub {{
    font-family:'JetBrains Mono',monospace;
    font-size:0.68rem;color:#94A3B8;
    letter-spacing:0.12em;text-transform:uppercase;
    animation:hdrFadeUp 0.4s ease 0.16s both;
}}
.csa-hdr-sub span {{ color:#CBD5E1;margin:0 8px; }}
.csa-stats {{
    display:flex;gap:0;margin-top:24px;
    border:1px solid #E2E8F0;border-radius:10px;
    overflow:hidden;width:fit-content;background:#F8FAFC;
    animation:hdrFadeUp 0.4s ease 0.24s both;
}}
.csa-stat {{
    padding:11px 24px;border-right:1px solid #E2E8F0;
    display:flex;flex-direction:column;gap:3px;
}}
.csa-stat:last-child {{ border-right:none; }}
.csa-sv {{ font-size:1.4rem;font-weight:700;color:#0F1C2E;line-height:1; }}
.csa-sv-b {{ color:#3D7EF5; }}
.csa-sv-g {{ color:#22C797; }}
.csa-sl {{ font-family:'JetBrains Mono',monospace;font-size:0.56rem;color:#94A3B8;letter-spacing:0.1em;text-transform:uppercase; }}

/* Pipeline pills */
.pill-row {{
    display:flex;align-items:stretch;
    background:#FFFFFF;border:1px solid #E2E8F0;
    border-radius:12px;overflow:hidden;padding:4px;gap:3px;
    margin-bottom:24px;
    box-shadow:0 1px 3px rgba(0,0,0,0.05);
}}
.pill {{
    flex:1;display:flex;align-items:center;gap:10px;
    padding:11px 14px;border-radius:9px;
    transition:all 0.3s;
}}
.pill.idle   {{ opacity:0.4; }}
.pill.done   {{ background:#F0FDF4; }}
.pill.active {{
    background:#EFF6FF;
    border:1px solid #BFDBFE;
    box-shadow:0 2px 8px rgba(61,126,245,0.12);
}}
.pill-icon {{
    width:30px;height:30px;flex-shrink:0;
    border-radius:7px;display:flex;align-items:center;justify-content:center;
    background:#F1F5F9;border:1px solid #E2E8F0;
    transition:all 0.3s;
}}
.pill.active .pill-icon {{ background:#EFF6FF;border-color:#93C5FD; }}
.pill.done   .pill-icon {{ background:#F0FDF4;border-color:#86EFAC; }}
.pnum {{ font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#94A3B8; }}
.pill.active .pnum {{ color:#3D7EF5; }}
.pill-title {{ font-size:0.76rem;font-weight:600;color:#475569;line-height:1.2; }}
.pill.active .pill-title {{ color:#1D4ED8; }}
.pill.done   .pill-title {{ color:#15803D; }}
.pill-desc {{ font-family:'JetBrains Mono',monospace;font-size:0.56rem;color:#CBD5E1;margin-top:1px; }}
.pill.active .pill-desc {{ color:#93C5FD; }}
.pill.done   .pill-desc {{ color:#86EFAC; }}
.pill-sep {{ width:16px;flex-shrink:0;display:flex;align-items:center; }}
.pill-line {{ width:100%;height:1px;background:#E2E8F0; }}
</style>
<div class="csa-hdr">
  <div class="csa-hdr-badge"><span class="csa-live-dot"></span> OLLAMA &nbsp;·&nbsp; LLAMA3.1 &nbsp;·&nbsp; RUNS LOCALLY &nbsp;·&nbsp; FREE</div>
  <div class="csa-hdr-title"><span class="tb">Code</span>Snippet<span class="tg">Agent</span></div>
  <div class="csa-hdr-sub">RAG Retrieval <span>|</span> AST Validation <span>|</span> Smell Detection <span>|</span> Quality Scoring</div>
  <div class="csa-stats">
    <div class="csa-stat"><span class="csa-sv csa-sv-b">6</span><span class="csa-sl">Pipeline Steps</span></div>
    <div class="csa-stat"><span class="csa-sv">100</span><span class="csa-sl">Quality Score</span></div>
    <div class="csa-stat"><span class="csa-sv csa-sv-b">3x</span><span class="csa-sl">AST Retries</span></div>
    <div class="csa-stat"><span class="csa-sv csa-sv-g">Free</span><span class="csa-sl">No API Key</span></div>
  </div>
</div>
<div class="pill-row">{pills}</div>
""", unsafe_allow_html=True)


def render_module_card(icon_svg, title, subtitle, color="#3D7EF5"):
    st.markdown(f"""
<style>
.mod-card {{
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:14px;
    padding:20px 24px 16px;
    margin-bottom:16px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    position:relative;overflow:hidden;
}}
.mod-card::before {{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:{color};
}}
.mod-card-head {{
    display:flex;align-items:center;gap:12px;margin-bottom:14px;
}}
.mod-card-icon {{
    width:38px;height:38px;border-radius:10px;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    background:{color}18;border:1px solid {color}30;
}}
.mod-card-title {{ font-size:0.96rem;font-weight:700;color:#0F1C2E; }}
.mod-card-sub   {{ font-size:0.72rem;color:#94A3B8;margin-top:2px;font-family:'JetBrains Mono',monospace; }}
</style>
<div class="mod-card">
  <div class="mod-card-head">
    <div class="mod-card-icon">{icon_svg}</div>
    <div>
      <div class="mod-card-title">{title}</div>
      <div class="mod-card-sub">{subtitle}</div>
    </div>
  </div>
""", unsafe_allow_html=True)


def close_module_card():
    st.markdown("</div>", unsafe_allow_html=True)


def render_scores(score, smells, syntax_valid, context_used, framework):
    axes = [
        ("Syntax Valid",    score["Syntax Valid"],    25),
        ("Smell Free",      score["Smell Free"],      25),
        ("Context Aligned", score["Context Aligned"], 25),
        ("Completeness",    score["Completeness"],    25),
    ]
    total = score["total"]

    def col(v, mx):
        r = v / mx
        if r == 1.0: return "#16A34A","#F0FDF4","#86EFAC"
        if r >= 0.6: return "#D97706","#FFFBEB","#FCD34D"
        return "#DC2626","#FEF2F2","#FCA5A5"

    cards = ""
    for label, val, mx in axes:
        c, bg, border = col(val, mx)
        pct = int(val / mx * 100)
        cards += f"""
        <div class="sc" style="background:{bg};border-color:{border}">
          <div class="sc-lbl">{label}</div>
          <div class="sc-val" style="color:{c}">{val}<span class="sc-mx">/{mx}</span></div>
          <div class="sc-bg"><div class="sc-bar" style="width:{pct}%;background:{c}"></div></div>
        </div>"""

    tc, tbg, tborder = col(total, 100)

    meta = [
        ("Syntax",    "Valid"    if syntax_valid  else "Error",   "#16A34A" if syntax_valid  else "#DC2626", "#F0FDF4" if syntax_valid else "#FEF2F2"),
        ("Context",   "RAG Used" if context_used  else "No RAG",  "#16A34A" if context_used  else "#D97706", "#F0FDF4" if context_used else "#FFFBEB"),
        ("Smells",    "None"     if not smells     else f"{len(smells)} Found", "#16A34A" if not smells else "#D97706", "#F0FDF4" if not smells else "#FFFBEB"),
        ("Framework", framework.upper(), "#3D7EF5","#EFF6FF"),
    ]
    chips = "".join(f"""
        <div class="chip" style="background:{bg};border-color:{c}30">
          <span class="chip-l" style="color:{c}88">{l}</span>
          <span class="chip-v" style="color:{c}">{v}</span>
        </div>""" for l,v,c,bg in meta)

    smell_html = ""
    if smells:
        tags = "".join(f'<span class="stag">{s}</span>' for s in smells)
        smell_html = f"""
        <div class="smell">
          <div class="smell-title">Code Smells Detected</div>
          <div class="smell-tags">{tags}</div>
        </div>"""

    st.markdown(f"""
<style>
@keyframes riseCard {{ from{{opacity:0;transform:translateY(10px)}} to{{opacity:1;transform:translateY(0)}} }}
.meta-row {{ display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px; }}
.chip {{
    display:inline-flex;align-items:center;gap:6px;
    border:1px solid;border-radius:20px;padding:4px 12px;font-size:0.72rem;
}}
.chip-l {{ font-weight:500; }}
.chip-v {{ font-weight:700; }}

.sc-grid {{ display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px; }}
.sc {{
    border:1px solid;border-radius:12px;padding:14px;
    display:flex;flex-direction:column;gap:8px;
    animation:riseCard 0.4s ease both;
    box-shadow:0 1px 3px rgba(0,0,0,0.04);
}}
.sc:nth-child(1){{animation-delay:.04s}} .sc:nth-child(2){{animation-delay:.08s}}
.sc:nth-child(3){{animation-delay:.12s}} .sc:nth-child(4){{animation-delay:.16s}}
.sc-lbl {{ font-size:0.6rem;color:#64748B;letter-spacing:0.08em;text-transform:uppercase;font-weight:600; }}
.sc-val {{ font-size:1.8rem;font-weight:700;line-height:1; }}
.sc-mx  {{ font-size:0.78rem;color:#94A3B8; }}
.sc-bg  {{ height:3px;background:#E2E8F0;border-radius:2px;overflow:hidden; }}
.sc-bar {{ height:100%;border-radius:2px;transition:width 1s ease; }}

.total {{
    background:{tbg};border:1px solid {tborder};
    border-radius:12px;padding:14px 20px;
    display:flex;align-items:center;justify-content:space-between;
    margin-bottom:12px;animation:riseCard 0.4s ease 0.2s both;
    box-shadow:0 1px 3px rgba(0,0,0,0.04);
}}
.total-l {{ display:flex;flex-direction:column;gap:3px; }}
.total-lbl {{ font-size:0.68rem;color:#64748B;text-transform:uppercase;letter-spacing:0.08em;font-weight:600; }}
.total-sub {{ font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#94A3B8; }}
.total-val {{ font-size:2.2rem;font-weight:700;color:{tc};line-height:1; }}
.total-den {{ font-size:0.9rem;color:#94A3B8; }}

.smell {{
    background:#FFFBEB;border:1px solid #FCD34D;border-left:3px solid #D97706;
    border-radius:10px;padding:12px 16px;margin-bottom:12px;
    animation:riseCard 0.4s ease 0.24s both;
}}
.smell-title {{ font-size:0.68rem;font-weight:700;color:#D97706;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px; }}
.smell-tags {{ display:flex;flex-wrap:wrap;gap:5px; }}
.stag {{
    font-family:'JetBrains Mono',monospace;font-size:0.6rem;
    color:#D97706;background:#FEF9EE;
    border:1px solid #FCD34D;border-radius:5px;padding:2px 8px;
}}
</style>
<div class="meta-row">{chips}</div>
<div class="sc-grid">{cards}</div>
<div class="total">
  <div class="total-l">
    <div class="total-lbl">Overall Quality Score</div>
    <div class="total-sub">4 axes &nbsp;·&nbsp; 25 pts each</div>
  </div>
  <div class="total-val">{total}<span class="total-den"> / 100</span></div>
</div>
{smell_html}
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# SIDEBAR RENDER
# ════════════════════════════════════════════════════════════
with st.sidebar:
    # Hidden selectboxes for config (controlled via sidebar HTML)
    llm_model   = st.selectbox("LLM",   ["llama3.1","llama3.2","llama3.2:1b","codellama","mistral"],   label_visibility="collapsed")
    embed_model = st.selectbox("Embed", ["nomic-embed-text","mxbai-embed-large"],                       label_visibility="collapsed")
    os.environ["LLM_MODEL"]   = llm_model
    os.environ["EMBED_MODEL"] = embed_model

    build_sidebar()

    if st.session_state.history:
        if st.button("Clear History", key="clrhist"):
            st.session_state.history = []
            st.rerun()


# ════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════
render_header()


# ════════════════════════════════════════════════════════════
# MODULE 01 — LOAD REPOSITORY
# ════════════════════════════════════════════════════════════
repo_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3D7EF5" stroke-width="2.5"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>'

render_module_card(
    repo_icon,
    "Load Repository",
    "Clone a GitHub repo and build the RAG index",
    "#3D7EF5"
)

cu, cb = st.columns([5, 1])
with cu:
    github_url = st.text_input("url", placeholder="https://github.com/username/repository")
with cb:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    load_btn = st.button("Load Repository", use_container_width=True)

st.markdown(
    '<p style="font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#94A3B8;'
    'letter-spacing:0.1em;text-transform:uppercase;margin:10px 0 6px;font-weight:600">Quick Start</p>',
    unsafe_allow_html=True
)
rc1, rc2, rc3 = st.columns(3)
REPOS = [
    ("vercel / next.js",    "https://github.com/vercel/next.js"),
    ("tiangolo / fastapi",  "https://github.com/tiangolo/fastapi"),
    ("expressjs / express", "https://github.com/expressjs/express"),
]
for col, (lbl, url) in zip([rc1, rc2, rc3], REPOS):
    with col:
        if st.button(lbl, key=f"r_{lbl}"):
            github_url = url

if load_btn and github_url and github_url.strip():
    prog = st.progress(0, text="Initialising...")
    sbox = st.empty()

    def on_prog(done, total):
        prog.progress(int(done / total * 100), text=f"Embedding  {done} / {total}  chunks")

    sbox.info("Cloning repository and building RAG index...")
    with st.spinner(""):
        res = load_repository(github_url.strip(), on_prog)

    if res["success"]:
        st.session_state.repo_data    = {"repo_id": res["repo_id"], "framework": res["framework"]}
        st.session_state.pipeline_step = 0
        prog.progress(100, text="Complete")
        sbox.success(f"Indexed {res['files_indexed']} chunks — Framework: {res['framework'].upper()} — ID: {res['repo_id']}")
        st.rerun()
    else:
        prog.empty()
        sbox.error(res["error"])

if repo_done:
    rd = st.session_state.repo_data
    st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;
    background:#F0FDF4;border:1px solid #86EFAC;border-left:3px solid #16A34A;
    border-radius:10px;padding:12px 16px;margin-top:10px;">
  <div style="width:8px;height:8px;border-radius:50%;background:#16A34A;flex-shrink:0;"></div>
  <span style="font-family:JetBrains Mono,monospace;font-size:0.74rem;color:#15803D;font-weight:700;letter-spacing:0.08em;">{rd['framework'].upper()}</span>
  <span style="font-size:0.8rem;color:#166534;font-weight:500;">Repository loaded and indexed</span>
  <span style="margin-left:auto;font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#86EFAC;">ID: {rd['repo_id']}</span>
</div>
""", unsafe_allow_html=True)

close_module_card()
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MODULE 02 — GENERATE SNIPPET
# ════════════════════════════════════════════════════════════
gen_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'

render_module_card(
    gen_icon,
    "Generate Snippet",
    "Describe your intent — agent matches your codebase style",
    "#8B5CF6"
)

if not repo_done:
    st.info("Load a repository in Module 01 to enable generation.")
else:
    INTENTS = [
        "Generate a user authentication server action with email and password validation",
        "Create a reusable Button component with loading state and size variants",
        "Write a REST API endpoint for paginated product listing with filters",
        "Generate a custom hook for fetching data with loading and error states",
        "Create a middleware function for JWT token validation and refresh",
        "Write a database connection utility with connection pooling",
    ]

    intent = st.text_area(
        "intent",
        placeholder="Describe the code you need in plain English...",
        height=90
    )

    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#94A3B8;'
        'letter-spacing:0.1em;text-transform:uppercase;margin:10px 0 6px;font-weight:600">Example Intents</p>',
        unsafe_allow_html=True
    )
    ic1, ic2 = st.columns(2)
    for i, ex in enumerate(INTENTS):
        with [ic1, ic2][i % 2]:
            short = ex[:54] + "..." if len(ex) > 54 else ex
            if st.button(short, key=f"ie_{i}"):
                intent = ex

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    gen_btn = st.button(
        "Generate Snippet",
        disabled=not bool(intent and intent.strip()),
        use_container_width=True,
        key="gen_main"
    )

    if gen_btn and intent and intent.strip():
        logs    = []
        log_box = st.empty()
        STEP_MAP = {
            "Step 1": 1, "RAG": 1, "Step 2": 2, "Prompt": 2,
            "Step 3": 3, "Generat": 3, "Ollama": 3,
            "Step 4": 4, "AST": 4, "Syntax": 4,
            "Step 5": 5, "Smell": 5, "Step 6": 6, "Scor": 6,
        }

        def log_fn(msg):
            logs.append(msg)
            log_box.code("\n".join(logs), language=None)
            for kw, step in STEP_MAP.items():
                if kw.lower() in msg.lower():
                    st.session_state.pipeline_step = step
                    break

        st.session_state.pipeline_step = 1
        result = None
        with st.spinner("Agent pipeline running..."):
            try:
                result = generate_snippet(
                    intent    = intent.strip(),
                    framework = st.session_state.repo_data["framework"],
                    repo_id   = st.session_state.repo_data["repo_id"],
                    log       = log_fn
                )
            except KeyError as e:
                log_box.empty()
                st.session_state.pipeline_step = 0
                st.error(
                    f"Ollama returned an unexpected response format (missing key: {e}). "
                    "Check that Ollama is running and the model is pulled. "
                    "Try: `ollama pull llama3.1` in your terminal."
                )
                st.stop()
            except Exception as e:
                log_box.empty()
                st.session_state.pipeline_step = 0
                st.error(f"Agent pipeline failed: {e}")
                st.stop()

        log_box.empty()
        st.session_state.pipeline_step = 0
        st.session_state.output        = result
        if result:
            st.session_state.logs = logs
            st.session_state.history.append({
                "intent":    intent.strip(),
                "framework": st.session_state.repo_data["framework"],
                "score":     result["quality_score"]["total"],
            })
        st.rerun()

close_module_card()
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MODULE 03 — OUTPUT & REVIEW
# ════════════════════════════════════════════════════════════
if st.session_state.output:
    out   = st.session_state.output
    score = out["quality_score"]

    review_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22C797" stroke-width="2.5"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>'
    render_module_card(
        review_icon,
        "Review Output",
        f"Quality score: {score['total']}/100  ·  Framework: {out['framework'].upper()}",
        "#22C797"
    )

    render_scores(
        score        = score,
        smells       = out["smells_detected"],
        syntax_valid = out["syntax_valid"],
        context_used = out["context_used"],
        framework    = out["framework"]
    )

    LANG = {"nextjs":"tsx","react":"tsx","express":"javascript",
            "nestjs":"typescript","fastapi":"python","django":"python"}
    lang = LANG.get(out["framework"], "javascript")
    ext  = "py" if lang == "python" else "tsx"

    if out.get("smell_fix"):
        t1, t2 = st.tabs(["Generated", "Auto-Fixed"])
        with t1:
            st.code(out["snippet"], language=lang, line_numbers=True)
        with t2:
            st.success("Refactored — detected smells resolved.")
            st.code(out["smell_fix"], language=lang, line_numbers=True)
    else:
        st.code(out["snippet"], language=lang, line_numbers=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    with a1:
        st.download_button("Download Snippet", data=out["snippet"],
                           file_name=f"snippet.{ext}", mime="text/plain",
                           use_container_width=True)
    with a2:
        if out.get("smell_fix"):
            st.download_button("Download Fixed", data=out["smell_fix"],
                               file_name=f"snippet_fixed.{ext}", mime="text/plain",
                               use_container_width=True)
    with a3:
        if st.button("Generate New", use_container_width=True, key="gen_new"):
            st.session_state.output        = None
            st.session_state.pipeline_step = 0
            st.rerun()

    if st.session_state.logs:
        with st.expander("Agent Execution Log"):
            st.code("\n".join(st.session_state.logs), language=None)

    close_module_card()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# MODULE 04 — SETTINGS
# ════════════════════════════════════════════════════════════
settings_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>'

render_module_card(settings_icon, "Settings", "Model configuration and system parameters", "#F59E0B")

sc1, sc2 = st.columns(2)
with sc1:
    st.markdown('<p style="font-size:0.72rem;font-weight:600;color:#64748B;margin-bottom:5px;">LLM Model</p>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;padding:9px 14px;font-family:JetBrains Mono,monospace;font-size:0.82rem;color:#0F1C2E;font-weight:600;">{llm_model}</div>', unsafe_allow_html=True)
with sc2:
    st.markdown('<p style="font-size:0.72rem;font-weight:600;color:#64748B;margin-bottom:5px;">Embed Model</p>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;padding:9px 14px;font-family:JetBrains Mono,monospace;font-size:0.82rem;color:#0F1C2E;font-weight:600;">{embed_model}</div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

cfg_data = [
    ("Chunk Size",       "500 characters"),
    ("Chunk Overlap",    "100 characters"),
    ("Embedding Dims",   "768 (nomic-embed-text)"),
    ("Top-K Retrieval",  "3 chunks"),
    ("Temperature",      "0.3 (deterministic)"),
    ("Max Tokens",       "800 per generation"),
    ("AST Retries",      "3 attempts max"),
    ("Smell Checks",     "Long method, duplicate, dead code, God class"),
]

config_html = "".join(f"""
<div style="display:flex;align-items:center;padding:8px 0;border-bottom:1px solid #F1F5F9;">
  <span style="font-size:0.76rem;font-weight:600;color:#475569;width:160px;flex-shrink:0;">{k}</span>
  <span style="font-family:JetBrains Mono,monospace;font-size:0.74rem;color:#3D7EF5;font-weight:600;">{v}</span>
</div>""" for k, v in cfg_data)

st.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:4px 14px 4px;margin-top:4px;">{config_html}</div>', unsafe_allow_html=True)

close_module_card()
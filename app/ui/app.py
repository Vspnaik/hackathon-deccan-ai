"""Talent Scout AI — Role Selection Gateway."""
import streamlit as st

st.set_page_config(
    page_title="Talent Scout AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f3ee; }
[data-testid="stHeader"] { background: #f5f3ee; }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 860px; padding-top: 2rem; }
.stButton > button { border-radius: 12px !important; font-weight: 600 !important; transition: all 0.2s !important; }

/* ── Nav ── */
.nav-bar { display: flex; align-items: center; justify-content: center; padding: 0.8rem 0; border-bottom: 1px solid #e0ddd6; margin-bottom: 3rem; }
.nav-logo { display: flex; align-items: center; gap: 0.7rem; }
.nav-icon { width: 40px; height: 40px; background: #1a1a2e; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #a3e635; font-size: 1.2rem; }
.nav-title { font-weight: 800; font-size: 1.15rem; color: #1a1a2e; }
.nav-sub { font-size: 0.65rem; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }

/* ── Hero ── */
.hero { text-align: center; margin-bottom: 3rem; }
.hero-badge { display: inline-block; background: #e8f5e0; color: #3d6b2e; padding: 0.35rem 1.1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 1.2rem; border: 1px solid #bce2a8; }
.hero h1 { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 900; color: #1a1a2e; line-height: 1.1; margin: 0 0 0.8rem; }
.hero h1 span { color: #65a30d; }
.hero p { color: #666; font-size: 1rem; line-height: 1.6; max-width: 520px; margin: 0 auto; }

/* ── Role Cards ── */
.role-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 2rem; }
.role-card { background: #fff; border: 2px solid #e0ddd6; border-radius: 20px; padding: 2.2rem 2rem; text-align: center; cursor: pointer; transition: all 0.25s; position: relative; overflow: hidden; }
.role-card:hover { border-color: #1a1a2e; transform: translateY(-4px); box-shadow: 0 12px 32px rgba(26,26,46,0.12); }
.role-card.hr:hover { border-color: #1a1a2e; }
.role-card.candidate:hover { border-color: #a3e635; }

.role-icon { width: 72px; height: 72px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 1.2rem; }
.role-icon.hr { background: #1a1a2e; }
.role-icon.cand { background: #e8f5e0; border: 2px solid #bce2a8; }

.role-card h2 { font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 800; color: #1a1a2e; margin: 0 0 0.5rem; }
.role-card p { color: #666; font-size: 0.88rem; line-height: 1.6; margin: 0 0 1.5rem; }

.role-badge { display: inline-block; padding: 0.25rem 0.7rem; border-radius: 20px; font-size: 0.72rem; font-weight: 600; margin-bottom: 1rem; }
.role-badge.hr { background: #1a1a2e; color: #a3e635; }
.role-badge.cand { background: #e8f5e0; color: #3d6b2e; border: 1px solid #bce2a8; }

.feature-list { list-style: none; padding: 0; margin: 0 0 1.5rem; text-align: left; }
.feature-list li { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.82rem; color: #555; margin-bottom: 0.5rem; }
.feature-list li::before { content: '✓'; color: #a3e635; font-weight: 700; flex-shrink: 0; margin-top: 0.05rem; }

.divider { display: flex; align-items: center; gap: 1rem; margin: 2.5rem 0; }
.divider hr { flex: 1; border: none; border-top: 1px solid #e0ddd6; }
.divider span { color: #bbb; font-size: 0.82rem; white-space: nowrap; }

.footer { text-align: center; color: #bbb; font-size: 0.78rem; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid #e0ddd6; }
</style>
""", unsafe_allow_html=True)

# ── Nav ──────────────────────────────────────────────────────────────────────
st.markdown("""<div class="nav-bar">
    <div class="nav-logo">
        <div class="nav-icon">⚡</div>
        <div>
            <div class="nav-title">Talent Scout</div>
            <div class="nav-sub">AI Sourcing & Engagement Agent</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""<div class="hero">
    <div class="hero-badge">✨ AI-Powered Talent Intelligence</div>
    <h1>Who are you <span>today?</span></h1>
    <p>Select your role to get started. Candidates build their profile and chat with our AI recruiter. HR teams run intelligent job-description analysis and candidate shortlisting.</p>
</div>""", unsafe_allow_html=True)

# ── Role Cards ───────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""<div class="role-card hr">
        <span class="role-badge hr">🏢 For Recruiters</span>
        <div class="role-icon hr">🔍</div>
        <h2>I'm HR / Recruiter</h2>
        <p>Source, rank and engage top candidates with AI-powered analysis of your job descriptions.</p>
        <ul class="feature-list">
            <li>Paste a JD and get a ranked shortlist instantly</li>
            <li>Match Score + Interest Score per candidate</li>
            <li>Expandable candidate breakdown with skill gaps</li>
            <li>Export to JSON / CSV for your ATS</li>
        </ul>
    </div>""", unsafe_allow_html=True)
    if st.button("Enter HR Dashboard →", key="go_hr", type="primary", use_container_width=True):
        st.switch_page("pages/3_HR_Dashboard.py")

with col2:
    st.markdown("""<div class="role-card candidate">
        <span class="role-badge cand">👤 For Candidates</span>
        <div class="role-icon cand">📋</div>
        <h2>I'm a Candidate</h2>
        <p>Build your profile, showcase your skills and projects, then chat with our AI to signal your interest level.</p>
        <ul class="feature-list">
            <li>Structured profile — experience, skills, projects</li>
            <li>AI-powered interest assessment chat</li>
            <li>Profile saved and matched against live JDs</li>
            <li>Get contacted when there's a strong match</li>
        </ul>
    </div>""", unsafe_allow_html=True)
    if st.button("Build My Profile →", key="go_candidate", use_container_width=True):
        st.switch_page("pages/1_Candidate_Profile.py")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""<div class="footer">
    Powered by Google Gemini · FastAPI · pgvector · Streamlit &nbsp;·&nbsp; All scores are for internal recruiter use only.
</div>""", unsafe_allow_html=True)

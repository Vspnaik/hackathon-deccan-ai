"""HR Recruiter Dashboard — Talent Scout AI."""
import streamlit as st, requests, json, pandas as pd

st.set_page_config(page_title="HR Dashboard | Talent Scout", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

API_URL = "http://localhost:8000"

SAMPLE_JDS = {
    "Senior Backend (Python)": "Senior Backend Engineer · Remote (EU/US time zones)\n\nWe're building an AI-native developer-tools product and need a senior backend engineer.\n\nWhat you'll do:\n- Architect and ship the core Python/FastAPI backend\n- Build scalable microservices with PostgreSQL and Redis\n- Drive performance and reliability across the platform\n\nYou should have:\n- 4-8 years of professional backend experience\n- Deep expertise in Python, FastAPI, and PostgreSQL\n- Experience with Redis, Docker, Kubernetes\n\nNice to have:\n- Fintech or SaaS background\n- Experience with Kafka or message queues\n\nSalary: 18-28 LPA · Notice ≤ 60 days · Bengaluru hybrid",
    "Staff ML Engineer": "Staff ML Engineer — applied LLMs\n\nJoin our AI team to build production ML systems.\n\nRequirements:\n- 5-10 years ML/AI experience\n- Python, PyTorch, TensorFlow\n- NLP, LLMs, Hugging Face\n- Bengaluru or Remote India\n- Salary 30-50 LPA",
    "Frontend React": "Senior Frontend Engineer · Remote\n\nOwn our web application end-to-end.\n\nRequired: React, TypeScript, Next.js\nNice to have: Design systems, Animation, Framer Motion\n\n5+ years · Remote OK · 20-35 LPA",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f3ee; }
[data-testid="stHeader"] { background: #f5f3ee; }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 1200px; padding-top: 0 !important; }
.stTextArea textarea { background: #fff !important; color: #1a1a2e !important; border: 1px solid #ddd !important; border-radius: 12px !important; font-size: 0.9rem !important; }
.stButton>button { border-radius: 10px !important; font-weight: 600 !important; }
div[data-testid="stExpander"] { border: none !important; background: transparent !important; }
div[data-testid="stExpander"] div[role="region"] { color: #1a1a2e !important; }

.nav-wrapper { background: #f5f3ee; border-bottom: 1px solid #e0ddd6; margin: -1rem -5rem 1.5rem -5rem; padding: 0.85rem 5rem; position: sticky; top: 0; z-index: 999; }
.nav-bar { display: flex; align-items: center; justify-content: space-between; max-width: 1200px; margin: 0 auto; }
.nav-logo { display: flex; align-items: center; gap: 0.6rem; }
.nav-icon { width: 36px; height: 36px; background: #1a1a2e; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #a3e635; font-size: 1.1rem; }
.nav-title { font-weight: 800; font-size: 1.1rem; color: #1a1a2e; }
.nav-sub { font-size: 0.65rem; color: #888; text-transform: uppercase; letter-spacing: 1.5px; }

.hero-badge { display: inline-block; background: #e8f5e0; color: #3d6b2e; padding: 0.35rem 1rem; border-radius: 20px; font-size: 0.8rem; font-weight: 500; margin-bottom: 1.5rem; }
.hero-title { font-family: 'Playfair Display', serif; font-size: 3.2rem; font-weight: 900; color: #1a1a2e; line-height: 1.1; margin-bottom: 0.5rem; }
.hero-green { color: #65a30d; }
.hero-desc { color: #666; font-size: 1rem; line-height: 1.6; margin: 1rem 0 1.5rem; max-width: 400px; }
.step-cards { display: flex; gap: 0.8rem; margin-top: 1rem; }
.step-card { border: 1px solid #ddd; border-radius: 12px; padding: 1rem; min-width: 120px; background: #fff; }
.step-num { font-size: 1.5rem; font-weight: 800; color: #1a1a2e; }
.step-text { font-size: 0.78rem; color: #666; margin-top: 0.3rem; }
.jd-section { background: #fff; border-radius: 16px; padding: 1.5rem; border: 1px solid #e0ddd6; }
.jd-label { font-size: 1.3rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.8rem; }
.char-count { font-size: 0.8rem; color: #999; margin-top: 0.3rem; }

.parsed-card { background: #fff; border: 1px solid #e0ddd6; border-radius: 16px; padding: 1.5rem; }
.parsed-header { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 600; }
.parsed-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 800; color: #1a1a2e; margin: 0.5rem 0; }
.parsed-desc { color: #666; font-size: 0.9rem; line-height: 1.5; margin: 0.5rem 0 1rem; }
.parsed-meta { display: flex; gap: 1.2rem; flex-wrap: wrap; margin: 0.8rem 0; font-size: 0.85rem; color: #555; }
.parsed-meta span { display: flex; align-items: center; gap: 0.3rem; }
.seniority-badge { background: #1a1a2e; color: #fff; padding: 0.25rem 0.8rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
.section-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 700; margin: 1rem 0 0.5rem; }
.skill-pill { display: inline-block; background: #1a1a2e; color: #fff; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin: 0.2rem; font-weight: 500; }
.skill-pill-nice { display: inline-block; background: #f0f0ea; color: #555; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin: 0.2rem; border: 1px solid #ddd; }
.skill-pill-missing { display: inline-block; background: #fef2f2; color: #dc2626; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; margin: 0.2rem; border: 1px solid #fca5a5; text-decoration: line-through; }

.shortlist-card { background: linear-gradient(135deg, #1a1a2e 40%, #4d7a22); border-radius: 16px; padding: 1.5rem; color: #fff; }
.shortlist-badge { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #a3e635; font-weight: 600; }
.shortlist-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 800; margin: 0.5rem 0; }
.shortlist-desc { color: #eee; font-size: 0.9rem; line-height: 1.5; }

.cand-table-container { background: #fff; border: 1px solid #e0ddd6; border-radius: 12px; margin-top: 1rem; overflow: hidden; }
.cand-table-header { display: grid; grid-template-columns: 3fr 1.2fr 1.2fr 1.2fr 1fr; padding: 1rem 1.5rem; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 700; border-bottom: 1px solid #e0ddd6; background: #fff; }

details.cand-row-details { border-bottom: 1px solid #e0ddd6; background: #fff; }
details.cand-row-details:last-child { border-bottom: none; }
summary.cand-row-summary { list-style: none; cursor: pointer; padding: 1.2rem 1.5rem; outline: none; }
summary.cand-row-summary::-webkit-details-marker { display: none; }
summary.cand-row-summary:hover { background: #fafaf5; }

.cand-row { display: grid; grid-template-columns: 3fr 1.2fr 1.2fr 1.2fr 1fr; align-items: center; gap: 1rem; }
.cand-name-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; }
.cand-name { font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 800; color: #1a1a2e; }
.ai-badge { background: #e8f5e0; color: #3d6b2e; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.7rem; font-weight: 600; border: 1px solid #bce2a8; display: inline-flex; align-items: center; gap: 0.2rem; }
.cand-meta { font-size: 0.8rem; color: #666; display: flex; align-items: center; gap: 0.8rem; }

.match-score { font-size: 1.3rem; font-weight: 800; color: #1a1a2e; }
.match-sub { font-size: 0.8rem; color: #999; font-weight: 500; }
.interest-text { font-size: 0.85rem; color: #888; font-style: italic; }
.combined-score { font-family: 'Playfair Display', serif; font-size: 1.8rem; font-weight: 900; color: #1a1a2e; }

.bar-container { width: 120px; margin-top: 0.4rem; }
.progress-bar { height: 6px; background: #f0f0ea; border-radius: 4px; overflow: hidden; width: 100%; }
.progress-fill { height: 100%; border-radius: 4px; }
.fill-dark { background: #1a1a2e; }
.fill-green { background: #a3e635; }
.fill-yellow { background: #fbbf24; }

.action-col { display: flex; align-items: center; justify-content: flex-end; gap: 0.8rem; }
.engage-btn { background: #1a1a2e; color: #fff; padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.4rem; border: none; }
.chevron { color: #888; font-size: 0.8rem; font-weight: bold; transition: transform 0.2s; }
details.cand-row-details[open] summary .chevron { transform: rotate(180deg); }

.detail-grid { display: grid; grid-template-columns: 1fr 1.2fr 1fr; gap: 2rem; padding: 1.8rem 1.5rem; background: #fafaf5; border-top: 1px solid #e0ddd6; }
.detail-section-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; color: #888; font-weight: 700; margin-bottom: 0.8rem; }
.detail-bio { color: #333; font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.8rem; }
.detail-company { color: #666; font-size: 0.8rem; margin-bottom: 1rem; }
.skills-container { display: flex; flex-wrap: wrap; gap: 0.4rem; }

.match-label { display: flex; justify-content: space-between; font-size: 0.85rem; color: #444; margin-bottom: 0.3rem; }
.match-value { color: #666; font-size: 0.8rem; }
.fit-bar-container { display: flex; gap: 1rem; margin-top: 1.5rem; }
.fit-item { flex: 1; }
.fit-bar { height: 6px; background: #f0f0ea; border-radius: 3px; margin-top: 0.4rem; overflow: hidden; }
.fit-fill { height: 100%; border-radius: 3px; background: #1a1a2e; }
.interest-note { color: #666; font-size: 0.9rem; font-style: italic; line-height: 1.5; }

.chat-bubble { padding: 0.7rem 1rem; border-radius: 10px; margin: 0.3rem 0; font-size: 0.85rem; }
.chat-r { background: #f5f5f0; margin-right: 2rem; border: 1px solid #e0ddd6; }
.chat-c { background: #e8f5e0; margin-left: 2rem; border: 1px solid #bce2a8; }

.skill-pill-s { padding: 0.3rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 500; display: inline-block; }
.skill-default { background: #fff; border: 1px solid #e0ddd6; color: #555; }
.skill-match { background: #e8f5e0; border: 1px solid #bce2a8; color: #3d6b2e; }
.skill-missing { background: #fff0f0; border: 1px solid #ffcdd2; color: #d32f2f; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

def score_color(s):
    if s >= 70: return "fill-green"
    if s >= 50: return "fill-dark"
    if s >= 30: return "fill-yellow"
    return "fill-red"

def render_nav():
    st.markdown("""<div class="nav-wrapper"><div class="nav-bar">
        <div class="nav-logo">
            <div class="nav-icon">⚡</div>
            <div><div class="nav-title">Talent Scout</div><div class="nav-sub">HR · Sourcing &amp; Analysis</div></div>
        </div>
        <div style="display:flex;align-items:center;gap:1rem;">
            <span style="font-size:0.78rem;color:#aaa;font-weight:500;">🔍 Recruiter Dashboard</span>
            <a href="/" target="_self" style="font-size:0.82rem;color:#1a1a2e;text-decoration:none;font-weight:600;padding:0.4rem 0.9rem;border:1px solid #e0ddd6;border-radius:8px;background:#fff;">← Home</a>
        </div>
    </div></div>""", unsafe_allow_html=True)

def render_landing():
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<div class="hero-badge">✨ Sourced · engaged · ranked — automatically</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Stop chasing candidates.<br><span class="hero-green">Score their interest.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-desc">Paste a job description. Our agent parses it, finds matching candidates, runs simulated conversations to gauge real interest, and hands you a ranked shortlist.</div>', unsafe_allow_html=True)
        st.markdown("""<div class="step-cards">
            <div class="step-card"><div class="step-num">1</div><div class="step-text">Parse JD into structured criteria</div></div>
            <div class="step-card"><div class="step-num">2</div><div class="step-text">Match & top-up with AI sourcing</div></div>
            <div class="step-card"><div class="step-num">3</div><div class="step-text">Engage to score real interest</div></div>
        </div>""", unsafe_allow_html=True)
    with col_r:
        st.markdown('<div class="jd-section">', unsafe_allow_html=True)
        st.markdown('<div class="jd-label">Job description</div>', unsafe_allow_html=True)
        tabs = st.tabs(list(SAMPLE_JDS.keys()))
        for i, (name, jd_text) in enumerate(SAMPLE_JDS.items()):
            with tabs[i]:
                if st.button(f"Use this JD", key=f"use_{i}", use_container_width=True):
                    st.session_state.jd_default = jd_text
                    st.rerun()
        if "jd_default" not in st.session_state:
            st.session_state.jd_default = list(SAMPLE_JDS.values())[0]
        jd_text = st.text_area("jd", value=st.session_state.jd_default, height=220, label_visibility="collapsed")
        st.markdown(f'<div class="char-count">{len(jd_text)} chars</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c2:
            search = st.button("🔍 Discover candidates", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    return jd_text, search

def render_parsed_jd(jd):
    must = jd.get("must_have_skills", [])
    nice = jd.get("nice_to_have_skills", [])
    must_pills = "".join(f'<span class="skill-pill">{s["name"]}</span>' for s in must)
    nice_pills = "".join(f'<span class="skill-pill-nice">✨ {s["name"]}</span>' for s in nice)
    locs = ", ".join(jd.get("locations", ["Remote"]))
    yrs = f'{jd.get("min_years_experience",0)}+ years'
    wm = jd.get("work_mode", "hybrid").title()
    sal = ""
    if jd.get("salary_range_lpa"):
        sal = f' · {jd["salary_range_lpa"]["min"]}-{jd["salary_range_lpa"]["max"]} LPA'
    st.markdown(f"""<div class="parsed-card">
        <div style="display:flex;justify-content:space-between;align-items:start;">
            <div class="parsed-header">JD Parsed</div>
            <span class="seniority-badge">{jd.get("seniority","mid").title()}</span>
        </div>
        <div class="parsed-title">{jd.get("role_title","Role")}</div>
        <div class="parsed-desc">{jd.get("department","")}</div>
        <div class="parsed-meta">
            <span>🏢 {yrs}</span><span>📍 {locs}</span><span>🌐 {wm} OK</span>{f'<span>💰{sal}</span>' if sal else ''}
        </div>
        <div class="section-label">Required</div>{must_pills}
        <div class="section-label">Nice to Have</div>{nice_pills}
    </div>""", unsafe_allow_html=True)

def render_shortlist_header(result):
    sl = result.get("shortlist", [])
    strong = sum(1 for s in sl if "Strong" in s.get("bucket", ""))
    st.markdown(f"""<div style="padding:0.6rem 0 1rem;">
        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:2px;color:#888;font-weight:700;margin-bottom:0.3rem;">Shortlist</div>
        <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:900;color:#1a1a2e;line-height:1;">{len(sl)} Candidates</div>
        <div style="font-size:0.8rem;color:#aaa;margin-top:0.3rem;">{strong} strong match · Combined = 70% match + 30% interest</div>
    </div>""", unsafe_allow_html=True)


def render_candidate_detail(entry):
    headline = entry.get("headline", "")
    yoe = entry.get("years_experience", 0)
    title = entry.get("current_title", "")
    skills = entry.get("skills", [])
    skills_html = "".join(f'<span class="skill-pill-s skill-default">{s["name"]}</span>' for s in skills[:6])
    profile_html = f"""<div><div class="detail-section-title">Profile</div><div class="detail-bio">{headline}</div><div class="detail-company">Currently at <strong>{title}</strong> · {yoe}y exp</div><div class="skills-container">{skills_html}</div></div>"""
    contribs = entry.get("feature_contributions", [])
    must_cov = next((c for c in contribs if "Must Have" in c.get("feature","")), {})
    exp_fit = next((c for c in contribs if "Experience" in c.get("feature","")), {})
    loc_fit = next((c for c in contribs if "Location" in c.get("feature","")), {})
    exp_val = int(exp_fit.get("value", 0) * 100)
    loc_val = int(loc_fit.get("value", 0) * 100)
    risks = entry.get("risks", [])
    missing_html = ""
    for r in risks:
        if "Missing" in r:
            missed = r.replace("Missing skills: ", "").split(", ")
            missing_html = "".join(f'<span class="skill-pill-s skill-missing">{s}</span>' for s in missed)
    match_html = f"""<div><div class="detail-section-title">Match Breakdown</div><div class="match-label"><span>Required skills</span><span class="match-value">{must_cov.get("note","")}</span></div><div class="skills-container" style="margin-bottom:1rem;">{missing_html}</div><div class="fit-bar-container"><div class="fit-item"><div class="match-label">Experience fit</div><div class="fit-bar"><div class="fit-fill" style="width:{exp_val}%"></div></div></div><div class="fit-item"><div class="match-label">Location fit</div><div class="fit-bar"><div class="fit-fill" style="width:{loc_val}%"></div></div></div></div></div>"""
    conv = entry.get("conversation_log", [])
    if conv:
        chat_html = "".join(f'<div class="chat-bubble {"chat-r" if m["role"]=="recruiter" else "chat-c"}"><b>{"🧑‍💼 Recruiter" if m["role"]=="recruiter" else "👤 Candidate"}:</b> {m["message"]}</div>' for m in conv[:4])
        int_html = f'<div><div class="detail-section-title">Interest Signal</div>{chat_html}</div>'
    else:
        int_html = '<div><div class="detail-section-title">Interest Signal</div><div class="interest-note">No outreach yet. Click Engage to simulate a conversation.</div></div>'
    return f'<div class="detail-grid">{profile_html}{match_html}{int_html}</div>'

def render_candidate_table(result):
    sl = result.get("shortlist", [])
    st.markdown('<div class="cand-table-container">', unsafe_allow_html=True)
    st.markdown("""<div class="cand-table-header">
        <div>Candidate</div><div>Match</div><div>Interest</div><div>Combined</div><div style="text-align:right">Action</div>
    </div>""", unsafe_allow_html=True)
    for entry in sl:
        ms = entry["match_score"]
        isc = entry["interest_score"]
        cs = entry["shortlist_rank_score"]
        int_text = f"{isc}/100" if isc != 50.0 else "not engaged"
        cc = score_color(cs)
        ai_badge = '<span class="ai-badge">✨ AI-sourced</span>'
        row_html = f"""<details class="cand-row-details"><summary class="cand-row-summary"><div class="cand-row"><div><div class="cand-name-row"><span class="cand-name">{entry['full_name']}</span>{ai_badge}</div><div class="cand-meta"><span>🏢 {entry.get('current_title','')}</span><span>📍 {entry.get('location','')}</span></div></div><div><span class="match-score">{ms}</span><span class="match-sub"> /100</span><div class="bar-container"><div class="progress-bar"><div class="progress-fill fill-dark" style="width:{ms}%"></div></div></div></div><div><span class="interest-text">{int_text}</span></div><div><span class="combined-score">{cs}</span><div class="bar-container"><div class="progress-bar"><div class="progress-fill {cc}" style="width:{cs}%"></div></div></div></div><div class="action-col"><span class="engage-btn">💬 Engage</span><span class="chevron">v</span></div></div></summary>{render_candidate_detail(entry)}</details>"""
        st.markdown(row_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    render_nav()
    if "search_result" not in st.session_state:
        jd_text, search = render_landing()
        if search and jd_text.strip():
            with st.spinner("🔄 Parsing JD → Retrieving → Reranking → Scoring..."):
                try:
                    r = requests.post(f"{API_URL}/search", json={"jd_text": jd_text, "use_db": False, "top_k": 10, "run_outreach": True}, timeout=180)
                    if r.status_code == 200:
                        st.session_state.search_result = r.json()
                        st.session_state.jd_text_used = jd_text
                        r2 = requests.post(f"{API_URL}/parse-jd", json={"jd_text": jd_text}, timeout=30)
                        if r2.status_code == 200 and r2.json().get("success"):
                            st.session_state.parsed_jd = r2.json()["jd"]
                        st.rerun()
                    else:
                        st.error(f"API error {r.status_code}: {r.text[:300]}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Run: `uvicorn app.api.main:app --reload --port 8000`")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        result = st.session_state.search_result
        if st.button("← New Search", type="secondary"):
            del st.session_state["search_result"]
            if "parsed_jd" in st.session_state:
                del st.session_state["parsed_jd"]
            st.rerun()
        col1, col2 = st.columns([1, 1.5], gap="large")
        with col1:
            if "parsed_jd" in st.session_state:
                render_parsed_jd(st.session_state.parsed_jd)
        with col2:
            render_shortlist_header(result)
        st.markdown("---")
        render_candidate_table(result)
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 Download JSON", json.dumps(result, indent=2), "shortlist.json", "application/json")
        with c2:
            if result.get("shortlist"):
                df = pd.DataFrame([{"Rank": e["rank"], "Name": e["full_name"], "Match": e["match_score"], "Interest": e["interest_score"], "Combined": e["shortlist_rank_score"], "Bucket": e.get("bucket","")} for e in result["shortlist"]])
                st.download_button("📥 Download CSV", df.to_csv(index=False), "shortlist.csv", "text/csv")

if __name__ == "__main__":
    main()

"""Candidate Profile — Resume Submission Page."""
import streamlit as st
import json
import os
import uuid
from datetime import datetime

st.set_page_config(page_title="Candidate Profile | Talent Scout", page_icon="📋", layout="wide", initial_sidebar_state="collapsed")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f3ee; }
[data-testid="stHeader"] { background: #f5f3ee; }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 860px; padding-top: 1rem; }
.stTextArea textarea { background: #fff !important; color: #1a1a2e !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
.stTextInput input { background: #fff !important; color: #1a1a2e !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
.stSelectbox > div { background: #fff !important; border-radius: 10px !important; }
.stMultiSelect > div { background: #fff !important; border-radius: 10px !important; }
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; }
.stNumberInput input { background: #fff !important; color: #1a1a2e !important; border-radius: 10px !important; }

.nav-bar { display: flex; align-items: center; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid #e0ddd6; margin-bottom: 2rem; }
.nav-logo { display: flex; align-items: center; gap: 0.6rem; }
.nav-icon { width: 36px; height: 36px; background: #1a1a2e; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #a3e635; font-size: 1.1rem; }
.nav-title { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
.nav-sub { font-size: 0.72rem; color: #888; }

.page-hero { text-align: center; padding: 2rem 0 1.5rem; }
.page-hero h1 { font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 900; color: #1a1a2e; margin-bottom: 0.5rem; }
.page-hero p { color: #666; font-size: 1rem; }

.form-section { background: #fff; border: 1px solid #e0ddd6; border-radius: 16px; padding: 1.8rem; margin-bottom: 1.2rem; }
.section-title { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 2px; color: #888; font-weight: 700; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
.section-icon { font-size: 1rem; }

.progress-bar-outer { height: 5px; background: #e0ddd6; border-radius: 3px; margin-bottom: 2rem; }
.progress-bar-inner { height: 100%; background: linear-gradient(90deg, #a3e635, #1a1a2e); border-radius: 3px; transition: width 0.5s ease; }

.submit-card { background: linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%); border-radius: 16px; padding: 2.5rem; text-align: center; color: #fff; margin-top: 1.5rem; }
.submit-card h3 { font-family: 'Playfair Display', serif; font-size: 1.6rem; margin-bottom: 0.5rem; }
.submit-card p { color: #aaa; font-size: 0.9rem; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ─── NAV ─────────────────────────────────────────────────────────────────────
st.markdown("""<div class="nav-bar">
    <div class="nav-logo">
        <div class="nav-icon">⚡</div>
        <div><div class="nav-title">Talent Scout</div><div class="nav-sub">AI Sourcing & Engagement Agent</div></div>
    </div>
    <div style="font-size:0.85rem;color:#888;">📋 Candidate Registration</div>
</div>""", unsafe_allow_html=True)

# ─── HERO ────────────────────────────────────────────────────────────────────
st.markdown("""<div class="page-hero">
    <h1>Build Your Profile</h1>
    <p>Fill in your details below. Our AI will match you to the best opportunities and schedule a quick interest chat.</p>
</div>""", unsafe_allow_html=True)

# ─── SKILL OPTIONS ───────────────────────────────────────────────────────────
ALL_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++", "C#", "Ruby", "Kotlin", "Swift",
    "React", "Next.js", "Vue.js", "Angular", "Svelte", "Node.js", "FastAPI", "Django", "Flask", "Spring Boot",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "DynamoDB",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "Ansible", "CI/CD", "GitHub Actions",
    "PyTorch", "TensorFlow", "Hugging Face", "LangChain", "OpenAI API", "Scikit-learn", "Pandas", "NumPy",
    "Git", "Linux", "REST APIs", "GraphQL", "gRPC", "Kafka", "RabbitMQ", "Celery",
    "Figma", "Tailwind CSS", "Sass/SCSS", "Webpack", "Vite",
]

# ─── FORM ────────────────────────────────────────────────────────────────────
with st.form("candidate_profile_form", clear_on_submit=False):

    # 1. Personal Details
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">👤</span> Personal Information</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        full_name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")
        email = st.text_input("Email Address *", placeholder="priya@email.com")
        phone = st.text_input("Phone Number", placeholder="+91 98765 43210")
    with c2:
        location = st.text_input("Current Location *", placeholder="e.g. Bengaluru, India")
        linkedin = st.text_input("LinkedIn URL", placeholder="linkedin.com/in/yourprofile")
        github = st.text_input("GitHub / Portfolio URL", placeholder="github.com/yourhandle")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Professional Summary
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">🎯</span> Professional Summary</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        current_title = st.text_input("Current Job Title *", placeholder="e.g. Senior Software Engineer")
    with c2:
        years_exp = st.number_input("Years of Experience *", min_value=0, max_value=50, value=3, step=1)
    with c3:
        employment_type = st.selectbox("Employment Type Seeking", ["Full-time", "Part-time", "Contract", "Freelance", "Open to all"])
    headline = st.text_area("Professional Headline / Summary *", placeholder="Write 2-3 sentences describing your expertise, what you've built, and what excites you...", height=100)
    notice_period = st.selectbox("Notice Period / Availability", ["Immediate", "< 2 weeks", "1 month", "2 months", "3 months", "> 3 months"])
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Skills & Tech Stack
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">🛠️</span> Skills & Technology Stack</div>', unsafe_allow_html=True)
    primary_skills = st.multiselect("Primary / Core Skills *", ALL_SKILLS, placeholder="Select your strongest skills...")
    secondary_skills = st.multiselect("Secondary / Familiar Skills", [s for s in ALL_SKILLS if s not in primary_skills], placeholder="Select other skills you know...")
    custom_skills = st.text_input("Additional Skills (comma-separated)", placeholder="e.g. Prompt Engineering, dbt, Airflow, CUDA")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Work Experience
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">💼</span> Work Experience</div>', unsafe_allow_html=True)
    st.caption("Describe your most relevant positions (latest first).")
    exp1_company = st.text_input("Company / Organisation (Current or Last)", placeholder="e.g. Infosys, Google, Startup Name")
    c1, c2 = st.columns(2)
    with c1:
        exp1_role = st.text_input("Role / Title", placeholder="e.g. Backend Engineer", key="exp1_role")
        exp1_duration = st.text_input("Duration", placeholder="e.g. Jan 2022 – Present")
    with c2:
        exp1_location = st.text_input("Location / Remote", placeholder="e.g. Bengaluru / Remote", key="exp1_loc")
    exp1_desc = st.text_area("Key Responsibilities & Achievements", placeholder="- Led migration of monolith to microservices, reducing latency by 40%\n- Mentored team of 3 junior engineers\n- Built real-time pipeline handling 10k events/sec", height=120)

    st.markdown("<hr style='border:none;border-top:1px solid #f0f0ea;margin:1rem 0'>", unsafe_allow_html=True)

    exp2_company = st.text_input("Previous Company (Optional)", placeholder="e.g. Wipro, Microsoft")
    c1, c2 = st.columns(2)
    with c1:
        exp2_role = st.text_input("Role / Title", placeholder="e.g. Junior Developer", key="exp2_role")
    with c2:
        exp2_duration = st.text_input("Duration", placeholder="e.g. Jul 2020 – Dec 2021", key="exp2_dur")
    exp2_desc = st.text_area("Key Responsibilities & Achievements (Optional)", height=90, key="exp2_desc")
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. Projects
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">🚀</span> Notable Projects</div>', unsafe_allow_html=True)
    st.caption("Highlight up to 3 projects you are most proud of.")
    for i in range(1, 4):
        with st.expander(f"Project {i}", expanded=(i == 1)):
            p_name = st.text_input("Project Name", placeholder="e.g. AI Resume Screener", key=f"p{i}_name")
            p_desc = st.text_area("What did you build? What was the impact?", placeholder="Built a FastAPI + LangChain pipeline that reduced screening time by 70%...", height=90, key=f"p{i}_desc")
            p_tech = st.text_input("Technologies Used", placeholder="e.g. Python, FastAPI, PostgreSQL, OpenAI", key=f"p{i}_tech")
            p_link = st.text_input("GitHub / Live Link (optional)", placeholder="https://github.com/...", key=f"p{i}_link")
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. Education
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">🎓</span> Education</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        edu_degree = st.text_input("Degree / Qualification *", placeholder="e.g. B.Tech Computer Science")
        edu_institution = st.text_input("Institution *", placeholder="e.g. IIT Bombay / BITS Pilani")
    with c2:
        edu_year = st.text_input("Year of Graduation", placeholder="e.g. 2021")
        edu_score = st.text_input("CGPA / Percentage (optional)", placeholder="e.g. 8.7 / 10")
    certifications = st.text_area("Certifications / Courses (optional)", placeholder="AWS Certified Solutions Architect, Google Cloud Professional ML Engineer, ...", height=70)
    st.markdown('</div>', unsafe_allow_html=True)

    # 7. Preferences
    st.markdown('<div class="form-section"><div class="section-title"><span class="section-icon">⚙️</span> Job Preferences</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        pref_role = st.text_input("Preferred Role / Domain", placeholder="e.g. ML Engineer, Full-stack")
        pref_salary = st.text_input("Expected Salary (LPA)", placeholder="e.g. 20-30 LPA")
    with c2:
        pref_location = st.text_input("Preferred Location(s)", placeholder="e.g. Bengaluru, Remote")
        work_mode = st.selectbox("Work Mode Preference", ["Remote", "Hybrid", "On-site", "Flexible"])
    with c3:
        open_to_relocation = st.selectbox("Open to Relocation?", ["Yes", "No", "Maybe"])
    additional_notes = st.text_area("Anything else you'd like recruiters to know?", height=80, placeholder="Sabbatical reason, side projects, open-source contributions, etc.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ─── SUBMIT ───────────────────────────────────────────────────────────────
    st.markdown('<div class="submit-card"><h3>Ready to find your next role? 🚀</h3><p>Your profile will be saved and you\'ll be taken to a quick interest chat with our AI recruiter.</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    submitted = st.form_submit_button("✨ Submit Profile & Start Chat →", type="primary", use_container_width=True)

# ─── PROCESS SUBMISSION ──────────────────────────────────────────────────────
if submitted:
    if not full_name.strip() or not email.strip() or not location.strip() or not current_title.strip() or not headline.strip() or not primary_skills:
        st.error("⚠️ Please fill in all required fields (marked with *): Full Name, Email, Location, Current Title, Headline, and at least one Primary Skill.")
    else:
        # Build candidate profile dict
        all_custom = [s.strip() for s in custom_skills.split(",") if s.strip()]
        all_skills_combined = (
            [{"name": s, "level": "expert"} for s in primary_skills] +
            [{"name": s, "level": "proficient"} for s in secondary_skills] +
            [{"name": s, "level": "familiar"} for s in all_custom]
        )

        projects = []
        for i in range(1, 4):
            name_val = st.session_state.get(f"p{i}_name", "")
            desc_val = st.session_state.get(f"p{i}_desc", "")
            if name_val and desc_val:
                projects.append({
                    "name": name_val,
                    "description": desc_val,
                    "tech": st.session_state.get(f"p{i}_tech", ""),
                    "link": st.session_state.get(f"p{i}_link", ""),
                })

        experience = []
        if exp1_company.strip():
            experience.append({
                "company": exp1_company,
                "role": exp1_role,
                "duration": exp1_duration,
                "location": exp1_location,
                "description": exp1_desc,
            })
        if exp2_company.strip():
            experience.append({
                "company": exp2_company,
                "role": exp2_role,
                "duration": exp2_duration,
                "description": exp2_desc,
            })

        candidate_profile = {
            "candidate_id": str(uuid.uuid4()),
            "submitted_at": datetime.utcnow().isoformat(),
            # Personal
            "full_name": full_name.strip(),
            "email": email.strip(),
            "phone": phone.strip(),
            "location": location.strip(),
            "linkedin": linkedin.strip(),
            "github": github.strip(),
            # Professional
            "current_title": current_title.strip(),
            "years_experience": int(years_exp),
            "headline": headline.strip(),
            "notice_period": notice_period,
            "employment_type": employment_type,
            # Skills
            "skills": all_skills_combined,
            # Experience
            "experience": experience,
            # Projects
            "projects": projects,
            # Education
            "education": {
                "degree": edu_degree.strip(),
                "institution": edu_institution.strip(),
                "year": edu_year.strip(),
                "score": edu_score.strip(),
                "certifications": certifications.strip(),
            },
            # Preferences
            "preferences": {
                "preferred_role": pref_role.strip(),
                "expected_salary": pref_salary.strip(),
                "preferred_location": pref_location.strip(),
                "work_mode": work_mode,
                "open_to_relocation": open_to_relocation,
                "additional_notes": additional_notes.strip(),
            },
            # Flags
            "profile_complete": True,
            "chat_completed": False,
            "interest_score": None,
        }

        # Save to JSON store (append to candidates file or separate file)
        candidates_file = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "data", "submitted_candidates.json"
        )
        candidates_file = os.path.normpath(candidates_file)
        existing = []
        if os.path.exists(candidates_file):
            try:
                with open(candidates_file, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception:
                existing = []
        existing.append(candidate_profile)
        with open(candidates_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        # Store in session state and redirect
        st.session_state["candidate_profile"] = candidate_profile
        st.session_state["chat_messages"] = []
        st.session_state["chat_stage"] = 0
        st.success(f"✅ Profile saved! Welcome, {full_name}. Taking you to the interest chat...")
        st.balloons()
        st.switch_page("pages/2_Interest_Chat.py")

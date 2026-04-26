"""Interest Chat — AI Recruiter Conversation Page."""
import streamlit as st
import os
import json
import time
import random
from datetime import datetime

st.set_page_config(page_title="Interest Chat | Talent Scout", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f3ee; }
[data-testid="stHeader"] { background: #f5f3ee; }
[data-testid="stSidebar"] { display: none; }
.block-container { max-width: 760px; padding-top: 1rem; }

.nav-bar { display: flex; align-items: center; justify-content: space-between; padding: 0.8rem 0; border-bottom: 1px solid #e0ddd6; margin-bottom: 1.5rem; }
.nav-logo { display: flex; align-items: center; gap: 0.6rem; }
.nav-icon { width: 36px; height: 36px; background: #1a1a2e; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #a3e635; font-size: 1.1rem; }
.nav-title { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
.nav-sub { font-size: 0.72rem; color: #888; }

.chat-header { background: linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%); border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 1rem; }
.ai-avatar { width: 52px; height: 52px; background: #a3e635; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; }
.chat-header-text h2 { font-family: 'Playfair Display', serif; color: #fff; margin: 0; font-size: 1.4rem; }
.chat-header-text p { color: #aaa; margin: 0; font-size: 0.85rem; }

.chat-window { background: #fff; border: 1px solid #e0ddd6; border-radius: 16px; padding: 1.5rem; min-height: 320px; margin-bottom: 1rem; }

.msg-row { display: flex; margin-bottom: 1rem; gap: 0.6rem; }
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.msg-avatar.ai { background: #1a1a2e; }
.msg-avatar.user { background: #e8f5e0; border: 1px solid #bce2a8; }

.msg-bubble { max-width: 78%; padding: 0.8rem 1.1rem; border-radius: 16px; font-size: 0.9rem; line-height: 1.6; }
.msg-bubble.ai { background: #f5f5f0; border: 1px solid #e0ddd6; color: #1a1a2e; border-top-left-radius: 4px; }
.msg-bubble.user { background: #1a1a2e; color: #fff; border-top-right-radius: 4px; }
.msg-time { font-size: 0.7rem; color: #bbb; margin-top: 0.3rem; text-align: right; }

.typing-indicator { display: flex; align-items: center; gap: 0.3rem; padding: 0.6rem 1rem; background: #f0f0ea; border-radius: 12px; width: fit-content; }
.typing-dot { width: 7px; height: 7px; border-radius: 50%; background: #999; animation: bounce 1.2s infinite; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1.1); opacity: 1; } }

.score-card { background: linear-gradient(135deg, #1a1a2e 0%, #2d2d4e 100%); border-radius: 16px; padding: 2.5rem; text-align: center; color: #fff; margin-top: 1.5rem; }
.score-big { font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 900; color: #a3e635; }
.score-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; color: #aaa; margin-bottom: 0.5rem; }
.interest-tag { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem; }
.tag-high { background: #e8f5e0; color: #3d6b2e; border: 1px solid #bce2a8; }
.tag-med { background: #fff8e1; color: #7c5c00; border: 1px solid #fdd835; }
.tag-low { background: #fff0f0; color: #d32f2f; border: 1px solid #ffcdd2; }

.stButton > button { border-radius: 10px !important; font-weight: 600 !important; }
.stTextInput input { background: #fff !important; color: #1a1a2e !important; border: 1px solid #ddd !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ─── NAV ─────────────────────────────────────────────────────────────────────
st.markdown("""<div class="nav-bar">
    <div class="nav-logo">
        <div class="nav-icon">⚡</div>
        <div><div class="nav-title">Talent Scout</div><div class="nav-sub">AI Sourcing & Engagement Agent</div></div>
    </div>
    <div style="font-size:0.85rem;color:#888;">💬 Interest Assessment Chat</div>
</div>""", unsafe_allow_html=True)

# ─── GUARD: must have a profile ───────────────────────────────────────────────
profile = st.session_state.get("candidate_profile", None)
if not profile:
    st.warning("⚠️ No candidate profile found. Please fill in your profile first.")
    if st.button("← Go to Profile Form"):
        st.switch_page("pages/1_Candidate_Profile.py")
    st.stop()

name = profile.get("full_name", "Candidate")
title = profile.get("current_title", "professional")
skills = [s["name"] for s in profile.get("skills", [])[:3]]
skills_str = ", ".join(skills) if skills else "your technical skills"
notice = profile.get("notice_period", "flexible")
preferred_role = profile.get("preferences", {}).get("preferred_role", title)

# ─── CONVERSATION FLOW ────────────────────────────────────────────────────────
CHAT_QUESTIONS = [
    f"Hi {name}! 👋 I'm Alex, the AI Talent Scout. I've reviewed your profile and I'm really impressed with your background as a **{title}**. I'd love to ask you a few quick questions to understand what you're really looking for right now. This will only take 3–4 minutes. **First — what's driving your job search right now?** Are you actively looking, passively exploring, or just keeping options open?",
    f"That's helpful context, thank you! Your experience with **{skills_str}** looks strong. On a scale of 1–10, how urgently are you looking to make a move? And what's your ideal timeline for starting a new role? (You mentioned '{notice}' as your notice period — does that still hold?)",
    f"Great. Now, what kind of role are you most excited about? You mentioned **{preferred_role or title}** — is that your primary focus, or are you open to adjacent areas? What would make a role a **definite yes** for you?",
    "Almost done! Two last things: **What are your salary expectations** and your preferred work arrangement — remote, hybrid, or on-site? And is there anything that would be a **hard dealbreaker** for you in a new role?",
    f"Thank you so much, {name}! 🙏 That gives me a really clear picture of what you're looking for. I'm going to use everything we discussed to match you with the best-fit opportunities. We'll reach out within 2–3 business days if there's a strong match. Any final questions for me before I wrap up?",
]

# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "chat_stage" not in st.session_state:
    st.session_state.chat_stage = 0
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "interest_score" not in st.session_state:
    st.session_state.interest_score = None

# Auto-send first AI message
if len(st.session_state.chat_messages) == 0:
    st.session_state.chat_messages.append({
        "role": "ai",
        "text": CHAT_QUESTIONS[0],
        "time": datetime.now().strftime("%H:%M"),
    })
    st.session_state.chat_stage = 1

# ─── CHAT HEADER ─────────────────────────────────────────────────────────────
progress_pct = int((st.session_state.chat_stage / len(CHAT_QUESTIONS)) * 100)
st.markdown(f"""<div class="chat-header">
    <div class="ai-avatar">🤖</div>
    <div class="chat-header-text">
        <h2>Alex — AI Talent Scout</h2>
        <p>Quick interest assessment · {len(CHAT_QUESTIONS)} questions · ~4 mins</p>
    </div>
</div>""", unsafe_allow_html=True)

# Progress bar
st.markdown(f"""<div style="margin-bottom:1.2rem;">
    <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#888;margin-bottom:0.3rem;">
        <span>Progress</span><span>{progress_pct}% complete</span>
    </div>
    <div style="height:5px;background:#e0ddd6;border-radius:3px;">
        <div style="height:100%;width:{progress_pct}%;background:linear-gradient(90deg,#a3e635,#1a1a2e);border-radius:3px;transition:width 0.5s;"></div>
    </div>
</div>""", unsafe_allow_html=True)

# ─── CHAT WINDOW ─────────────────────────────────────────────────────────────
chat_html_parts = ['<div class="chat-window">']
for msg in st.session_state.chat_messages:
    role_cls = msg["role"]
    avatar = "🤖" if role_cls == "ai" else "😊"
    bubble_cls = "ai" if role_cls == "ai" else "user"
    row_cls = "" if role_cls == "ai" else "user"
    chat_html_parts.append(f"""
    <div class="msg-row {row_cls}">
        <div class="msg-avatar {bubble_cls}">{avatar}</div>
        <div>
            <div class="msg-bubble {bubble_cls}">{msg["text"]}</div>
            <div class="msg-time">{msg["time"]}</div>
        </div>
    </div>""")

chat_html_parts.append('</div>')
st.markdown("".join(chat_html_parts), unsafe_allow_html=True)

# ─── INPUT / INTERACTION ─────────────────────────────────────────────────────
if not st.session_state.chat_complete:
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_reply = st.text_input("Your reply...", placeholder="Type your answer here and press Send →", label_visibility="collapsed")
        with col2:
            send = st.form_submit_button("Send ➤", use_container_width=True, type="primary")

    if send and user_reply.strip():
        # Append user message
        st.session_state.chat_messages.append({
            "role": "user",
            "text": user_reply.strip(),
            "time": datetime.now().strftime("%H:%M"),
        })

        stage = st.session_state.chat_stage

        if stage < len(CHAT_QUESTIONS):
            # Send next AI question
            st.session_state.chat_messages.append({
                "role": "ai",
                "text": CHAT_QUESTIONS[stage],
                "time": datetime.now().strftime("%H:%M"),
            })
            st.session_state.chat_stage = stage + 1

        if st.session_state.chat_stage >= len(CHAT_QUESTIONS):
            # Calculate interest score based on answer length / keyword signals
            all_user_text = " ".join(
                m["text"].lower() for m in st.session_state.chat_messages if m["role"] == "user"
            )
            high_kws = ["actively", "immediately", "asap", "urgent", "definitely", "very interested", "looking forward", "excited", "ready", "open to", "yes", "great opportunity"]
            low_kws  = ["just exploring", "not sure", "maybe", "passive", "not urgent", "later", "probably not", "no", "hard pass"]
            high_hits = sum(1 for kw in high_kws if kw in all_user_text)
            low_hits  = sum(1 for kw in low_kws  if kw in all_user_text)
            base = 55 + (high_hits * 5) - (low_hits * 8)
            # Adjust for length of answers (longer = more engaged)
            avg_len = sum(len(m["text"]) for m in st.session_state.chat_messages if m["role"] == "user") / max(1, sum(1 for m in st.session_state.chat_messages if m["role"] == "user"))
            if avg_len > 80: base += 10
            elif avg_len > 40: base += 5
            score = max(20, min(98, base))
            st.session_state.interest_score = round(score, 1)
            st.session_state.chat_complete = True

            # Save score back to profile and file
            profile["interest_score"] = st.session_state.interest_score
            profile["chat_completed"] = True
            profile["conversation_log"] = [
                {"role": m["role"], "message": m["text"]}
                for m in st.session_state.chat_messages
            ]
            st.session_state["candidate_profile"] = profile

            # Update file
            candidates_file = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "data", "submitted_candidates.json"
            )
            candidates_file = os.path.normpath(candidates_file)
            if os.path.exists(candidates_file):
                try:
                    with open(candidates_file, "r", encoding="utf-8") as f:
                        all_cands = json.load(f)
                    for i, c in enumerate(all_cands):
                        if c.get("candidate_id") == profile.get("candidate_id"):
                            all_cands[i] = profile
                            break
                    with open(candidates_file, "w", encoding="utf-8") as f:
                        json.dump(all_cands, f, indent=2)
                except Exception:
                    pass

        st.rerun()
else:
    # Chat complete — show friendly completion card (no score shown to candidate)
    st.markdown(f"""<div class="score-card">
        <div style="font-size:3rem;margin-bottom:0.8rem;">🎉</div>
        <h2 style="font-family:'Playfair Display',serif;color:#fff;margin:0 0 0.5rem;">You're all set, {name}!</h2>
        <p style="color:#aaa;font-size:0.95rem;margin:0 0 1.2rem;line-height:1.6;">
            Thanks for taking the time to chat with us.<br>
            Our team will review your profile and reach out within <strong style="color:#a3e635;">2–3 business days</strong> if there's a strong match.
        </p>
        <p style="color:#888;font-size:0.82rem;">
            📬 We'll contact you at <strong style="color:#ccc;">{profile.get("email", "your email")}</strong>
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Edit My Profile", use_container_width=True):
            st.switch_page("pages/1_Candidate_Profile.py")
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
            st.switch_page("app.py")

    # Show profile summary — WITHOUT any scores
    with st.expander("📋 View Your Submitted Profile"):
        prof = st.session_state.get("candidate_profile", {})
        st.json({
            "name": prof.get("full_name"),
            "email": prof.get("email"),
            "title": prof.get("current_title"),
            "experience_years": prof.get("years_experience"),
            "top_skills": [s["name"] for s in prof.get("skills", [])[:6]],
            "notice_period": prof.get("notice_period"),
            "preferences": prof.get("preferences"),
        })


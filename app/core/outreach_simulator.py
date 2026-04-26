"""
Outreach Simulator: simulates multi-turn recruiter-candidate conversations.
Uses LLM for conversation generation and structured signal extraction.
Falls back to deterministic simulation based on candidate interest_profile.
"""
import json
import sys
import os
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.schemas import JobDescription, OutreachSignals
from app.services.llm_client import generate_text, extract_structured, _USE_MOCK


def simulate_outreach(
    candidate: dict,
    jd: JobDescription,
) -> Tuple[OutreachSignals, List[Dict[str, str]]]:
    """
    Simulate recruiter outreach with a candidate.
    Returns (signals, conversation_log).
    """
    if _USE_MOCK:
        return _deterministic_simulate(candidate, jd)

    return _llm_simulate(candidate, jd)


def _llm_simulate(candidate: dict, jd: JobDescription) -> Tuple[OutreachSignals, List[Dict[str, str]]]:
    """Use LLM to simulate conversation and extract signals."""
    cand_name = candidate.get("full_name", "Candidate")
    cand_title = candidate.get("current_title", "Engineer")
    skills = ", ".join([s["name"] for s in candidate.get("skills", [])[:6]])
    expected_lpa = candidate.get("compensation", {}).get("expected_lpa", 0)
    notice = candidate.get("availability", {}).get("notice_period_days", 30)
    career_goals = ", ".join(candidate.get("interest_profile", {}).get("career_goals", []))
    reply_style = candidate.get("interest_profile", {}).get("reply_style", "concise_positive")
    salary_sensitivity = candidate.get("interest_profile", {}).get("salary_sensitivity", 0.5)

    prompt = f"""Simulate a 4-turn recruiter-candidate conversation.

RECRUITER CONTEXT:
- Role: {jd.role_title} at a {jd.industries[0] if jd.industries else 'tech'} company
- Location: {', '.join(jd.locations)} ({jd.work_mode})
- Skills needed: {', '.join(s.name for s in jd.must_have_skills)}
- Salary: {jd.salary_range_lpa.min if jd.salary_range_lpa else '?'}-{jd.salary_range_lpa.max if jd.salary_range_lpa else '?'} LPA
- Max notice: {jd.notice_period_days_max} days

CANDIDATE PROFILE:
- Name: {cand_name}
- Title: {cand_title}
- Skills: {skills}
- Expected salary: {expected_lpa} LPA
- Notice period: {notice} days
- Career goals: {career_goals}
- Reply style: {reply_style}
- Salary sensitivity: {salary_sensitivity}

Generate a realistic 4-turn conversation as JSON array:
[{{"role": "recruiter", "message": "..."}}, {{"role": "candidate", "message": "..."}}, ...]

The recruiter should ask about: interest in role, compensation alignment, notice period, work mode preference.
The candidate should respond realistically based on their profile."""

    try:
        response = generate_text(prompt)
        conversation = json.loads(response) if isinstance(response, str) else response
        if isinstance(conversation, dict) and "conversation" in conversation:
            conversation = conversation["conversation"]
    except Exception:
        _, conversation = _deterministic_simulate(candidate, jd)

    # Extract signals from conversation
    signals = _extract_signals(candidate, jd, conversation)
    return signals, conversation


def _extract_signals(candidate: dict, jd: JobDescription, conversation: list) -> OutreachSignals:
    """Extract structured outreach signals from conversation + candidate profile."""
    interest_profile = candidate.get("interest_profile", {})
    salary_sensitivity = interest_profile.get("salary_sensitivity", 0.5)
    reply_style = interest_profile.get("reply_style", "concise_positive")
    expected_lpa = candidate.get("compensation", {}).get("expected_lpa", 0)
    notice = candidate.get("availability", {}).get("notice_period_days", 30)

    # I_e: Explicit interest based on reply style
    style_map = {"enthusiastic": 0.9, "concise_positive": 0.75, "detailed_analytical": 0.7, "cautious": 0.5, "passive": 0.3}
    I_e = style_map.get(reply_style, 0.5)

    # R_a: Role alignment from career goals vs JD
    career_goals = set(g.lower() for g in interest_profile.get("career_goals", []))
    jd_keywords = set(k.lower() for k in jd.keywords) | {jd.role_title.lower().split()[0]}
    R_a = min(1.0, len(career_goals & jd_keywords) * 0.3 + 0.4)

    # W_a: Work-mode/location alignment
    cand_mode = candidate.get("work_preferences", {}).get("work_mode", "hybrid")
    W_a = 1.0 if cand_mode == jd.work_mode else 0.6
    cand_loc = candidate.get("location", "").lower()
    jd_locs = {l.lower() for l in jd.locations}
    if cand_loc in jd_locs or "remote india" in jd_locs:
        W_a = min(1.0, W_a + 0.2)

    # S_a: Salary alignment
    S_a = 1.0
    salary_mismatch_pct = 0.0
    if jd.salary_range_lpa and expected_lpa > 0:
        if expected_lpa <= jd.salary_range_lpa.max:
            S_a = 1.0
        else:
            salary_mismatch_pct = (expected_lpa - jd.salary_range_lpa.max) / jd.salary_range_lpa.max * 100
            S_a = max(0.1, 1.0 - salary_mismatch_pct / 50 * salary_sensitivity)

    # N_p: Notice period alignment
    N_p = 1.0
    notice_overshoot = 0
    if notice <= jd.notice_period_days_max:
        N_p = 1.0
    else:
        notice_overshoot = notice - jd.notice_period_days_max
        N_p = max(0.2, 1.0 - notice_overshoot / 90)

    # G_q: Engagement quality
    G_q = 0.7 if reply_style in ("enthusiastic", "concise_positive", "detailed_analytical") else 0.4

    # F_t: Follow-through
    F_t = 0.8 if candidate.get("availability", {}).get("actively_looking") else 0.4

    declined = reply_style == "passive" and I_e < 0.35
    reconnect = not candidate.get("availability", {}).get("actively_looking", True)

    return OutreachSignals(
        I_e=round(I_e, 3), R_a=round(R_a, 3), W_a=round(W_a, 3),
        S_a=round(S_a, 3), N_p=round(N_p, 3), G_q=round(G_q, 3), F_t=round(F_t, 3),
        declined=declined, reconnect_later=reconnect,
        salary_mismatch_pct=round(salary_mismatch_pct, 1),
        notice_overshoot_days=notice_overshoot,
    )


def _deterministic_simulate(candidate: dict, jd: JobDescription) -> Tuple[OutreachSignals, List[Dict[str, str]]]:
    """Deterministic fallback simulation without LLM."""
    cand_name = candidate.get("full_name", "Candidate")
    expected = candidate.get("compensation", {}).get("expected_lpa", 0)
    notice = candidate.get("availability", {}).get("notice_period_days", 30)
    reply_style = candidate.get("interest_profile", {}).get("reply_style", "concise_positive")
    sal_max = jd.salary_range_lpa.max if jd.salary_range_lpa else 30

    # Build deterministic conversation
    responses = {
        "enthusiastic": [
            f"That sounds amazing! I've been looking for exactly this kind of {jd.role_title} role.",
            f"The compensation range of {jd.salary_range_lpa.min if jd.salary_range_lpa else '?'}-{sal_max} LPA works well for me." if expected <= sal_max else f"I was hoping for closer to {expected} LPA, but I'm open to discussing.",
        ],
        "concise_positive": [
            f"Thanks for reaching out. I'm interested in learning more about the role.",
            f"The comp range aligns with my expectations." if expected <= sal_max else f"My expectation is {expected} LPA. Is there flexibility?",
        ],
        "cautious": [
            f"I appreciate you reaching out. Can you share more details about the team and tech stack?",
            f"I'd need to understand the full benefits package before making any commitment.",
        ],
        "detailed_analytical": [
            f"Interesting. I'd like to understand the scale of systems, team size, and growth trajectory.",
            f"Compensation-wise, I'm at {candidate.get('compensation', {}).get('current_lpa', '?')} LPA currently. The range mentioned seems reasonable." if expected <= sal_max else f"My current CTC is {candidate.get('compensation', {}).get('current_lpa', '?')} LPA and I'm expecting {expected} LPA.",
        ],
        "passive": [
            f"I'm not actively looking right now, but feel free to send over the JD.",
            f"I'll review it when I get a chance.",
        ],
    }

    cand_msgs = responses.get(reply_style, responses["concise_positive"])
    conversation = [
        {"role": "recruiter", "message": f"Hi {cand_name}! I came across your profile and think you'd be a great fit for our {jd.role_title} role in {', '.join(jd.locations)} ({jd.work_mode}). Would you be open to discussing?"},
        {"role": "candidate", "message": cand_msgs[0]},
        {"role": "recruiter", "message": f"Great! The role involves {', '.join(s.name for s in jd.must_have_skills[:3])}. Compensation is {jd.salary_range_lpa.min if jd.salary_range_lpa else '?'}-{sal_max} LPA. Notice period max is {jd.notice_period_days_max} days. Does that align?"},
        {"role": "candidate", "message": cand_msgs[1] if len(cand_msgs) > 1 else "That sounds reasonable."},
        {"role": "recruiter", "message": f"What's your current notice period and availability?"},
        {"role": "candidate", "message": f"My notice period is {notice} days. {'I can start discussions right away.' if candidate.get('availability', {}).get('actively_looking') else 'I might need some time to think it over.'}"},
    ]

    signals = _extract_signals(candidate, jd, conversation)
    return signals, conversation

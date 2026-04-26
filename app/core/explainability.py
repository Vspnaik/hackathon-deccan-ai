"""
Explainability engine: generates recruiter-facing rationales from scored features and conversation evidence.
Produces faithful explanations grounded in visible evidence, not LLM opinions.
"""
from typing import List, Tuple, Dict, Any
from app.core.schemas import JobDescription, FeatureContribution


def generate_rationale(
    candidate: dict,
    jd: JobDescription,
    match_contributions: List[FeatureContribution],
    interest_rationale: List[str],
    match_score: float,
    interest_score: float,
) -> Tuple[List[str], List[str], List[str]]:
    """
    Generate match rationale, interest rationale, and risks from evidence.
    
    Returns:
        (match_rationale_list, interest_rationale_list, risks_list)
    """
    match_rationale = []
    risks = []

    # Match rationale from feature contributions
    cand_skills = {s["name"].lower() for s in candidate.get("skills", [])}
    jd_must = [s.name for s in jd.must_have_skills]
    jd_must_lower = [s.lower() for s in jd_must]

    matched = [s for s in jd_must if s.lower() in cand_skills]
    missing = [s for s in jd_must if s.lower() not in cand_skills]

    match_rationale.append(f"Matched {len(matched)}/{len(jd_must)} must-have skills: {', '.join(matched) if matched else 'none'}")

    # Experience
    yoe = candidate.get("years_experience", 0)
    match_rationale.append(f"{yoe} years experience {'fits' if jd.min_years_experience <= yoe <= jd.max_years_experience else 'outside'} target band {jd.min_years_experience}-{jd.max_years_experience}")

    # Industry
    cand_ind = set(candidate.get("industries", []))
    jd_ind = set(jd.industries)
    overlap = cand_ind & jd_ind
    if overlap:
        match_rationale.append(f"Industry alignment: {', '.join(overlap)}")

    # Projects
    projects = candidate.get("projects", [])
    if projects:
        top_proj = projects[0]
        match_rationale.append(f"Relevant project: {top_proj.get('name', '')} — {top_proj.get('impact', '')}")

    # Location / work mode
    cand_loc = candidate.get("location", "")
    cand_mode = candidate.get("work_preferences", {}).get("work_mode", "hybrid")
    match_rationale.append(f"Location: {cand_loc} ({cand_mode})")

    # Notice and compensation
    notice = candidate.get("availability", {}).get("notice_period_days", 30)
    expected = candidate.get("compensation", {}).get("expected_lpa", 0)
    match_rationale.append(f"Notice: {notice}d (max {jd.notice_period_days_max}d), Expected: {expected} LPA")

    # Risks
    if missing:
        risks.append(f"Missing skills: {', '.join(missing)}")
    if yoe < jd.min_years_experience:
        risks.append(f"Experience {yoe}y below minimum {jd.min_years_experience}y")
    if yoe > jd.max_years_experience:
        risks.append(f"Experience {yoe}y above maximum {jd.max_years_experience}y — may be over-qualified")
    if notice > jd.notice_period_days_max:
        risks.append(f"Notice period {notice}d exceeds max {jd.notice_period_days_max}d")
    if jd.salary_range_lpa and expected > jd.salary_range_lpa.max:
        risks.append(f"Expected salary {expected} LPA exceeds budget {jd.salary_range_lpa.max} LPA")
    if not candidate.get("availability", {}).get("actively_looking"):
        risks.append("Candidate is not actively looking")

    return match_rationale, interest_rationale, risks


def get_status_label(match_score: float, interest_score: float) -> str:
    """Get human-readable status label."""
    if interest_score >= 70:
        return "🔥 Hot"
    elif interest_score >= 50:
        return "🌤️ Warm"
    elif interest_score >= 30:
        return "❄️ Uncertain"
    else:
        return "🚫 Not Interested"

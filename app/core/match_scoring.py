"""
Match scoring engine implementing the DPR formula.
Computes structured feature scores, applies hard constraints, and calibrates to 0-100.
"""
from typing import Dict, Any, List, Tuple
from app.core.schemas import JobDescription, FeatureContribution
from app.core.calibration import sigmoid_calibrate


def calculate_match_score(
    candidate: dict,
    jd: JobDescription,
    rerank_score: float = 0.0,
    dense_sim: float = 0.0,
    sparse_sim: float = 0.0,
) -> Tuple[float, List[FeatureContribution]]:
    """
    Compute the DPR Match Score formula.
    
    Returns:
        (match_score_0_100, list_of_feature_contributions)
    """
    features = compute_features(candidate, jd)
    contributions = []

    # Structured fit: S_f = 0.30*M_h + 0.08*N_h + 0.10*T + 0.12*E + 0.10*D + 0.12*P + 0.08*L + 0.10*C
    weights = {
        "must_have_coverage": 0.30,
        "nice_to_have_coverage": 0.08,
        "title_similarity": 0.10,
        "experience_fit": 0.12,
        "domain_fit": 0.10,
        "project_relevance": 0.12,
        "location_fit": 0.08,
        "compensation_fit": 0.10,
    }

    S_f = 0.0
    for feat_name, weight in weights.items():
        val = features.get(feat_name, 0.0)
        contrib = val * weight
        S_f += contrib
        contributions.append(FeatureContribution(
            feature=feat_name.replace("_", " ").title(),
            value=round(val, 3),
            weight=weight,
            contribution=round(contrib, 4),
            note=features.get(f"{feat_name}_note", ""),
        ))

    # Raw match: M_raw = 0.38*S_f + 0.30*X + 0.17*V + 0.15*K
    # Normalise rerank_score to [0,1] using sigmoid
    X = sigmoid_calibrate(rerank_score) if rerank_score != 0 else 0.5
    V = max(0, min(1, dense_sim))
    K = max(0, min(1, sparse_sim))

    M_raw = 0.38 * S_f + 0.30 * X + 0.17 * V + 0.15 * K

    contributions.append(FeatureContribution(feature="Cross-Encoder Score", value=round(X, 3), weight=0.30, contribution=round(0.30 * X, 4)))
    contributions.append(FeatureContribution(feature="Dense Similarity", value=round(V, 3), weight=0.17, contribution=round(0.17 * V, 4)))
    contributions.append(FeatureContribution(feature="Sparse Similarity", value=round(K, 3), weight=0.15, contribution=round(0.15 * K, 4)))

    # Hard constraint gate G(c) and soft penalty Q(c)
    G, Q, gate_notes = compute_gates(candidate, jd, features)
    M_adj = G * Q * M_raw

    if G == 0:
        contributions.append(FeatureContribution(feature="Hard Constraint Gate", value=0, weight=1.0, contribution=0, note="BLOCKED: " + "; ".join(gate_notes)))
    elif Q < 1.0:
        contributions.append(FeatureContribution(feature="Soft Penalty", value=round(Q, 2), weight=1.0, contribution=round(-1 * (1 - Q) * M_raw, 4), note="; ".join(gate_notes)))

    # Calibrate to 0-100
    match_score = round(100 * sigmoid_calibrate(M_adj, scale=3.0, shift=0.35), 1)
    match_score = max(0, min(100, match_score))

    return match_score, contributions


def compute_features(candidate: dict, jd: JobDescription) -> Dict[str, Any]:
    """Compute individual feature scores in [0, 1]."""
    features = {}
    cand_skills = {s["name"].lower(): s for s in candidate.get("skills", [])}

    # M_h: Must-have skill coverage
    jd_must = [s.name.lower() for s in jd.must_have_skills]
    matched_must = [s for s in jd_must if s in cand_skills]
    features["must_have_coverage"] = len(matched_must) / max(len(jd_must), 1)
    features["must_have_coverage_note"] = f"Matched {len(matched_must)}/{len(jd_must)}: {', '.join(matched_must) if matched_must else 'none'}"

    # N_h: Nice-to-have coverage
    jd_nice = [s.name.lower() for s in jd.nice_to_have_skills]
    matched_nice = [s for s in jd_nice if s in cand_skills]
    features["nice_to_have_coverage"] = len(matched_nice) / max(len(jd_nice), 1)
    features["nice_to_have_coverage_note"] = f"Matched {len(matched_nice)}/{len(jd_nice)}"

    # T: Title similarity (simple keyword overlap)
    jd_title_words = set(jd.role_title.lower().split())
    cand_title_words = set(candidate.get("current_title", "").lower().split())
    title_overlap = len(jd_title_words & cand_title_words) / max(len(jd_title_words), 1)
    features["title_similarity"] = min(1.0, title_overlap)
    features["title_similarity_note"] = candidate.get("current_title", "")

    # E: Experience fit
    yoe = candidate.get("years_experience", 0)
    if jd.min_years_experience <= yoe <= jd.max_years_experience:
        features["experience_fit"] = 1.0
        features["experience_fit_note"] = f"{yoe}y within {jd.min_years_experience}-{jd.max_years_experience}y band"
    elif yoe > jd.max_years_experience:
        overshoot = yoe - jd.max_years_experience
        features["experience_fit"] = max(0.3, 1.0 - overshoot * 0.1)
        features["experience_fit_note"] = f"{yoe}y exceeds max {jd.max_years_experience}y by {overshoot:.1f}y"
    else:
        deficit = jd.min_years_experience - yoe
        features["experience_fit"] = max(0.2, 1.0 - deficit * 0.15)
        features["experience_fit_note"] = f"{yoe}y below min {jd.min_years_experience}y by {deficit:.1f}y"

    # D: Domain/industry fit
    cand_ind = {i.lower() for i in candidate.get("industries", [])}
    jd_ind = {i.lower() for i in jd.industries}
    features["domain_fit"] = len(cand_ind & jd_ind) / max(len(jd_ind), 1)
    features["domain_fit_note"] = f"Industries: {', '.join(cand_ind & jd_ind) if cand_ind & jd_ind else 'no overlap'}"

    # P: Project relevance
    project_score = 0.0
    projects = candidate.get("projects", [])
    if projects:
        jd_keywords = set(w.lower() for s in jd.must_have_skills for w in s.name.split()) | set(k.lower() for k in jd.keywords)
        for proj in projects:
            proj_words = set(proj.get("summary", "").lower().split() + proj.get("name", "").lower().split())
            overlap = len(proj_words & jd_keywords)
            project_score += min(1.0, overlap * 0.2)
        project_score = min(1.0, project_score / len(projects))
    features["project_relevance"] = project_score
    features["project_relevance_note"] = f"{len(projects)} projects evaluated"

    # L: Location/work-mode fit
    cand_loc = candidate.get("location", "").lower()
    jd_locs = {l.lower() for l in jd.locations}
    cand_mode = candidate.get("work_preferences", {}).get("work_mode", "hybrid")
    loc_score = 0.0
    if cand_loc in jd_locs or "remote india" in jd_locs:
        loc_score = 1.0
    elif candidate.get("work_preferences", {}).get("open_to_relocation"):
        loc_score = 0.6
    else:
        loc_score = 0.2
    if jd.work_mode == cand_mode:
        loc_score = min(1.0, loc_score + 0.1)
    features["location_fit"] = loc_score
    features["location_fit_note"] = f"{candidate.get('location', '?')} ({cand_mode}) vs {', '.join(jd.locations)} ({jd.work_mode})"

    # C: Compensation/availability fit
    comp_score = 1.0
    if jd.salary_range_lpa:
        expected = candidate.get("compensation", {}).get("expected_lpa", 0)
        if expected <= jd.salary_range_lpa.max:
            comp_score = 1.0
        elif expected <= jd.salary_range_lpa.max * 1.15:
            comp_score = 0.7
        else:
            comp_score = 0.3
    notice = candidate.get("availability", {}).get("notice_period_days", 30)
    if notice <= jd.notice_period_days_max:
        comp_score = min(comp_score, 1.0)
    elif notice <= jd.notice_period_days_max * 1.3:
        comp_score = min(comp_score, 0.7)
    else:
        comp_score = min(comp_score, 0.4)
    features["compensation_fit"] = comp_score
    features["compensation_fit_note"] = f"Expected: {candidate.get('compensation', {}).get('expected_lpa', '?')} LPA, Notice: {notice}d"

    return features


def compute_gates(candidate: dict, jd: JobDescription, features: dict) -> Tuple[int, float, List[str]]:
    """Compute hard constraint gate G and soft penalty Q."""
    G = 1
    Q = 1.0
    notes = []

    # Hard gate: work mode blocker
    prefs = candidate.get("work_preferences", {})
    if jd.hard_constraints.must_accept_hybrid and prefs.get("work_mode") == "onsite":
        G = 0
        notes.append("Candidate is onsite-only, role requires hybrid")

    # Soft penalty: missing critical must-have
    if features.get("must_have_coverage", 1.0) < 0.5:
        Q = min(Q, 0.35)
        notes.append("Less than 50% must-have skills matched")

    # Soft penalty: experience below minimum by > 2 years
    yoe = candidate.get("years_experience", 0)
    if yoe < jd.min_years_experience - 2:
        Q = min(Q, 0.60)
        notes.append(f"Experience {yoe}y is {jd.min_years_experience - yoe:.1f}y below minimum")

    return G, Q, notes

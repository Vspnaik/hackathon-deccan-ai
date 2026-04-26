"""
Interest scoring engine implementing the DPR formula.
Converts outreach signals into a calibrated 0-100 Interest Score.
"""
from app.core.schemas import OutreachSignals
from app.core.calibration import sigmoid_calibrate


def calculate_interest_score(signals: OutreachSignals) -> tuple:
    """
    Compute the DPR Interest Score formula.
    
    I_raw = 0.35*I_e + 0.18*R_a + 0.12*W_a + 0.15*S_a + 0.10*N_p + 0.06*G_q + 0.04*F_t
    
    Returns:
        (interest_score_0_100, rationale_list)
    """
    # Raw interest
    I_raw = (
        0.35 * signals.I_e +
        0.18 * signals.R_a +
        0.12 * signals.W_a +
        0.15 * signals.S_a +
        0.10 * signals.N_p +
        0.06 * signals.G_q +
        0.04 * signals.F_t
    )

    # Calibrate
    interest = 100 * sigmoid_calibrate(I_raw, scale=3.5, shift=0.35)

    # Apply caps per DPR
    rationale = []

    if signals.declined:
        interest = 0.0
        rationale.append("Candidate explicitly declined the opportunity")
        return round(interest, 1), rationale

    if signals.salary_mismatch_pct > 25:
        interest = min(interest, 35.0)
        rationale.append(f"Salary mismatch of {signals.salary_mismatch_pct:.0f}% above budget — capped at 35")

    if signals.notice_overshoot_days > 45:
        interest = min(interest, 45.0)
        rationale.append(f"Notice period exceeds max by {signals.notice_overshoot_days} days — capped at 45")

    if signals.reconnect_later:
        interest = min(interest, 65.0)
        rationale.append("Candidate asked to reconnect later — capped at 65")

    # Build positive rationale
    if signals.I_e >= 0.7:
        rationale.append("Strong explicit interest expressed")
    elif signals.I_e >= 0.5:
        rationale.append("Moderate interest expressed")
    else:
        rationale.append("Low explicit interest signal")

    if signals.S_a >= 0.8:
        rationale.append("Salary expectations well-aligned")
    elif signals.S_a < 0.5:
        rationale.append(f"Salary concerns: mismatch ~{signals.salary_mismatch_pct:.0f}%")

    if signals.W_a >= 0.8:
        rationale.append("Work mode and location fully compatible")

    if signals.N_p >= 0.8:
        rationale.append("Notice period within acceptable range")
    elif signals.N_p < 0.5:
        rationale.append(f"Notice period risk: {signals.notice_overshoot_days}d over max")

    interest = max(0, min(100, round(interest, 1)))
    return interest, rationale


def classify_interest_bucket(interest_score: float, match_score: float) -> str:
    """Classify into DPR-defined buckets."""
    if match_score >= 70 and interest_score >= 60:
        return "Strong Shortlist"
    elif match_score >= 60 and interest_score >= 45:
        return "Recruiter Review"
    elif match_score >= 50 and interest_score >= 30:
        return "Park for Later"
    else:
        return "Not Recommended"

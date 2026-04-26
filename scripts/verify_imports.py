"""Quick verification script to test all module imports."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

results = []

try:
    from app.core.schemas import JobDescription, CandidateProfile, ShortlistEntry, OutreachSignals
    results.append("OK: schemas")
except Exception as e:
    results.append(f"FAIL: schemas - {e}")

try:
    from app.core.calibration import sigmoid_calibrate, linear_calibrate
    assert abs(sigmoid_calibrate(0.5) - 0.7310585786300049) < 0.01
    results.append("OK: calibration")
except Exception as e:
    results.append(f"FAIL: calibration - {e}")

try:
    from app.core.jd_parser import parse_jd
    jd = parse_jd("Senior Backend Engineer, Python, FastAPI, 4-8 years, Bengaluru hybrid, fintech, 18-28 LPA")
    assert jd.role_title != ""
    results.append(f"OK: jd_parser (parsed: {jd.role_title})")
except Exception as e:
    results.append(f"FAIL: jd_parser - {e}")

try:
    from app.core.match_scoring import calculate_match_score, compute_features
    results.append("OK: match_scoring")
except Exception as e:
    results.append(f"FAIL: match_scoring - {e}")

try:
    from app.core.interest_scoring import calculate_interest_score, classify_interest_bucket
    signals = OutreachSignals(I_e=0.8, R_a=0.7, W_a=0.9, S_a=0.9, N_p=1.0, G_q=0.7, F_t=0.8)
    score, rationale = calculate_interest_score(signals)
    assert 0 <= score <= 100
    results.append(f"OK: interest_scoring (score={score})")
except Exception as e:
    results.append(f"FAIL: interest_scoring - {e}")

try:
    from app.core.explainability import generate_rationale, get_status_label
    results.append("OK: explainability")
except Exception as e:
    results.append(f"FAIL: explainability - {e}")

try:
    from app.core.outreach_simulator import simulate_outreach
    results.append("OK: outreach_simulator")
except Exception as e:
    results.append(f"FAIL: outreach_simulator - {e}")

try:
    from app.core.retrieval import hard_filter, rules_score, reciprocal_rank_fusion
    results.append("OK: retrieval")
except Exception as e:
    results.append(f"FAIL: retrieval - {e}")

try:
    from app.core.reranker import build_jd_text
    results.append("OK: reranker")
except Exception as e:
    results.append(f"FAIL: reranker - {e}")

try:
    import json
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synthetic_candidates.json")) as f:
        candidates = json.load(f)
    assert len(candidates) == 120
    results.append(f"OK: synthetic data ({len(candidates)} candidates)")
except Exception as e:
    results.append(f"FAIL: synthetic data - {e}")

try:
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synthetic_jds.json")) as f:
        jds = json.load(f)
    assert len(jds) == 10
    results.append(f"OK: synthetic JDs ({len(jds)} JDs)")
except Exception as e:
    results.append(f"FAIL: synthetic JDs - {e}")

print("\n=== VERIFICATION RESULTS ===")
for r in results:
    print(f"  {r}")
passed = sum(1 for r in results if r.startswith("OK"))
total = len(results)
print(f"\n{passed}/{total} checks passed.")

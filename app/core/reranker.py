"""
Cross-encoder reranker using sentence-transformers.
Scores (JD text, candidate profile text) pairs for precision-focused reranking.
"""
import os
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from dotenv import load_dotenv

load_dotenv()

RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2")

_reranker = None


def get_reranker() -> CrossEncoder:
    """Lazy-load the cross-encoder model singleton."""
    global _reranker
    if _reranker is None:
        print(f"[Reranker] Loading model: {RERANKER_MODEL}")
        _reranker = CrossEncoder(RERANKER_MODEL)
        print("[Reranker] Model loaded.")
    return _reranker


def rerank_candidates(
    jd_text: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Rerank candidates using cross-encoder.
    
    Args:
        jd_text: Full JD text or structured JD summary.
        candidates: List of candidate dicts from retrieval stage.
        top_k: Number of top candidates to return.
    
    Returns:
        Top-K candidates sorted by rerank score, each with '_rerank_score' added.
    """
    if not candidates:
        return []

    reranker = get_reranker()

    # Build text pairs: (JD text, candidate profile text)
    pairs = []
    for cand in candidates:
        cand_text = cand.get("profile_text", "")
        if not cand_text:
            # Build from structured data
            skills = ", ".join([s["name"] for s in cand.get("skills", [])[:8]])
            cand_text = f"{cand.get('current_title', '')} with {cand.get('years_experience', 0)} years. Skills: {skills}"
        pairs.append((jd_text, cand_text))

    # Score all pairs
    scores = reranker.predict(pairs, show_progress_bar=False)

    # Attach scores and sort
    for cand, score in zip(candidates, scores):
        cand["_rerank_score"] = float(score)

    # Sort by rerank score descending
    candidates.sort(key=lambda x: x.get("_rerank_score", 0), reverse=True)

    return candidates[:top_k]


def build_jd_text(jd) -> str:
    """Build a readable JD text string for the cross-encoder input."""
    parts = [f"Role: {jd.role_title}"]
    if jd.seniority:
        parts.append(f"Seniority: {jd.seniority}")
    if jd.must_have_skills:
        skills = ", ".join(s.name for s in jd.must_have_skills)
        parts.append(f"Required skills: {skills}")
    if jd.nice_to_have_skills:
        skills = ", ".join(s.name for s in jd.nice_to_have_skills)
        parts.append(f"Nice to have: {skills}")
    if jd.min_years_experience or jd.max_years_experience:
        parts.append(f"Experience: {jd.min_years_experience}-{jd.max_years_experience} years")
    if jd.locations:
        parts.append(f"Location: {', '.join(jd.locations)}")
    if jd.work_mode:
        parts.append(f"Work mode: {jd.work_mode}")
    if jd.industries:
        parts.append(f"Industries: {', '.join(jd.industries)}")
    if jd.keywords:
        parts.append(f"Keywords: {', '.join(jd.keywords)}")
    return ". ".join(parts)

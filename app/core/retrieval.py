"""
Hybrid retrieval engine: dense + sparse + rules-based scoring with RRF fusion.
Implements hard constraint filtering before retrieval.
"""
import os
import sys
import numpy as np
from typing import List, Tuple, Dict, Any
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.schemas import JobDescription
from app.services.embeddings import encode_text
from dotenv import load_dotenv

load_dotenv()

RRF_K = 60  # RRF constant


def hard_filter(candidate: dict, jd: JobDescription) -> bool:
    """Return True if candidate passes all hard constraints."""
    prefs = candidate.get("work_preferences", {})
    avail = candidate.get("availability", {})
    comp = candidate.get("compensation", {})

    # Work mode check
    if jd.hard_constraints.must_accept_hybrid:
        cand_mode = prefs.get("work_mode", "hybrid")
        if cand_mode == "onsite":
            return False

    # Notice period check
    if avail.get("notice_period_days", 0) > jd.notice_period_days_max * 1.5:
        return False

    # Salary floor impossible check
    if jd.salary_range_lpa:
        expected = comp.get("expected_lpa", 0)
        if expected > jd.salary_range_lpa.max * 1.5:
            return False

    return True


def rules_score(candidate: dict, jd: JobDescription) -> float:
    """
    Compute structured rules-based score from explicit field comparisons.
    Returns a score in [0, 1].
    """
    score = 0.0
    cand_skills = {s["name"].lower() for s in candidate.get("skills", [])}
    jd_must = {s.name.lower() for s in jd.must_have_skills}
    jd_nice = {s.name.lower() for s in jd.nice_to_have_skills}

    # Must-have skill overlap (40%)
    must_overlap = len(cand_skills & jd_must) / max(len(jd_must), 1)
    score += 0.40 * must_overlap

    # Nice-to-have skill overlap (10%)
    nice_overlap = len(cand_skills & jd_nice) / max(len(jd_nice), 1)
    score += 0.10 * nice_overlap

    # Experience fit (20%)
    yoe = candidate.get("years_experience", 0)
    if jd.min_years_experience <= yoe <= jd.max_years_experience:
        score += 0.20
    elif yoe > jd.max_years_experience:
        score += 0.10
    else:
        deficit = jd.min_years_experience - yoe
        score += max(0.0, 0.20 - deficit * 0.05)

    # Location match (15%)
    cand_loc = candidate.get("location", "").lower()
    jd_locs = {l.lower() for l in jd.locations}
    if cand_loc in jd_locs or "remote india" in jd_locs:
        score += 0.15
    elif candidate.get("work_preferences", {}).get("open_to_relocation"):
        score += 0.08

    # Industry match (15%)
    cand_ind = {i.lower() for i in candidate.get("industries", [])}
    jd_ind = {i.lower() for i in jd.industries}
    ind_overlap = len(cand_ind & jd_ind) / max(len(jd_ind), 1)
    score += 0.15 * ind_overlap

    return min(1.0, score)


def dense_retrieve(jd: JobDescription, session, top_k: int = 80) -> List[Tuple[str, float]]:
    """Dense retrieval using pgvector cosine similarity."""
    from sqlalchemy import text as sa_text
    jd_text = f"{jd.role_title} {jd.seniority} {' '.join(s.name for s in jd.must_have_skills)} {' '.join(jd.keywords)}"
    jd_embedding = encode_text(jd_text)

    query = sa_text("""
        SELECT candidate_id, 1 - (embedding <=> :emb::vector) AS similarity
        FROM candidates
        ORDER BY embedding <=> :emb::vector
        LIMIT :limit
    """)
    results = session.execute(query, {"emb": str(jd_embedding), "limit": top_k}).fetchall()
    return [(r[0], float(r[1])) for r in results]


def sparse_retrieve(jd: JobDescription, session, top_k: int = 80) -> List[Tuple[str, float]]:
    """Sparse retrieval using PostgreSQL full-text search."""
    from sqlalchemy import text as sa_text
    search_terms = " | ".join(
        [s.name for s in jd.must_have_skills] + jd.keywords[:3] + [jd.role_title]
    )
    # Sanitize for tsquery
    search_terms = search_terms.replace(".", " ").replace("/", " ")

    query = sa_text("""
        SELECT candidate_id,
               ts_rank(to_tsvector('english', profile_text), to_tsquery('english', :terms)) AS rank
        FROM candidates
        WHERE to_tsvector('english', profile_text) @@ to_tsquery('english', :terms)
        ORDER BY rank DESC
        LIMIT :limit
    """)
    try:
        results = session.execute(query, {"terms": search_terms, "limit": top_k}).fetchall()
        return [(r[0], float(r[1])) for r in results]
    except Exception as e:
        print(f"[Retrieval] Sparse search error: {e}. Skipping sparse channel.")
        return []


def reciprocal_rank_fusion(
    rankings: List[List[Tuple[str, float]]],
    k: int = RRF_K
) -> List[Tuple[str, float]]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion."""
    scores = defaultdict(float)
    for ranking in rankings:
        for rank_pos, (cand_id, _) in enumerate(ranking):
            scores[cand_id] += 1.0 / (k + rank_pos + 1)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return fused


def retrieve_candidates(
    jd: JobDescription,
    top_k: int = 30,
    use_db: bool = True,
) -> List[Dict[str, Any]]:
    """
    Full hybrid retrieval pipeline:
    1. Hard filter
    2. Dense retrieval (pgvector)
    3. Sparse retrieval (full-text)
    4. Rules-based scoring
    5. RRF fusion
    Returns top-K candidate dicts with retrieval scores.
    Auto-falls back to JSON mode if DB is unavailable.
    """
    if use_db:
        try:
            return _retrieve_from_db(jd, top_k)
        except Exception as e:
            print(f"[Retrieval] DB retrieval failed: {e}")
            print(f"[Retrieval] Falling back to JSON-only mode.")
            return _retrieve_from_json(jd, top_k)
    else:
        return _retrieve_from_json(jd, top_k)


def _retrieve_from_db(jd: JobDescription, top_k: int) -> List[Dict[str, Any]]:
    """Retrieve from PostgreSQL + pgvector."""
    from app.db.models import DBCandidate, get_session
    from sqlalchemy import text as sa_text
    session = get_session()
    try:
        # Dense retrieval
        dense_results = dense_retrieve(jd, session, top_k=80)

        # Sparse retrieval
        sparse_results = sparse_retrieve(jd, session, top_k=80)

        # Get all candidates for rules scoring
        all_candidates = session.query(DBCandidate).all()
        cand_map = {c.candidate_id: c.profile_json for c in all_candidates}

        # Rules-based scoring
        rules_results = []
        for cand_id, profile in cand_map.items():
            if hard_filter(profile, jd):
                rs = rules_score(profile, jd)
                rules_results.append((cand_id, rs))
        rules_results.sort(key=lambda x: x[1], reverse=True)
        rules_results = rules_results[:80]

        # RRF fusion
        fused = reciprocal_rank_fusion([dense_results, sparse_results, rules_results])

        # Filter by hard constraints and return top-K
        results = []
        for cand_id, rrf_score in fused:
            if cand_id in cand_map and hard_filter(cand_map[cand_id], jd):
                profile = cand_map[cand_id]
                profile["_rrf_score"] = rrf_score
                profile["_rules_score"] = rules_score(profile, jd)
                # Get dense similarity
                dense_sim = dict(dense_results).get(cand_id, 0.0)
                sparse_sim = dict(sparse_results).get(cand_id, 0.0)
                profile["_dense_sim"] = dense_sim
                profile["_sparse_sim"] = sparse_sim
                results.append(profile)
                if len(results) >= top_k:
                    break

        return results
    finally:
        session.close()


# Cache for pre-computed candidate embeddings (computed once, reused across searches)
_candidate_cache = {"candidates": None, "embeddings": None}


def _load_candidates_with_embeddings():
    """Load candidates from JSON and pre-compute embeddings (cached after first call)."""
    import json
    from app.services.embeddings import encode_texts

    if _candidate_cache["candidates"] is not None:
        return _candidate_cache["candidates"], _candidate_cache["embeddings"]

    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(project_root, "data", "synthetic_candidates.json")
    if not os.path.exists(data_path):
        print(f"[Retrieval] No synthetic_candidates.json found at {data_path}")
        return [], None

    with open(data_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    print(f"[Retrieval] Pre-computing embeddings for {len(candidates)} candidates (one-time)...")
    texts = [c["profile_text"] for c in candidates]
    embeddings = np.array(encode_texts(texts))
    print(f"[Retrieval] Embeddings cached. Shape: {embeddings.shape}")

    _candidate_cache["candidates"] = candidates
    _candidate_cache["embeddings"] = embeddings
    return candidates, embeddings


def _retrieve_from_json(jd: JobDescription, top_k: int) -> List[Dict[str, Any]]:
    """Fallback: retrieve from JSON file with cached embeddings."""
    candidates, embeddings = _load_candidates_with_embeddings()
    if not candidates:
        return []

    # Encode JD (single fast call)
    jd_text = f"{jd.role_title} {' '.join(s.name for s in jd.must_have_skills)} {' '.join(jd.keywords)}"
    jd_emb = np.array(encode_text(jd_text))

    # Compute all dense similarities at once via matrix multiplication
    dense_sims = embeddings @ jd_emb

    # Filter + score
    scored = []
    for i, cand in enumerate(candidates):
        if not hard_filter(cand, jd):
            continue
        rs = rules_score(cand, jd)
        dense_sim = float(dense_sims[i])
        cand["_rules_score"] = rs
        cand["_dense_sim"] = dense_sim
        cand["_sparse_sim"] = 0.0
        cand["_rrf_score"] = rs * 0.5 + dense_sim * 0.5
        scored.append(cand)

    scored.sort(key=lambda x: x["_rrf_score"], reverse=True)
    return scored[:top_k]

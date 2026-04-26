"""
FastAPI backend for the Talent Scout Agent.
Orchestrates the full pipeline: parse JD → retrieve → rerank → score → outreach → shortlist.
"""
import json
import os
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.schemas import (
    JobDescription, ShortlistEntry, ShortlistResponse, ParsedJDResponse,
    OutreachSignals, FeatureContribution,
)
from app.core.jd_parser import parse_jd
from app.core.retrieval import retrieve_candidates
from app.core.reranker import rerank_candidates, build_jd_text
from app.core.match_scoring import calculate_match_score
from app.core.outreach_simulator import simulate_outreach
from app.core.interest_scoring import calculate_interest_score, classify_interest_bucket
from app.core.explainability import generate_rationale, get_status_label

app = FastAPI(title="Talent Scout AI", version="1.0.0", description="AI-Powered Talent Scouting and Engagement Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JDInput(BaseModel):
    jd_text: str
    use_db: bool = True
    top_k: int = 10
    run_outreach: bool = True


class OutreachInput(BaseModel):
    candidate_id: str
    jd: JobDescription


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "talent-scout-ai", "timestamp": datetime.now().isoformat()}


@app.post("/parse-jd", response_model=ParsedJDResponse)
def parse_job_description(input: JDInput):
    """Parse raw JD text into structured JobDescription schema."""
    try:
        jd = parse_jd(input.jd_text)
        return ParsedJDResponse(success=True, jd=jd)
    except Exception as e:
        return ParsedJDResponse(success=False, error=str(e))


@app.post("/search", response_model=ShortlistResponse)
def search_candidates(input: JDInput):
    """
    Full pipeline: parse JD → retrieve → rerank → score → outreach → shortlist.
    """
    try:
        # 1. Parse JD
        jd = parse_jd(input.jd_text)

        # 2. Retrieve candidates (hybrid: dense + sparse + rules)
        candidates = retrieve_candidates(jd, top_k=30, use_db=input.use_db)
        total_passed = len(candidates)

        if not candidates:
            return ShortlistResponse(
                job_id=jd.job_id or "parsed",
                role_title=jd.role_title,
                generated_at=datetime.now().isoformat(),
                total_candidates_evaluated=0,
                total_passed_filters=0,
                shortlist=[],
            )

        # 3. Rerank top 30 → top K
        jd_text = build_jd_text(jd)
        reranked = rerank_candidates(jd_text, candidates, top_k=input.top_k)

        # 4. Score and optionally run outreach
        shortlist = []
        for rank_idx, cand in enumerate(reranked):
            # Match score
            rerank_score = cand.get("_rerank_score", 0.0)
            dense_sim = cand.get("_dense_sim", 0.0)
            sparse_sim = cand.get("_sparse_sim", 0.0)

            match_score, contributions = calculate_match_score(
                cand, jd,
                rerank_score=rerank_score,
                dense_sim=dense_sim,
                sparse_sim=sparse_sim,
            )

            # Outreach simulation (top candidates only)
            interest_score = 50.0
            interest_rationale = ["Outreach not yet simulated"]
            conversation_log = []

            if input.run_outreach:
                signals, conversation_log = simulate_outreach(cand, jd)
                interest_score, interest_rationale = calculate_interest_score(signals)

            # Shortlist rank score
            rank_score = round(0.70 * match_score + 0.30 * interest_score, 1)

            # Explainability
            match_rationale, interest_rationale_final, risks = generate_rationale(
                cand, jd, contributions, interest_rationale, match_score, interest_score
            )

            # Bucket
            bucket = classify_interest_bucket(interest_score, match_score)

            entry = ShortlistEntry(
                rank=rank_idx + 1,
                candidate_id=cand.get("candidate_id", f"cand_{rank_idx}"),
                full_name=cand.get("full_name", "Unknown"),
                headline=cand.get("headline", ""),
                current_title=cand.get("current_title", ""),
                location=cand.get("location", ""),
                years_experience=cand.get("years_experience", 0),
                match_score=match_score,
                interest_score=interest_score,
                shortlist_rank_score=rank_score,
                match_rationale=match_rationale,
                interest_rationale=interest_rationale_final,
                risks=risks,
                feature_contributions=contributions,
                conversation_log=conversation_log,
                bucket=bucket,
            )
            shortlist.append(entry)

        # Sort by shortlist_rank_score
        shortlist.sort(key=lambda x: x.shortlist_rank_score, reverse=True)
        for i, entry in enumerate(shortlist):
            entry.rank = i + 1

        # Load total candidate count
        total_evaluated = 120  # default synthetic pool size
        if input.use_db:
            try:
                from app.db.models import get_session, DBCandidate
                session = get_session()
                total_evaluated = session.query(DBCandidate).count()
                session.close()
            except Exception:
                pass

        return ShortlistResponse(
            job_id=jd.job_id or "parsed",
            role_title=jd.role_title,
            generated_at=datetime.now().isoformat(),
            total_candidates_evaluated=total_evaluated,
            total_passed_filters=total_passed,
            shortlist=shortlist,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

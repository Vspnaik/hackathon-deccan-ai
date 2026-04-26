"""
Pydantic v2 schemas for the Talent Scouting Agent.
Matches the strict JSON schemas defined in the DPR.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# JD Schema Models
# ──────────────────────────────────────────────

class SkillWeight(BaseModel):
    """A skill with an importance weight for the JD."""
    name: str
    weight: float = Field(ge=0.0, le=1.0)


class SalaryRange(BaseModel):
    """Salary range in LPA (Lakhs Per Annum)."""
    min: float
    max: float


class HardConstraints(BaseModel):
    """Non-negotiable requirements that gate candidates."""
    work_authorisation_required: bool = False
    must_accept_hybrid: bool = False


class JobDescription(BaseModel):
    """Full structured JD schema as defined in the DPR."""
    job_id: str = ""
    role_title: str = ""
    department: str = ""
    seniority: str = ""
    employment_type: str = "full_time"
    work_mode: str = "hybrid"
    locations: List[str] = Field(default_factory=list)
    must_have_skills: List[SkillWeight] = Field(default_factory=list)
    nice_to_have_skills: List[SkillWeight] = Field(default_factory=list)
    min_years_experience: float = 0
    max_years_experience: float = 20
    industries: List[str] = Field(default_factory=list)
    education_preferences: List[str] = Field(default_factory=list)
    salary_range_lpa: Optional[SalaryRange] = None
    notice_period_days_max: int = 90
    keywords: List[str] = Field(default_factory=list)
    hard_constraints: HardConstraints = Field(default_factory=HardConstraints)


# ──────────────────────────────────────────────
# Candidate Schema Models
# ──────────────────────────────────────────────

class CandidateSkill(BaseModel):
    """A candidate's skill with proficiency and recency."""
    name: str
    level: int = Field(ge=1, le=5, description="1=beginner, 5=expert")
    years: float = 0
    last_used_months_ago: int = 0


class Education(BaseModel):
    degree: str = ""
    field: str = ""


class Project(BaseModel):
    name: str = ""
    summary: str = ""
    impact: str = ""


class WorkPreferences(BaseModel):
    work_mode: str = "hybrid"
    open_to_relocation: bool = False
    preferred_locations: List[str] = Field(default_factory=list)


class Compensation(BaseModel):
    current_lpa: float = 0
    expected_lpa: float = 0


class Availability(BaseModel):
    notice_period_days: int = 30
    actively_looking: bool = True


class InterestProfile(BaseModel):
    """Latent interest profile used by the outreach simulator."""
    career_goals: List[str] = Field(default_factory=list)
    salary_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    reply_style: str = "concise_positive"


class CandidateProfile(BaseModel):
    """Full candidate profile schema as defined in the DPR."""
    candidate_id: str = ""
    full_name: str = ""
    headline: str = ""
    location: str = ""
    timezone: str = "Asia/Kolkata"
    current_title: str = ""
    years_experience: float = 0
    skills: List[CandidateSkill] = Field(default_factory=list)
    title_history: List[str] = Field(default_factory=list)
    industries: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    work_preferences: WorkPreferences = Field(default_factory=WorkPreferences)
    compensation: Compensation = Field(default_factory=Compensation)
    availability: Availability = Field(default_factory=Availability)
    interest_profile: InterestProfile = Field(default_factory=InterestProfile)
    profile_text: str = ""

    # Hidden ground-truth labels for evaluation (not exposed in UI)
    latent_match_truth: Optional[Dict[str, float]] = None
    latent_interest_truth: Optional[Dict[str, float]] = None


# ──────────────────────────────────────────────
# Outreach Signal Schema
# ──────────────────────────────────────────────

class OutreachSignals(BaseModel):
    """Structured signals extracted from simulated outreach conversation."""
    I_e: float = Field(default=0.5, ge=0.0, le=1.0, description="Explicit interest signal")
    R_a: float = Field(default=0.5, ge=0.0, le=1.0, description="Role alignment")
    W_a: float = Field(default=0.5, ge=0.0, le=1.0, description="Work-mode/location alignment")
    S_a: float = Field(default=0.5, ge=0.0, le=1.0, description="Salary alignment")
    N_p: float = Field(default=0.5, ge=0.0, le=1.0, description="Notice-period alignment")
    G_q: float = Field(default=0.5, ge=0.0, le=1.0, description="Engagement quality")
    F_t: float = Field(default=0.5, ge=0.0, le=1.0, description="Follow-through completion")
    declined: bool = False
    reconnect_later: bool = False
    salary_mismatch_pct: float = 0.0
    notice_overshoot_days: int = 0


# ──────────────────────────────────────────────
# Feature Contribution (for explainability)
# ──────────────────────────────────────────────

class FeatureContribution(BaseModel):
    """Single row in the feature contribution table."""
    feature: str
    value: float
    weight: float
    contribution: float
    note: str = ""


# ──────────────────────────────────────────────
# API Response Models
# ──────────────────────────────────────────────

class ShortlistEntry(BaseModel):
    """One candidate in the final shortlist."""
    rank: int
    candidate_id: str
    full_name: str
    headline: str = ""
    current_title: str = ""
    location: str = ""
    years_experience: float = 0
    match_score: float
    interest_score: float
    shortlist_rank_score: float
    match_rationale: List[str] = Field(default_factory=list)
    interest_rationale: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    feature_contributions: List[FeatureContribution] = Field(default_factory=list)
    conversation_log: List[Dict[str, str]] = Field(default_factory=list)
    bucket: str = "reject"


class ShortlistResponse(BaseModel):
    """Complete shortlist response returned by the API."""
    job_id: str
    role_title: str = ""
    generated_at: str
    total_candidates_evaluated: int = 0
    total_passed_filters: int = 0
    shortlist: List[ShortlistEntry] = Field(default_factory=list)


class ParsedJDResponse(BaseModel):
    """Response from JD parsing endpoint."""
    success: bool
    jd: Optional[JobDescription] = None
    error: Optional[str] = None

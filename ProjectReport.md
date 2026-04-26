# AI-Powered Talent Scouting and Engagement Agent — Project Report

## 1. Executive Summary

This project implements a production-ready AI talent scouting system that automates the end-to-end recruiting pipeline: parsing job descriptions, discovering matching candidates from a synthetic pool, simulating recruiter outreach conversations, and producing a recruiter-ready shortlist with calibrated **Match Scores**, **Interest Scores**, and auditable rationale for every ranking decision.

The system uses a **hybrid retrieval and reranking** architecture that separates recall, ranking, and explanation into distinct, testable components — stronger than a single-model prompt-only approach.

---

## 2. System Architecture

### 2.1 High-Level Pipeline

```
┌──────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────┐
│  Raw JD  │──▶│  JD Parser   │───▶│  Hard Filters  │──▶│   Hybrid    │
│  Text    │    │ (LLM/Regex)  │    │  (Constraints) │    │  Retrieval  │
└──────────┘    └──────────────┘    └────────────────┘    └──────┬──────┘
                                                                 │
                        ┌────────────────────────────────────────┘
                        ▼
               ┌────────────────┐    ┌───────────────┐    ┌──────────────┐
               │  RRF Fusion    │──▶│  Cross-Encoder│───▶│    Match     │
               │  (3 channels)  │    │  Reranker     │    │   Scoring    │
               └────────────────┘    └───────────────┘    └──────┬───────┘
                                                                 │
                        ┌────────────────────────────────────────┘
                        ▼
               ┌────────────────┐    ┌───────────────┐    ┌──────────────┐
               │   Outreach     │──▶│   Interest    │───▶│   Shortlist  │
               │  Simulation    │    │   Scoring     │    │  + Rationale │
               └────────────────┘    └───────────────┘    └──────────────┘
```

### 2.2 Component Responsibilities

| Stage | Module | Purpose |
|-------|--------|---------|
| 1. Parse | `jd_parser.py` | LLM structured extraction → `JobDescription` schema; regex fallback |
| 2. Filter | `retrieval.py` → `hard_filter()` | Reject candidates failing non-negotiable constraints |
| 3. Retrieve | `retrieval.py` | Dense (pgvector ANN) + Sparse (full-text) + Rules-based scoring |
| 4. Fuse | `retrieval.py` → `reciprocal_rank_fusion()` | RRF merges 3 ranked lists into a single fused ranking |
| 5. Rerank | `reranker.py` | Cross-encoder precision scoring on (JD, candidate) text pairs |
| 6. Match Score | `match_scoring.py` | DPR formula: weighted features + constraint gates + calibration |
| 7. Outreach | `outreach_simulator.py` | Multi-turn conversation simulation (LLM or deterministic) |
| 8. Interest Score | `interest_scoring.py` | Converts outreach signals into calibrated 0–100 score |
| 9. Explain | `explainability.py` | Generates faithful rationale from evidence, not LLM opinions |
| 10. Serve | `api/main.py` + `ui/app.py` | FastAPI backend + Streamlit dashboard |

---

## 3. Project Structure

```
clauderesagnt/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI backend (orchestrator)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic v2 data contracts
│   │   ├── jd_parser.py            # JD parsing (LLM + regex fallback)
│   │   ├── retrieval.py            # Hybrid retrieval + RRF fusion
│   │   ├── reranker.py             # Cross-encoder reranking
│   │   ├── match_scoring.py        # Match score formula + gates
│   │   ├── interest_scoring.py     # Interest score formula + caps
│   │   ├── outreach_simulator.py   # Conversation simulation
│   │   ├── explainability.py       # Rationale generation
│   │   └── calibration.py          # Sigmoid/Platt/isotonic calibration
│   ├── db/
│   │   ├── __init__.py
│   │   └── models.py               # SQLAlchemy + pgvector models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_client.py           # LLM abstraction (Gemini + mock)
│   │   └── embeddings.py           # Sentence-transformers wrapper
│   └── ui/
│       ├── app.py                  # Streamlit role-selection gateway
│       └── pages/
│           ├── 1_Candidate_Profile.py # Candidate resume form
│           ├── 2_Interest_Chat.py     # AI interest assessment chat
│           └── 3_HR_Dashboard.py      # Recruiter sourcing dashboard
├── data/
│   ├── synthetic_candidates.json   # 120 generated candidate profiles
│   └── synthetic_jds.json          # 10 curated job descriptions
├── scripts/
│   ├── generate_synthetic_data.py  # Candidate/JD data generator
│   ├── build_index.py              # DB embedding indexer
│   └── verify_imports.py           # Import verification utility
├── docker-compose.yml              # PostgreSQL + pgvector container
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env                            # Local configuration (not committed)
├── README.md                       # Quick-start guide
└── ProjectReport.md                # This document
```

---

## 4. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Backend API** | FastAPI + Uvicorn | ≥0.115 | REST API orchestrating the pipeline |
| **Frontend** | Streamlit | ≥1.45 | Multi-page Recruiter & Candidate UI |
| **Database** | PostgreSQL 16 + pgvector | pg16 | Vector store for ANN search |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | ≥3.4 | 384-dim dense embeddings (local, CPU) |
| **Reranker** | cross-encoder (`ms-marco-MiniLM-L6-v2`) | — | Precision reranking of (query, doc) pairs |
| **LLM** | Google Gemini 2.5 Flash | — | JD parsing, conversation generation |
| **ORM** | SQLAlchemy 2.0 | ≥2.0 | Database models and queries |
| **Data Validation** | Pydantic v2 | ≥2.11 | Strict JSON schema enforcement |
| **Data Generation** | Faker | ≥40.0 | Synthetic candidate profile generation |
| **ML Utilities** | scikit-learn, NumPy | — | Calibration, vector math |

### 4.1 Dual-Mode Architecture

The system operates in two modes:

| Mode | Requirements | Retrieval Method |
|------|-------------|-----------------|
| **DB Mode** | PostgreSQL + pgvector running | Dense (pgvector ANN) + Sparse (full-text) + Rules |
| **JSON Mode** | No database needed | Dense (cached embeddings + NumPy) + Rules |

JSON mode auto-activates when the database is unavailable, enabling fully offline demos.

---

## 5. Data Model

### 5.1 JobDescription Schema

```
JobDescription
├── job_id, role_title, department, seniority
├── employment_type, work_mode
├── locations[]
├── must_have_skills[] ─── SkillWeight {name, weight: 0.0–1.0}
├── nice_to_have_skills[] ─── SkillWeight
├── min_years_experience, max_years_experience
├── industries[], education_preferences[]
├── salary_range_lpa ─── SalaryRange {min, max}
├── notice_period_days_max
├── keywords[]
└── hard_constraints ─── HardConstraints {work_authorisation, must_accept_hybrid}
```

### 5.2 CandidateProfile Schema

```
CandidateProfile
├── candidate_id, full_name, headline, location, timezone
├── current_title, years_experience
├── skills[] ─── CandidateSkill {name, level: 1–5, years, last_used_months_ago}
├── title_history[], industries[], certifications[]
├── education[] ─── Education {degree, field}
├── projects[] ─── Project {name, summary, impact}
├── work_preferences ─── WorkPreferences {work_mode, open_to_relocation, preferred_locations}
├── compensation ─── Compensation {current_lpa, expected_lpa}
├── availability ─── Availability {notice_period_days, actively_looking}
├── interest_profile ─── InterestProfile {career_goals, salary_sensitivity, reply_style}
└── profile_text (flattened text for embedding)
```

### 5.3 Synthetic Data

- **120 candidates** across 6 role families: Backend, Frontend, Data Engineering, ML/AI, DevOps/SRE, Full-Stack
- **10 curated JDs** with hidden relevance labels for evaluation
- Generated using O*NET/ESCO-seeded skill taxonomies via Faker

---

## 6. Scoring Methodology

### 6.1 Match Score (0–100)

The Match Score quantifies how well a candidate's profile aligns with the JD requirements.

#### Step 1: Structured Feature Scores (S_f)

Each feature is scored in [0, 1] and weighted:

| Feature | Symbol | Weight | How Computed |
|---------|--------|--------|-------------|
| Must-have skill coverage | M_h | 0.30 | `|matched ∩ required| / |required|` |
| Nice-to-have coverage | N_h | 0.08 | `|matched ∩ nice| / |nice|` |
| Title similarity | T | 0.10 | Word overlap between JD title and candidate title |
| Experience fit | E | 0.12 | 1.0 if in band, penalised by deficit or overshoot |
| Domain/industry fit | D | 0.10 | `|candidate_industries ∩ jd_industries| / |jd_industries|` |
| Project relevance | P | 0.12 | Keyword overlap between projects and JD skills/keywords |
| Location/work-mode fit | L | 0.08 | Location match + work-mode compatibility |
| Compensation/notice fit | C | 0.10 | Salary within budget + notice within max |

```
S_f = 0.30·M_h + 0.08·N_h + 0.10·T + 0.12·E + 0.10·D + 0.12·P + 0.08·L + 0.10·C
```

#### Step 2: Raw Match Score (M_raw)

Combines structured fit with retrieval signals:

```
M_raw = 0.38·S_f + 0.30·X + 0.17·V + 0.15·K
```

| Signal | Source |
|--------|--------|
| X = Cross-encoder rerank score | `cross-encoder/ms-marco-MiniLM-L6-v2` sigmoid-normalised |
| V = Dense similarity | Cosine similarity from `all-MiniLM-L6-v2` embeddings |
| K = Sparse similarity | PostgreSQL `ts_rank` full-text score |

#### Step 3: Constraint Gates

```
M_adj = G(c) · Q(c) · M_raw
```

| Gate | Type | Condition | Effect |
|------|------|-----------|--------|
| G(c) | Hard | Onsite-only candidate for hybrid role | G = 0 → blocked |
| Q(c) | Soft | <50% must-have skills matched | Q = 0.35 |
| Q(c) | Soft | Experience >2y below minimum | Q = 0.60 |

#### Step 4: Calibration

```
MatchScore = 100 × σ(M_adj; scale=3.0, shift=0.35)
```

Where σ is the Platt/sigmoid function: `σ(x) = 1 / (1 + e^(-scale·(x - shift)))`

---

### 6.2 Interest Score (0–100)

The Interest Score measures a candidate's likely willingness to engage with the opportunity, captured via the multi-turn AI chat on the candidate portal.

#### Real-time Chat Scoring

The score is calculated dynamically based on conversational signals during the 5-question AI assessment:

1. **Base Baseline:** Starts at `55`
2. **High-Intent Keywords (+5 each):** "actively", "immediately", "asap", "definitely", "very interested", "looking forward", "ready", etc.
3. **Low-Intent Keywords (-8 each):** "just exploring", "not sure", "passive", "probably not", "hard pass", etc.
4. **Engagement Depth (Answer Length):**
   - Average answer > 80 characters: `+10 points`
   - Average answer > 40 characters: `+5 points`

```
InterestScore = min(98, max(20, 55 + (HighHits * 5) - (LowHits * 8) + LengthBonus))
```

*Note: For simulated candidates where chat hasn't occurred, the system defaults to a baseline of 50.0.*

---

### 6.3 Shortlist Ranking

```
ShortlistRankScore = 0.70 × MatchScore + 0.30 × InterestScore
```

### 6.4 Bucket Classification

| Bucket | Condition |
|--------|-----------|
| 🟢 **Strong Shortlist** | Match ≥ 70 AND Interest ≥ 60 |
| 🟡 **Recruiter Review** | Match ≥ 60 AND Interest ≥ 45 |
| ⚪ **Park for Later** | Match ≥ 50 AND Interest ≥ 30 |
| 🔴 **Not Recommended** | Otherwise |

---

## 7. Retrieval Strategy

### 7.1 Hybrid Retrieval (3 Channels)

| Channel | Method | Top-K | Technology |
|---------|--------|-------|-----------|
| **Dense** | Cosine similarity on 384-dim embeddings | 80 | pgvector HNSW index / NumPy |
| **Sparse** | Full-text search with `ts_rank` | 80 | PostgreSQL `tsvector` |
| **Rules** | Structured field comparison scoring | 80 | Custom Python logic |

### 7.2 Reciprocal Rank Fusion (RRF)

Merges the three ranked lists using:

```
RRF_score(c) = Σ_r  1 / (k + rank_r(c))
```

Where `k = 60` (RRF constant) and `r` iterates over the three retrieval channels.

### 7.3 Cross-Encoder Reranking

The top-30 RRF results are reranked using `cross-encoder/ms-marco-MiniLM-L6-v2`:
- Input: `(JD summary text, candidate profile text)` pairs
- Output: Relevance score per pair
- Top-K candidates (configurable, default 10) proceed to scoring

---

## 8. Outreach Simulation

### 8.1 Dual-Mode Simulation

| Mode | Trigger | Conversation Source |
|------|---------|-------------------|
| **LLM Mode** | `GEMINI_API_KEY` set | Gemini generates 4-turn conversations |
| **Deterministic Mode** | No API key / mock mode | Template-based responses keyed on `reply_style` |

### 8.2 Reply Styles

Each synthetic candidate has a latent `reply_style` that drives conversation tone:

| Style | I_e Score | Behaviour |
|-------|-----------|-----------|
| `enthusiastic` | 0.9 | Actively excited, asks about role details |
| `concise_positive` | 0.75 | Brief, positive responses |
| `detailed_analytical` | 0.7 | Asks probing questions about tech/scale |
| `cautious` | 0.5 | Wants full details before committing |
| `passive` | 0.3 | Not actively looking, low engagement |

### 8.3 Signal Extraction

After each conversation (LLM or deterministic), structured signals are extracted from:
- Candidate profile data (salary, notice, location, career goals)
- Reply style and availability status
- Salary mismatch percentage calculation
- Notice period overshoot calculation

---

## 9. Explainability

### 9.1 Design Principles

- **Evidence-grounded**: Every rationale point cites specific data (skill counts, years, salary figures)
- **No LLM opinions**: Explanations come from scored features, not generative text
- **Auditable**: Feature contribution tables show exact weight × value = contribution

### 9.2 Output Per Candidate

| Section | Content |
|---------|---------|
| **Match Rationale** | Skills matched/missing, experience fit, industry alignment, projects, location |
| **Interest Rationale** | Interest level, salary alignment, work mode, notice period |
| **Risks** | Missing skills, experience gaps, salary budget concerns, notice period risks |
| **Feature Contributions** | Table: Feature, Value, Weight, Contribution, Note |
| **Conversation Log** | Full simulated recruiter-candidate chat |

---

## 10. Calibration

### 10.1 Methods Available

| Method | When Used | Formula |
|--------|-----------|---------|
| **Sigmoid (Platt)** | Default for small datasets | `σ(x) = 1 / (1 + e^(-scale·(x-shift)))` |
| **Linear** | Simple min-max rescaling | `(x - min) / (max - min)` |
| **Isotonic** | When ≥300 labelled pairs exist | scikit-learn `IsotonicRegression` |

### 10.2 Current Parameters

| Score | Scale | Shift |
|-------|-------|-------|
| Match Score | 3.0 | 0.35 |
| Interest Score | 3.5 | 0.35 |
| Cross-encoder normalisation | 2.5 | 0.0 |

---

## 11. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/parse-jd` | Parse raw JD text → structured `JobDescription` |
| `POST` | `/search` | Full pipeline: parse → retrieve → rerank → score → shortlist |

### Search Request Body

```json
{
  "jd_text": "Senior Backend Engineer, Python...",
  "use_db": false,
  "top_k": 10,
  "run_outreach": true
}
```

### Search Response Body

```json
{
  "job_id": "jd_parsed",
  "role_title": "Senior Backend Engineer",
  "generated_at": "2026-04-26T21:00:00",
  "total_candidates_evaluated": 120,
  "total_passed_filters": 85,
  "shortlist": [
    {
      "rank": 1,
      "candidate_id": "cand_001",
      "full_name": "Priya Sharma",
      "match_score": 78.5,
      "interest_score": 72.3,
      "shortlist_rank_score": 76.6,
      "bucket": "Strong Shortlist",
      "match_rationale": ["Matched 5/6 must-have skills..."],
      "interest_rationale": ["Strong explicit interest expressed..."],
      "risks": ["Missing skills: Redis"],
      "feature_contributions": [{"feature": "Must Have Coverage", "value": 0.833, "weight": 0.30, "contribution": 0.25}],
      "conversation_log": [{"role": "recruiter", "message": "Hi Priya!..."}]
    }
  ]
}
```

---

## 12. Dashboard UI

### 12.1 Features

- **JD Input**: Text area with sample JD pre-loaded
- **Settings Sidebar**: DB toggle, shortlist size slider, outreach toggle
- **Metrics Row**: Candidates evaluated, passed filters, shortlisted, strong matches
- **Candidate Expanders**: Profile info, scores, rationale, risks, feature contribution table, simulated conversation
- **Tabs**: Search | Parsed JD (JSON view) | Export (JSON/CSV download)

### 12.2 Design

- Dark theme with gradient header (`#667eea → #764ba2`)
- Inter font family
- Glassmorphism metric cards with hover animations
- Color-coded score badges (green ≥70, yellow ≥50, red <50)
- Chat-style conversation display with role-based styling

---

## 13. Setup & Running

### Prerequisites
- Python 3.11+
- (Optional) Docker Desktop for PostgreSQL + pgvector
- (Optional) Gemini API key for LLM features

### Commands

```bash
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env           # Edit .env if needed

# 4. Generate synthetic data
python scripts/generate_synthetic_data.py

# 5. (Optional) Start database and build index
docker-compose up -d
python scripts/build_index.py

# 6. Start API server
uvicorn app.api.main:app --reload --port 8000

# 7. Start Streamlit dashboard (new terminal)
streamlit run app/ui/app.py
```

---

## 14. Design Decisions

| Decision | Rationale |
|----------|-----------|
| Hybrid retrieval over single-model | Combines recall (dense), precision (sparse), and domain logic (rules) |
| RRF over learned fusion | No training data needed; robust with heterogeneous score distributions |
| Cross-encoder reranking | Higher accuracy than bi-encoder alone for top-K precision |
| Deterministic outreach fallback | Demo reliability without API keys |
| Sigmoid calibration | Appropriate for small synthetic datasets; upgradeable to isotonic |
| Local CPU embeddings | Zero cost, no API dependency, fast iteration |
| JSON-only fallback mode | Works without Docker/PostgreSQL for portable demos |
| Evidence-grounded explanations | Auditable and faithful vs. LLM-generated rationale |

---

## 15. Limitations & Future Work

| Area | Current | Future |
|------|---------|--------|
| Data | 120 synthetic candidates | Real candidate pools, resume parsing |
| Calibration | Sigmoid with hand-tuned params | Isotonic regression with labelled pairs |
| Evaluation | Manual inspection | NDCG@10, MAP, precision/recall metrics |
| Outreach | Simulated conversations | Real email/messaging integration |
| Skills | Exact string matching | Semantic skill taxonomy with embeddings |
| Scale | Single-process | Async workers, batch processing |
| Auth | None | OAuth2 + RBAC for multi-tenant |

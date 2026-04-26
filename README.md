# 🎯 AI-Powered Talent Scouting and Engagement Agent

An intelligent recruiting agent that ingests Job Descriptions, discovers matching candidates from a synthetic pool, simulates recruiter outreach, and returns a recruiter-ready shortlist with **Match Score**, **Interest Score**, and auditable rationale for every ranking decision.

## Architecture

```
JD Input → JD Parser → Hard Filter → Hybrid Retrieval (Dense + Sparse + Rules)
    → RRF Fusion → Cross-Encoder Reranking → Match Scoring
    → Outreach Simulation → Interest Scoring → Final Shortlist + Rationale
```

### Key Components
- **Hybrid Retrieval**: Dense (pgvector ANN), Sparse (full-text), Rules-based scoring
- **Reciprocal Rank Fusion**: Combines multiple retrieval signals
- **Cross-Encoder Reranker**: `ms-marco-MiniLM-L6-v2` for precision reranking
- **Calibrated Scoring**: DPR-defined formulas with sigmoid/Platt calibration
- **Outreach Simulator**: LLM-powered or deterministic conversation simulation
- **Explainability**: Feature contribution tables, not LLM opinions

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database | PostgreSQL 16 + pgvector |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Reranker | cross-encoder/ms-marco-MiniLM-L6-v2 |
| LLM | Google Gemini 2.5 Flash (with fallback mock) |
| Data | 120 synthetic candidates, 10 curated JDs |

## Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop (for PostgreSQL + pgvector)
- (Optional) Gemini API key

### 1. Setup Environment

```bash
# Clone and enter the project
cd clauderesagnt

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your Gemini API key (optional - system works without it)
```

### 3. Start Database (Optional)

```bash
# Start PostgreSQL + pgvector
docker-compose up -d
```

### 4. Generate Data & Build Index

```bash
# Generate 120 synthetic candidates + 10 JDs
python scripts/generate_synthetic_data.py

# (If using DB) Build embeddings and index
python scripts/build_index.py
```

### 5. Run the Application

```bash
# Terminal 1: Start FastAPI backend
uvicorn app.api.main:app --reload --port 8000

# Terminal 2: Start Streamlit UI
streamlit run app/ui/app.py
```

### 6. Demo

1. Open the Streamlit UI (usually http://localhost:8501)
2. Paste a JD or use the sample
3. Toggle **"Use Database"** off if not using PostgreSQL
4. Click **"Find Candidates"**
5. Explore shortlist, rationales, feature contributions, and simulated conversations

### Sample JD for Demo
```
Senior Backend Engineer, Bengaluru hybrid, Python/FastAPI/PostgreSQL/Redis,
4–8 years, fintech preferred, salary 18–28 LPA, notice ≤ 60 days.
```

## Scoring Formulas

### Match Score
```
S_f = 0.30*M_h + 0.08*N_h + 0.10*T + 0.12*E + 0.10*D + 0.12*P + 0.08*L + 0.10*C
M_raw = 0.38*S_f + 0.30*X + 0.17*V + 0.15*K
MatchScore = 100 * Calibrate(G * Q * M_raw)
```

### Interest Score
```
I_raw = 0.35*I_e + 0.18*R_a + 0.12*W_a + 0.15*S_a + 0.10*N_p + 0.06*G_q + 0.04*F_t
InterestScore = 100 * Calibrate(I_raw) [with caps for decline/salary/notice]
```

### Shortlist Ranking
```
ShortlistRankScore = 0.70 * MatchScore + 0.30 * InterestScore
```

## Project Structure

```
clauderesagnt/
├── app/
│   ├── ui/app.py                  # Streamlit dashboard
│   ├── api/main.py                # FastAPI backend
│   ├── core/
│   │   ├── schemas.py             # Pydantic models
│   │   ├── jd_parser.py           # JD parsing
│   │   ├── retrieval.py           # Hybrid retrieval + RRF
│   │   ├── reranker.py            # Cross-encoder reranking
│   │   ├── match_scoring.py       # Match score formula
│   │   ├── interest_scoring.py    # Interest score formula
│   │   ├── outreach_simulator.py  # Engagement simulation
│   │   ├── explainability.py      # Rationale generation
│   │   └── calibration.py         # Score calibration
│   ├── db/models.py               # SQLAlchemy + pgvector
│   └── services/
│       ├── llm_client.py          # LLM abstraction
│       └── embeddings.py          # Embedding service
├── data/                          # Generated synthetic data
├── scripts/                       # Data generation & indexing
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## License

This project is built for the Catalyst hackathon. Synthetic data only — no real personal data.

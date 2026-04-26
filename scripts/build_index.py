"""
Build the pgvector index: load synthetic candidates, compute embeddings, insert into DB.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.models import DBCandidate, get_engine, init_db, Base
from app.services.embeddings import encode_texts
from sqlalchemy.orm import sessionmaker


def main():
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synthetic_candidates.json")
    if not os.path.exists(data_path):
        print("ERROR: synthetic_candidates.json not found. Run generate_synthetic_data.py first.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    print(f"Loaded {len(candidates)} candidates.")

    # Initialise DB
    try:
        init_db()
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        # Test connection
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        print(f"\nERROR: Could not connect to PostgreSQL database.")
        print(f"Details: {e}")
        print(f"\nTo fix this, either:")
        print(f"  1. Run 'docker-compose up -d' to start the pgvector container")
        print(f"  2. Or update DATABASE_URL in .env with your Postgres credentials")
        print(f"\nAlternatively, skip this step entirely and use JSON-only mode:")
        print(f"  - In the Streamlit UI, toggle OFF 'Use Database (pgvector)'")
        print(f"  - The system will retrieve candidates directly from the JSON file")
        return

    # Clear existing data
    session.query(DBCandidate).delete()
    session.commit()

    # Compute embeddings in batch
    profile_texts = [c["profile_text"] for c in candidates]
    print("Computing embeddings...")
    embeddings = encode_texts(profile_texts)
    print(f"Computed {len(embeddings)} embeddings.")

    # Insert into DB
    for cand, emb in zip(candidates, embeddings):
        db_cand = DBCandidate(
            candidate_id=cand["candidate_id"],
            full_name=cand["full_name"],
            location=cand.get("location", ""),
            current_title=cand.get("current_title", ""),
            years_experience=cand.get("years_experience", 0),
            work_mode=cand.get("work_preferences", {}).get("work_mode", "hybrid"),
            notice_period_days=cand.get("availability", {}).get("notice_period_days", 30),
            expected_lpa=cand.get("compensation", {}).get("expected_lpa", 0),
            actively_looking=cand.get("availability", {}).get("actively_looking", True),
            profile_json=cand,
            profile_text=cand["profile_text"],
            embedding=emb,
        )
        session.add(db_cand)

    session.commit()
    print(f"Inserted {len(candidates)} candidates into database.")

    # Create HNSW index for fast ANN search
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("DROP INDEX IF EXISTS idx_candidate_embedding"))
        conn.execute(text(
            "CREATE INDEX idx_candidate_embedding ON candidates "
            "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
        ))
        conn.commit()
    print("HNSW index created on embedding column.")
    session.close()


if __name__ == "__main__":
    main()

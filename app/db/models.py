"""
SQLAlchemy models for the talent scout database with pgvector support.
"""
from sqlalchemy import Column, String, Integer, Float, JSON, Boolean, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension

Base = declarative_base()


class DBCandidate(Base):
    """Candidate row with profile JSON and dense embedding vector."""
    __tablename__ = "candidates"

    candidate_id = Column(String, primary_key=True)
    full_name = Column(String, nullable=False)
    location = Column(String, index=True)
    current_title = Column(String)
    years_experience = Column(Float)
    work_mode = Column(String, index=True)
    notice_period_days = Column(Integer)
    expected_lpa = Column(Float)
    actively_looking = Column(Boolean, default=True)
    profile_json = Column(JSON, nullable=False)
    profile_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))


def get_engine():
    url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/talent_scout")
    return create_engine(url, echo=False)


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Create all tables. Call once during setup."""
    engine = get_engine()
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(
            __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
        )
        conn.commit()
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")

"""
Generate 120 synthetic candidate profiles across 6 role families + 10 curated JDs.
Uses O*NET/ESCO-seeded skill taxonomies and Faker for names/contacts only.
"""
import json
import random
import uuid
import os
import sys
from faker import Faker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.schemas import CandidateProfile, CandidateSkill, Education, Project, WorkPreferences, Compensation, Availability, InterestProfile

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# ── O*NET / ESCO-seeded skill taxonomies per role family ──

ROLE_FAMILIES = {
    "backend": {
        "titles": ["Backend Engineer", "Software Engineer", "Backend Developer", "Server-Side Engineer", "API Developer", "Platform Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t} / Tech Lead"},
        "must_skills": ["Python", "Java", "Go", "Node.js", "PostgreSQL", "MySQL", "Redis", "REST APIs", "GraphQL", "Docker"],
        "opt_skills": ["Kafka", "RabbitMQ", "Kubernetes", "Terraform", "AWS", "GCP", "CI/CD", "Microservices", "gRPC", "Elasticsearch"],
        "industries": ["fintech", "saas", "ecommerce", "healthtech", "edtech", "logistics"],
        "projects": [
            ("Payment Gateway API", "Built high-throughput payment processing microservices", "Processed 50K+ transactions/day"),
            ("User Auth Service", "Designed OAuth2/JWT authentication service", "Reduced auth latency by 40%"),
            ("Data Pipeline", "Built ETL pipelines for real-time analytics", "Enabled sub-second dashboards"),
            ("Inventory System", "Microservices for real-time inventory management", "Cut stockout rate by 25%"),
        ]
    },
    "frontend": {
        "titles": ["Frontend Engineer", "UI Developer", "Frontend Developer", "Web Developer", "UI/UX Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t}"},
        "must_skills": ["React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Next.js", "Redux", "Webpack", "Figma", "REST APIs"],
        "opt_skills": ["Vue.js", "Angular", "Svelte", "Tailwind CSS", "GraphQL", "Storybook", "Jest", "Cypress", "Accessibility", "PWA"],
        "industries": ["saas", "ecommerce", "media", "edtech", "fintech", "social"],
        "projects": [
            ("Design System", "Built component library with Storybook", "Adopted by 5 product teams"),
            ("Dashboard App", "Real-time analytics dashboard with React", "Served 10K daily users"),
            ("E-commerce Storefront", "Next.js SSR storefront with Stripe", "Improved conversion by 18%"),
        ]
    },
    "fullstack": {
        "titles": ["Full-Stack Engineer", "Software Engineer", "Full-Stack Developer", "Product Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t}"},
        "must_skills": ["Python", "React", "TypeScript", "PostgreSQL", "Node.js", "Docker", "REST APIs", "Git", "FastAPI", "JavaScript"],
        "opt_skills": ["AWS", "Redis", "MongoDB", "GraphQL", "Kubernetes", "Terraform", "CI/CD", "Next.js", "Tailwind CSS", "Celery"],
        "industries": ["saas", "fintech", "ecommerce", "healthtech", "edtech", "social"],
        "projects": [
            ("SaaS Platform", "End-to-end SaaS product with React + FastAPI", "Onboarded 200+ enterprise clients"),
            ("Marketplace App", "Two-sided marketplace with payment integration", "GMV of 5Cr in first year"),
        ]
    },
    "data": {
        "titles": ["Data Engineer", "Analytics Engineer", "ETL Developer", "Data Platform Engineer", "BI Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t}"},
        "must_skills": ["Python", "SQL", "Apache Spark", "Airflow", "PostgreSQL", "AWS", "dbt", "Snowflake", "Kafka", "ETL"],
        "opt_skills": ["BigQuery", "Redshift", "Databricks", "Flink", "Hive", "Presto", "Terraform", "Docker", "Looker", "Pandas"],
        "industries": ["fintech", "ecommerce", "adtech", "logistics", "healthtech", "telecom"],
        "projects": [
            ("Data Lake", "Built company-wide data lake on S3 + Spark", "Unified 12 data sources"),
            ("Real-time Pipeline", "Kafka + Flink streaming pipeline", "Sub-minute data freshness"),
        ]
    },
    "ml": {
        "titles": ["ML Engineer", "Machine Learning Engineer", "AI Engineer", "Applied Scientist", "NLP Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t} / ML Architect"},
        "must_skills": ["Python", "PyTorch", "TensorFlow", "scikit-learn", "SQL", "NumPy", "Pandas", "Docker", "MLflow", "NLP"],
        "opt_skills": ["Hugging Face", "LangChain", "Ray", "Kubernetes", "AWS SageMaker", "Computer Vision", "Reinforcement Learning", "LLMs", "Feature Stores", "A/B Testing"],
        "industries": ["fintech", "healthtech", "adtech", "ecommerce", "autonomous", "saas"],
        "projects": [
            ("Fraud Detection", "Built real-time fraud scoring model", "Reduced fraud by 35%"),
            ("Recommendation Engine", "Collaborative filtering + content-based", "Increased engagement by 22%"),
            ("NLP Classifier", "Text classification for support tickets", "Automated 60% of ticket routing"),
        ]
    },
    "devops": {
        "titles": ["DevOps Engineer", "SRE", "Platform Engineer", "Infrastructure Engineer", "Cloud Engineer"],
        "seniority_titles": {"junior": "Junior {t}", "mid": "{t}", "senior": "Senior {t}", "lead": "Lead {t} / Staff {t}"},
        "must_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux", "CI/CD", "Python", "Bash", "Prometheus", "Grafana"],
        "opt_skills": ["GCP", "Azure", "Ansible", "Helm", "ArgoCD", "Jenkins", "Datadog", "ELK Stack", "Istio", "Vault"],
        "industries": ["saas", "fintech", "ecommerce", "media", "telecom", "gaming"],
        "projects": [
            ("K8s Migration", "Migrated monolith to Kubernetes", "99.95% uptime achieved"),
            ("CI/CD Pipeline", "Built GitOps pipeline with ArgoCD", "Deploy time reduced from 2h to 15min"),
        ]
    }
}

LOCATIONS = ["Bengaluru", "Mumbai", "Hyderabad", "Pune", "Chennai", "Delhi NCR", "Noida", "Gurgaon", "Remote India"]
WORK_MODES = ["remote", "hybrid", "onsite"]
DEGREES = ["B.Tech", "M.Tech", "B.Sc CS", "MCA", "B.E.", "M.S."]
REPLY_STYLES = ["concise_positive", "enthusiastic", "cautious", "detailed_analytical", "passive"]

SENIORITY_BANDS = {
    "junior": (0.5, 2.5, 4, 12),
    "mid": (2.5, 5.0, 10, 22),
    "senior": (5.0, 9.0, 18, 35),
    "lead": (8.0, 15.0, 28, 55),
}


def generate_candidate(idx: int, role_family: str, seniority: str) -> dict:
    """Generate a single synthetic candidate profile."""
    rf = ROLE_FAMILIES[role_family]
    band = SENIORITY_BANDS[seniority]
    yoe = round(random.uniform(band[0], band[1]), 1)
    salary_current = round(random.uniform(band[2], band[3]), 1)
    salary_expected = round(salary_current * random.uniform(1.05, 1.35), 1)

    base_title = random.choice(rf["titles"])
    title_template = rf["seniority_titles"][seniority]
    current_title = title_template.replace("{t}", base_title)

    num_must = random.randint(3, min(6, len(rf["must_skills"])))
    num_opt = random.randint(1, min(4, len(rf["opt_skills"])))
    chosen_must = random.sample(rf["must_skills"], num_must)
    chosen_opt = random.sample(rf["opt_skills"], num_opt)
    all_skills = chosen_must + chosen_opt

    skills = []
    for s in all_skills:
        level = random.randint(2, 5) if s in chosen_must else random.randint(1, 4)
        skill_years = min(round(random.uniform(0.5, yoe), 1), yoe)
        skills.append(CandidateSkill(name=s, level=level, years=skill_years, last_used_months_ago=random.choice([0, 0, 0, 1, 3, 6, 12])))

    location = random.choice(LOCATIONS)
    work_mode = random.choice(WORK_MODES)
    notice = random.choice([0, 15, 30, 30, 30, 45, 60, 60, 90])
    actively_looking = random.random() > 0.3

    proj_templates = rf["projects"]
    num_projects = random.randint(1, min(3, len(proj_templates)))
    projects = [Project(name=p[0], summary=p[1], impact=p[2]) for p in random.sample(proj_templates, num_projects)]

    title_history = [base_title]
    if seniority in ("senior", "lead"):
        title_history = [random.choice(rf["titles"]), current_title]

    name = fake.name()
    candidate = CandidateProfile(
        candidate_id=f"cand_{idx:03d}",
        full_name=name,
        headline=f"{current_title} | {' · '.join(chosen_must[:3])}",
        location=location,
        timezone="Asia/Kolkata",
        current_title=current_title,
        years_experience=yoe,
        skills=skills,
        title_history=title_history,
        industries=random.sample(rf["industries"], min(2, len(rf["industries"]))),
        education=[Education(degree=random.choice(DEGREES), field="Computer Science")],
        certifications=random.sample(["AWS Certified", "CKA", "GCP Professional", "Azure Fundamentals", ""], k=1),
        projects=projects,
        work_preferences=WorkPreferences(
            work_mode=work_mode,
            open_to_relocation=random.random() > 0.6,
            preferred_locations=[location] + (["Remote India"] if work_mode == "remote" else [])
        ),
        compensation=Compensation(current_lpa=salary_current, expected_lpa=salary_expected),
        availability=Availability(notice_period_days=notice, actively_looking=actively_looking),
        interest_profile=InterestProfile(
            career_goals=random.sample(["backend scale", "frontend craft", "ml research", "leadership", "fintech products", "startup", "big tech", "remote work"], 2),
            salary_sensitivity=round(random.uniform(0.3, 0.9), 2),
            reply_style=random.choice(REPLY_STYLES)
        ),
        profile_text=_build_profile_text(name, current_title, yoe, all_skills, projects, location, rf["industries"]),
        latent_match_truth={},
        latent_interest_truth={}
    )
    return candidate.model_dump()


def _build_profile_text(name, title, yoe, skills, projects, location, industries):
    skill_str = ", ".join(skills[:6])
    proj_str = "; ".join([p.name for p in projects])
    return (
        f"{name} is a {title} based in {location} with {yoe} years of experience. "
        f"Core skills include {skill_str}. "
        f"Industry experience spans {', '.join(industries[:2])}. "
        f"Key projects: {proj_str}."
    )


def generate_jds() -> list:
    """Generate 10 curated JDs with hidden relevance mappings."""
    jds = [
        {
            "job_id": "jd_001", "role_title": "Senior Backend Engineer", "department": "Engineering",
            "seniority": "senior", "employment_type": "full_time", "work_mode": "hybrid",
            "locations": ["Bengaluru"], "must_have_skills": [{"name": "Python", "weight": 1.0}, {"name": "FastAPI", "weight": 0.9}, {"name": "PostgreSQL", "weight": 0.8}, {"name": "Redis", "weight": 0.7}],
            "nice_to_have_skills": [{"name": "Docker", "weight": 0.5}, {"name": "Kafka", "weight": 0.5}],
            "min_years_experience": 4, "max_years_experience": 8, "industries": ["fintech", "saas"],
            "education_preferences": ["B.Tech", "M.Tech"], "salary_range_lpa": {"min": 18, "max": 28},
            "notice_period_days_max": 60, "keywords": ["microservices", "backend systems", "apis"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": True}
        },
        {
            "job_id": "jd_002", "role_title": "Frontend Engineer", "department": "Product",
            "seniority": "mid", "employment_type": "full_time", "work_mode": "remote",
            "locations": ["Remote India"], "must_have_skills": [{"name": "React", "weight": 1.0}, {"name": "TypeScript", "weight": 0.9}, {"name": "CSS3", "weight": 0.7}],
            "nice_to_have_skills": [{"name": "Next.js", "weight": 0.6}, {"name": "GraphQL", "weight": 0.4}],
            "min_years_experience": 2, "max_years_experience": 5, "industries": ["saas", "ecommerce"],
            "education_preferences": ["B.Tech", "B.Sc CS"], "salary_range_lpa": {"min": 10, "max": 20},
            "notice_period_days_max": 30, "keywords": ["react", "ui", "frontend"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": False}
        },
        {
            "job_id": "jd_003", "role_title": "ML Engineer", "department": "AI/ML",
            "seniority": "senior", "employment_type": "full_time", "work_mode": "hybrid",
            "locations": ["Bengaluru", "Hyderabad"], "must_have_skills": [{"name": "Python", "weight": 1.0}, {"name": "PyTorch", "weight": 0.9}, {"name": "scikit-learn", "weight": 0.7}, {"name": "SQL", "weight": 0.6}],
            "nice_to_have_skills": [{"name": "Hugging Face", "weight": 0.5}, {"name": "MLflow", "weight": 0.4}],
            "min_years_experience": 4, "max_years_experience": 10, "industries": ["fintech", "healthtech"],
            "education_preferences": ["M.Tech", "M.S."], "salary_range_lpa": {"min": 22, "max": 40},
            "notice_period_days_max": 60, "keywords": ["machine learning", "deep learning", "nlp"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": True}
        },
        {
            "job_id": "jd_004", "role_title": "DevOps Engineer", "department": "Infrastructure",
            "seniority": "mid", "employment_type": "full_time", "work_mode": "onsite",
            "locations": ["Mumbai", "Pune"], "must_have_skills": [{"name": "AWS", "weight": 1.0}, {"name": "Docker", "weight": 0.9}, {"name": "Kubernetes", "weight": 0.9}, {"name": "Terraform", "weight": 0.8}],
            "nice_to_have_skills": [{"name": "Ansible", "weight": 0.4}, {"name": "Prometheus", "weight": 0.5}],
            "min_years_experience": 3, "max_years_experience": 7, "industries": ["saas", "fintech"],
            "education_preferences": ["B.Tech", "B.E."], "salary_range_lpa": {"min": 14, "max": 25},
            "notice_period_days_max": 45, "keywords": ["devops", "cloud", "infrastructure"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": False}
        },
        {
            "job_id": "jd_005", "role_title": "Full-Stack Engineer", "department": "Engineering",
            "seniority": "senior", "employment_type": "full_time", "work_mode": "hybrid",
            "locations": ["Bengaluru", "Pune"], "must_have_skills": [{"name": "React", "weight": 1.0}, {"name": "Python", "weight": 1.0}, {"name": "PostgreSQL", "weight": 0.8}, {"name": "Docker", "weight": 0.7}],
            "nice_to_have_skills": [{"name": "AWS", "weight": 0.5}, {"name": "Redis", "weight": 0.5}],
            "min_years_experience": 5, "max_years_experience": 10, "industries": ["saas", "edtech"],
            "education_preferences": ["B.Tech", "M.Tech"], "salary_range_lpa": {"min": 20, "max": 35},
            "notice_period_days_max": 60, "keywords": ["full-stack", "react", "python", "product engineering"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": True}
        },
        {
            "job_id": "jd_006", "role_title": "Data Engineer", "department": "Data",
            "seniority": "mid", "employment_type": "full_time", "work_mode": "remote",
            "locations": ["Remote India"], "must_have_skills": [{"name": "Python", "weight": 1.0}, {"name": "Apache Spark", "weight": 0.9}, {"name": "SQL", "weight": 0.8}, {"name": "Airflow", "weight": 0.7}],
            "nice_to_have_skills": [{"name": "Kafka", "weight": 0.5}, {"name": "dbt", "weight": 0.4}],
            "min_years_experience": 3, "max_years_experience": 6, "industries": ["ecommerce", "adtech"],
            "education_preferences": ["B.Tech", "M.Tech"], "salary_range_lpa": {"min": 14, "max": 24},
            "notice_period_days_max": 30, "keywords": ["data engineering", "etl", "spark"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": False}
        },
        {
            "job_id": "jd_007", "role_title": "Junior Backend Developer", "department": "Engineering",
            "seniority": "junior", "employment_type": "full_time", "work_mode": "onsite",
            "locations": ["Chennai"], "must_have_skills": [{"name": "Python", "weight": 1.0}, {"name": "REST APIs", "weight": 0.8}, {"name": "Git", "weight": 0.6}],
            "nice_to_have_skills": [{"name": "Docker", "weight": 0.4}, {"name": "PostgreSQL", "weight": 0.5}],
            "min_years_experience": 0, "max_years_experience": 2, "industries": ["saas", "edtech"],
            "education_preferences": ["B.Tech", "B.Sc CS", "MCA"], "salary_range_lpa": {"min": 4, "max": 10},
            "notice_period_days_max": 30, "keywords": ["python", "backend", "junior"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": False}
        },
        {
            "job_id": "jd_008", "role_title": "Lead Platform Engineer", "department": "Platform",
            "seniority": "lead", "employment_type": "full_time", "work_mode": "hybrid",
            "locations": ["Bengaluru", "Hyderabad"], "must_have_skills": [{"name": "Kubernetes", "weight": 1.0}, {"name": "AWS", "weight": 1.0}, {"name": "Terraform", "weight": 0.9}, {"name": "Python", "weight": 0.7}],
            "nice_to_have_skills": [{"name": "Istio", "weight": 0.5}, {"name": "ArgoCD", "weight": 0.5}],
            "min_years_experience": 8, "max_years_experience": 15, "industries": ["fintech", "saas"],
            "education_preferences": ["B.Tech", "M.Tech"], "salary_range_lpa": {"min": 35, "max": 55},
            "notice_period_days_max": 90, "keywords": ["platform", "infrastructure", "leadership"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": True}
        },
        {
            "job_id": "jd_009", "role_title": "Senior Frontend Engineer", "department": "Product",
            "seniority": "senior", "employment_type": "full_time", "work_mode": "hybrid",
            "locations": ["Bengaluru", "Mumbai"], "must_have_skills": [{"name": "React", "weight": 1.0}, {"name": "TypeScript", "weight": 1.0}, {"name": "Next.js", "weight": 0.8}],
            "nice_to_have_skills": [{"name": "Figma", "weight": 0.5}, {"name": "Storybook", "weight": 0.4}],
            "min_years_experience": 5, "max_years_experience": 9, "industries": ["saas", "media"],
            "education_preferences": ["B.Tech", "B.Sc CS"], "salary_range_lpa": {"min": 20, "max": 32},
            "notice_period_days_max": 60, "keywords": ["react", "frontend", "design system"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": True}
        },
        {
            "job_id": "jd_010", "role_title": "AI/NLP Engineer", "department": "AI/ML",
            "seniority": "mid", "employment_type": "full_time", "work_mode": "remote",
            "locations": ["Remote India"], "must_have_skills": [{"name": "Python", "weight": 1.0}, {"name": "NLP", "weight": 1.0}, {"name": "Hugging Face", "weight": 0.8}, {"name": "PyTorch", "weight": 0.8}],
            "nice_to_have_skills": [{"name": "LangChain", "weight": 0.6}, {"name": "LLMs", "weight": 0.5}],
            "min_years_experience": 2, "max_years_experience": 6, "industries": ["healthtech", "saas"],
            "education_preferences": ["M.Tech", "M.S."], "salary_range_lpa": {"min": 16, "max": 30},
            "notice_period_days_max": 45, "keywords": ["nlp", "llm", "transformers", "ai"],
            "hard_constraints": {"work_authorisation_required": False, "must_accept_hybrid": False}
        },
    ]
    return jds


def assign_latent_truth(candidates: list, jds: list) -> list:
    """Assign hidden match/interest truth labels for each JD-candidate pair."""
    for cand in candidates:
        cand_skills = {s["name"].lower() for s in cand["skills"]}
        cand_loc = cand["location"].lower()
        for jd in jds:
            jd_id = jd["job_id"]
            jd_must = {s["name"].lower() for s in jd["must_have_skills"]}
            jd_nice = {s["name"].lower() for s in jd.get("nice_to_have_skills", [])}
            jd_locs = {l.lower() for l in jd["locations"]}

            must_overlap = len(cand_skills & jd_must) / max(len(jd_must), 1)
            nice_overlap = len(cand_skills & jd_nice) / max(len(jd_nice), 1)
            loc_match = 1.0 if cand_loc in jd_locs or "remote india" in jd_locs else 0.3
            exp_fit = 1.0 if jd["min_years_experience"] <= cand["years_experience"] <= jd["max_years_experience"] else 0.4
            salary_ok = 1.0
            if jd.get("salary_range_lpa"):
                if cand["compensation"]["expected_lpa"] > jd["salary_range_lpa"]["max"] * 1.15:
                    salary_ok = 0.3

            match_truth = round(0.45 * must_overlap + 0.10 * nice_overlap + 0.15 * loc_match + 0.15 * exp_fit + 0.15 * salary_ok, 3)
            interest_truth = round(random.uniform(0.3, 0.95) if match_truth > 0.5 else random.uniform(0.1, 0.5), 3)

            cand["latent_match_truth"][jd_id] = match_truth
            cand["latent_interest_truth"][jd_id] = interest_truth
    return candidates


def main():
    families = list(ROLE_FAMILIES.keys())
    candidates_per_family = 20
    candidates = []
    idx = 1

    seniority_dist = ["junior"] * 3 + ["mid"] * 8 + ["senior"] * 6 + ["lead"] * 3

    for family in families:
        for i in range(candidates_per_family):
            seniority = random.choice(seniority_dist)
            cand = generate_candidate(idx, family, seniority)
            idx += 1
            candidates.append(cand)

    jds = generate_jds()
    candidates = assign_latent_truth(candidates, jds)

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "synthetic_candidates.json"), "w", encoding="utf-8") as f:
        json.dump(candidates, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(candidates)} candidates -> data/synthetic_candidates.json")

    with open(os.path.join(data_dir, "synthetic_jds.json"), "w", encoding="utf-8") as f:
        json.dump(jds, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(jds)} JDs -> data/synthetic_jds.json")


if __name__ == "__main__":
    main()

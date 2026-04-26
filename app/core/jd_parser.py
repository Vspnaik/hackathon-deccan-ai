"""
JD Parser: converts raw JD text into a strict JobDescription schema using LLM structured extraction.
Falls back to keyword-based parsing when LLM is unavailable.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_client import extract_structured, generate_text, _USE_MOCK
from app.core.schemas import JobDescription, SkillWeight, SalaryRange, HardConstraints


PARSE_SYSTEM_PROMPT = """You are a precise job description parser. Extract structured information from the provided job description text.
Return ONLY the structured data matching the requested schema. Be thorough: extract all skills, requirements, and constraints mentioned."""


def parse_jd(jd_text: str) -> JobDescription:
    """
    Parse raw JD text into a structured JobDescription.
    Uses LLM structured extraction with retry, falling back to keyword extraction.
    """
    if _USE_MOCK:
        return _keyword_parse(jd_text)

    prompt = f"""Parse the following job description into the structured schema.
Extract: role_title, seniority, work_mode, locations, must_have_skills (with weights 0.6-1.0),
nice_to_have_skills (with weights 0.3-0.6), min/max years experience, industries,
education_preferences, salary range, notice period, keywords, and hard constraints.

Job Description:
{jd_text}"""

    try:
        result = extract_structured(prompt, JobDescription, system_prompt=PARSE_SYSTEM_PROMPT)
        if isinstance(result, dict):
            jd = JobDescription(**result)
        else:
            jd = result
        # Validate minimum fields
        if not jd.role_title:
            raise ValueError("role_title is empty after LLM extraction")
        return jd
    except Exception as e:
        print(f"[JD Parser] LLM extraction failed: {e}. Falling back to keyword parse.")
        return _keyword_parse(jd_text)


def _keyword_parse(jd_text: str) -> JobDescription:
    """
    Fallback keyword-based JD parser for when LLM is unavailable.
    Extracts key information using pattern matching.
    """
    text_lower = jd_text.lower()

    # Extract role title (first significant phrase)
    role_title = "Software Engineer"
    title_patterns = [
        r"(senior|junior|lead|staff|principal)?\s*(backend|frontend|full[-\s]?stack|data|ml|devops|platform|cloud|sre|ai|nlp)\s*(engineer|developer|architect)",
    ]
    for pat in title_patterns:
        m = re.search(pat, text_lower)
        if m:
            role_title = m.group(0).strip().title()
            break

    # Extract seniority
    seniority = "mid"
    if "senior" in text_lower:
        seniority = "senior"
    elif "junior" in text_lower:
        seniority = "junior"
    elif "lead" in text_lower or "staff" in text_lower:
        seniority = "lead"

    # Extract work mode
    work_mode = "hybrid"
    if "remote" in text_lower:
        work_mode = "remote"
    elif "onsite" in text_lower or "on-site" in text_lower or "office" in text_lower:
        work_mode = "onsite"

    # Extract locations
    locations = []
    city_list = ["bengaluru", "bangalore", "mumbai", "hyderabad", "pune", "chennai", "delhi", "noida", "gurgaon", "remote"]
    for city in city_list:
        if city in text_lower:
            locations.append(city.title() if city != "remote" else "Remote India")
    if not locations:
        locations = ["Remote India"]

    # Extract skills
    tech_skills = [
        "python", "java", "go", "node.js", "react", "typescript", "javascript", "fastapi",
        "postgresql", "mysql", "redis", "docker", "kubernetes", "terraform", "aws", "gcp",
        "kafka", "spark", "airflow", "pytorch", "tensorflow", "scikit-learn", "sql",
        "graphql", "rest apis", "css3", "html5", "next.js", "mongodb", "elasticsearch",
        "git", "ci/cd", "mlflow", "hugging face", "nlp", "llms", "pandas", "numpy",
        "celery", "rabbitmq", "prometheus", "grafana", "linux", "bash",
    ]
    found_skills = [s for s in tech_skills if s in text_lower]
    must_have = [SkillWeight(name=s.title() if len(s) > 3 else s.upper(), weight=round(1.0 - i * 0.05, 2))
                 for i, s in enumerate(found_skills[:6])]
    nice_to_have = [SkillWeight(name=s.title() if len(s) > 3 else s.upper(), weight=0.5)
                    for s in found_skills[6:10]]

    # Extract experience
    min_exp, max_exp = 0, 20
    exp_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*(?:years|yrs|yr)", text_lower)
    if exp_match:
        min_exp = int(exp_match.group(1))
        max_exp = int(exp_match.group(2))

    # Extract salary
    salary = None
    sal_match = re.search(r"(\d+)\s*[-–to]+\s*(\d+)\s*(?:lpa|lakhs|l)", text_lower)
    if sal_match:
        salary = SalaryRange(min=float(sal_match.group(1)), max=float(sal_match.group(2)))

    # Extract notice period
    notice_max = 60
    notice_match = re.search(r"notice\s*(?:period)?[:\s]*(?:≤|<=|max|upto|up to)?\s*(\d+)\s*(?:days|d)", text_lower)
    if notice_match:
        notice_max = int(notice_match.group(1))

    # Extract industries
    industries = []
    ind_list = ["fintech", "saas", "ecommerce", "healthtech", "edtech", "logistics", "media", "adtech"]
    for ind in ind_list:
        if ind in text_lower:
            industries.append(ind)

    return JobDescription(
        job_id="jd_parsed",
        role_title=role_title,
        seniority=seniority,
        work_mode=work_mode,
        locations=locations,
        must_have_skills=must_have,
        nice_to_have_skills=nice_to_have,
        min_years_experience=min_exp,
        max_years_experience=max_exp,
        industries=industries if industries else ["saas"],
        salary_range_lpa=salary,
        notice_period_days_max=notice_max,
        keywords=found_skills[:5],
        hard_constraints=HardConstraints(
            must_accept_hybrid=(work_mode == "hybrid"),
        ),
    )

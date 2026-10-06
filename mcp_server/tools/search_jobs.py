"""
MCP Tool: search_jobs
Searches the local mock jobs repository (data/jobs.json) containing 20+ realistic listings.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
JOBS_FILE = BASE_DIR / "data" / "jobs.json"


def load_jobs() -> List[Dict[str, Any]]:
    if not JOBS_FILE.exists():
        # Fallback to empty list if not found
        return []
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def search_jobs(
    role: str = "",
    location: str = "",
    keywords: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search mock job openings matching given role keywords, location, and optional keywords.

    Args:
        role: Title or role keyword (e.g. 'Data Analyst', 'Software Developer', 'AI')
        location: City or region (e.g. 'Chennai', 'Bengaluru', 'Remote')
        keywords: Additional search keywords (e.g. 'Python', 'SQL', 'FastAPI')

    Returns:
        List of matching job listings.
    """
    all_jobs = load_jobs()
    if not all_jobs:
        return []

    role_term = (role or "").strip().lower()
    loc_term = (location or "").strip().lower()
    kw_term = (keywords or "").strip().lower()

    # Search tokens
    search_tokens = [t for t in [role_term, kw_term] if t]

    results = []
    for job in all_jobs:
        job_role = job.get("role", "").lower()
        job_desc = job.get("description", "").lower()
        job_loc = job.get("location", "").lower()
        job_company = job.get("company", "").lower()
        req_skills = [s.lower() for s in job.get("required_skills", [])]
        pref_skills = [s.lower() for s in job.get("preferred_skills", [])]

        # Location check
        if loc_term and loc_term not in job_loc:
            continue

        # Role & keyword check
        if not search_tokens:
            results.append(job)
            continue

        matches_role = any(
            t in job_role
            or t in job_desc
            or t in job_company
            or any(t in s for s in req_skills)
            or any(t in s for s in pref_skills)
            for t in search_tokens
        )

        if matches_role:
            results.append(job)

    # If no strict match found, return top 3 available jobs as suggestions
    if not results and all_jobs:
        return all_jobs[:3]

    return results


if __name__ == "__main__":
    test_res = search_jobs("Data Analyst", "Chennai")
    print(f"Found {len(test_res)} jobs for 'Data Analyst' in Chennai.")

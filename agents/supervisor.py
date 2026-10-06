"""
Supervisor Agent:
Evaluates user query, extracts candidate/role/company metadata,
seeds RAG pipeline, and coordinates multi-agent conditional routing.
"""

import re
from typing import Dict, Any
from graph.state import JobCopilotState
from rag.pipeline import rag_pipeline
from tools.resume_tools import extract_skills_from_text


def supervisor_node(state: JobCopilotState) -> Dict[str, Any]:
    """
    Evaluates user intent and initializes shared context for all downstream agents.
    """
    query = state.get("user_query") or state.get("query", "")
    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")

    # Ensure RAG knowledge base is ingested for the current session
    rag_pipeline.ingest_documents(resume_text=resume_text, job_description=job_description)

    # 1. Extract Candidate Name
    candidate_name = state.get("candidate_name", "")
    if not candidate_name or candidate_name == "Candidate":
        first_lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
        if first_lines:
            candidate_name = first_lines[0].title()
        else:
            candidate_name = "Candidate"

    # 2. Extract Target Company
    company_name = state.get("target_company") or state.get("company_name", "")
    if not company_name or company_name == "Target Company":
        comp_match = re.search(r"(?:Company|At|For)\s*:\s*([A-Za-z0-9\s]+)", job_description, re.IGNORECASE)
        if comp_match:
            company_name = comp_match.group(1).split("\n")[0].strip()
        elif "zoho" in (query + job_description).lower():
            company_name = "Zoho Corporation"
        elif "tcs" in (query + job_description).lower():
            company_name = "Tata Consultancy Services (TCS)"
        elif "freshworks" in (query + job_description).lower():
            company_name = "Freshworks"
        else:
            company_name = "Target Company"

    # 3. Extract Target Role
    target_role = state.get("target_role", "")
    if not target_role or target_role == "Target Role":
        role_match = re.search(r"(?:Role|Title|Position)\s*:\s*([A-Za-z0-9\s]+)", job_description, re.IGNORECASE)
        if role_match:
            target_role = role_match.group(1).split("\n")[0].strip()
        elif "data analyst" in (query + job_description).lower():
            target_role = "Junior Data Analyst"
        elif "ai engineer" in (query + job_description).lower() or "ml engineer" in (query + job_description).lower():
            target_role = "Associate AI / ML Engineer"
        elif "software developer" in (query + job_description).lower():
            target_role = "Software Developer"
        else:
            target_role = "Target Position"

    # Extract initial skills
    resume_skills = extract_skills_from_text(resume_text)

    # 4. Intent Classification and Conditional Routing
    q_lower = query.lower()
    if any(k in q_lower for k in ["interview only", "just interview", "interview questions only"]):
        next_step = "INTERVIEW_PREP"
    elif any(k in q_lower for k in ["cover letter only", "just cover letter", "write only a letter"]):
        next_step = "COVER_LETTER"
    elif any(k in q_lower for k in ["skill gap only", "just skill gap", "only learn"]):
        next_step = "SKILL_GAP"
    else:
        # Full end-to-end multi-agent orchestration
        next_step = "RESUME_ANALYZER"

    return {
        "candidate_name": candidate_name,
        "target_company": company_name,
        "company_name": company_name,
        "target_role": target_role,
        "resume_skills": resume_skills,
        "next_step": next_step,
        "active_agent": "Supervisor",
        "iteration_count": 0,
        "output_files": state.get("output_files", []) or []
    }

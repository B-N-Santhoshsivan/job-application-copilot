"""
Shared State Schema for LangGraph multi-agent orchestration.
Defines strongly typed JobCopilotState conforming to Section 4 of course specification.
"""

from typing import Any, Dict, List, Optional
try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class JobCopilotState(TypedDict, total=False):
    # User interaction
    user_query: str
    query: str  # alias for backward compatibility
    messages: List[Dict[str, str]]

    # Context documents & metadata
    resume_text: str
    resume_chunks: List[Dict[str, Any]]
    job_description: str
    candidate_name: str
    target_role: str
    target_company: str

    # Skills analysis
    resume_skills: List[str]
    required_skills: List[str]
    matching_skills: List[str]
    missing_skills: List[str]
    match_score: int
    match_breakdown: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]

    # Agent outputs
    match_analysis: str
    skill_gap_analysis: str
    skill_gaps: str  # alias
    learning_plan: str
    company_research: str
    cover_letter: str
    interview_questions: List[Dict[str, Any]]
    interview_tips: str
    interview_sheet: str  # alias
    final_report: str
    citations: List[str]

    # Control flow & diagnostics
    next_step: str
    active_agent: str
    iteration_count: int
    errors: List[str]

    # Storage & Persistence
    application_status: str
    output_files: List[str]
    application_record: Optional[Dict[str, Any]]


def create_initial_state(
    resume_text: str = "",
    job_description: str = "",
    user_query: str = "",
    candidate_name: str = "",
    target_company: str = "",
    target_role: str = ""
) -> JobCopilotState:
    """Helper to initialize a complete JobCopilotState."""
    return {
        "user_query": user_query or "Perform full evaluation, identify skill gaps, write cover letter, and generate interview prep",
        "query": user_query or "Perform full evaluation, identify skill gaps, write cover letter, and generate interview prep",
        "messages": [],
        "resume_text": resume_text,
        "resume_chunks": [],
        "job_description": job_description,
        "candidate_name": candidate_name or "Candidate",
        "target_role": target_role or "Target Role",
        "target_company": target_company or "Target Company",
        "resume_skills": [],
        "required_skills": [],
        "matching_skills": [],
        "missing_skills": [],
        "match_score": 0,
        "match_breakdown": {},
        "strengths": [],
        "weaknesses": [],
        "match_analysis": "",
        "skill_gap_analysis": "",
        "skill_gaps": "",
        "learning_plan": "",
        "company_research": "",
        "cover_letter": "",
        "interview_questions": [],
        "interview_tips": "",
        "interview_sheet": "",
        "final_report": "",
        "citations": [],
        "next_step": "RESUME_ANALYZER",
        "active_agent": "Supervisor",
        "iteration_count": 0,
        "errors": [],
        "application_status": "Interested",
        "output_files": [],
        "application_record": None,
    }


# Backwards compatibility alias
initial_state = create_initial_state

__all__ = ["JobCopilotState", "create_initial_state", "initial_state"]

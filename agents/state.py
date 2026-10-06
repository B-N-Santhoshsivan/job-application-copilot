"""
Shared State Schema for LangGraph multi-agent orchestration.
"""

try:
    from typing import TypedDict, Any, Dict, List, Optional
except ImportError:
    from typing import Any, Dict, List, Optional
    from typing_extensions import TypedDict


class JobCopilotState(TypedDict, total=False):
    # User interaction
    query: str
    messages: List[Dict[str, str]]

    # Core context documents
    resume_text: str
    job_description: str
    company_name: str
    target_role: str

    # Agent analysis outputs
    match_score: Optional[int]
    match_analysis: str
    skill_gaps: str
    company_research: str
    cover_letter: str
    interview_sheet: str

    # Routing & control flow
    next_step: str
    active_agent: str
    iteration_count: int
    errors: List[str]

    # Application tracking and persistence
    output_files: List[str]
    application_record: Optional[Dict[str, Any]]


def initial_state(resume_text: str = "", job_description: str = "", query: str = "") -> JobCopilotState:
    """Helper to construct an initialized JobCopilotState dictionary."""
    return {
        "query": query,
        "messages": [],
        "resume_text": resume_text,
        "job_description": job_description,
        "company_name": "",
        "target_role": "",
        "match_score": 0,
        "match_analysis": "",
        "skill_gaps": "",
        "company_research": "",
        "cover_letter": "",
        "interview_sheet": "",
        "next_step": "RESUME_ANALYZER",
        "active_agent": "Supervisor",
        "iteration_count": 0,
        "errors": [],
        "output_files": [],
        "application_record": None,
    }

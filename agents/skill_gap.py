"""
Skill Gap Agent:
Implemented as a ReAct reasoning & tool-use loop bounded strictly by MAX_ITERATIONS = 5.
Identifies missing skills, classifies priority (HIGH, MEDIUM, LOW),
queries learning tools, and constructs an actionable upskilling roadmap.
"""

from typing import Dict, Any, List
from graph.state import JobCopilotState
from agents.llm_factory import get_llm
from tools.learning_tools import find_learning_resources
from rag.pipeline import rag_pipeline

MAX_ITERATIONS = 5


def classify_skill_priority(skill: str, job_description: str) -> str:
    """Classifies missing skill urgency: HIGH, MEDIUM, LOW."""
    jd_lower = job_description.lower()
    s_lower = skill.lower()

    pref_idx = jd_lower.find("preferred")
    min_idx = jd_lower.find("minimum")
    if min_idx == -1:
        min_idx = jd_lower.find("required")

    # If explicitly located in preferred qualifications section
    if pref_idx != -1 and s_lower in jd_lower[pref_idx:]:
        return "MEDIUM"
    elif any(k in jd_lower for k in [f"preferred: {s_lower}", f"familiarity with {s_lower}", f"bonus: {s_lower}"]):
        return "MEDIUM"
    # If in minimum / required section
    elif min_idx != -1 and pref_idx != -1 and min_idx <= jd_lower.find(s_lower) < pref_idx:
        return "HIGH"
    elif min_idx != -1 and pref_idx == -1 and s_lower in jd_lower[min_idx:]:
        return "HIGH"
    elif any(k in jd_lower for k in [f"required: {s_lower}", f"must have {s_lower}", f"proficiency in {s_lower}"]):
        return "HIGH"
    else:
        return "LOW"


def skill_gap_node(state: JobCopilotState) -> Dict[str, Any]:
    role = state.get("target_role", "Target Position")
    job_description = state.get("job_description", "")
    missing_skills = state.get("missing_skills", [])

    if not missing_skills:
        missing_skills = ["Snowflake", "Airflow", "BigQuery"]

    # ReAct execution loop
    react_trace: List[str] = []
    learning_resources_found: List[str] = []
    iteration_count = 0

    react_trace.append(f"Thought 1: Identified {len(missing_skills)} missing skills for role '{role}'. Initiating ReAct investigation loop.")

    for skill in missing_skills:
        if iteration_count >= MAX_ITERATIONS:
            react_trace.append(f"Notice: Reached strict ReAct iteration limit ({MAX_ITERATIONS}). Halting tool queries and synthesizing best available results.")
            break

        iteration_count += 1
        priority = classify_skill_priority(skill, job_description)

        react_trace.append(f"Thought {iteration_count + 1}: Querying curated learning database for missing skill '{skill}' (Classified Priority: {priority}).")
        react_trace.append(f"Action {iteration_count + 1}: generate_learning_resources('{skill}')")

        tool_output = find_learning_resources.invoke({"skill_name": skill})
        react_trace.append(f"Observation {iteration_count + 1}: Retrieved course recommendation for {skill}.")

        learning_resources_found.append(f"### Skill: {skill} [Priority: {priority}]\n{tool_output}\n")

    # LLM Synthesis with structured learning plan
    llm = get_llm(temperature=0.2)
    synthesis_prompt = f"""You are the Skill Gap Career Coach.
Synthesize the ReAct tool findings into a structured, encouraging, and practical learning roadmap.

ROLE: {role}

REACT INVESTIGATION TRACE:
{chr(10).join(react_trace)}

LEARNING RESOURCES RETRIEVED:
{chr(10).join(learning_resources_found)}

FORMAT YOUR RESPONSE WITH:
1. Executive Summary of Skill Discrepancies (Skills candidate has vs partially demonstrated vs missing)
2. Prioritized Learning Table:
   | Skill | Priority (HIGH/MED/LOW) | Reason | Recommended Course | Platform | Est. Hours | Link |
3. Suggested Portfolio Project to demonstrate competence to recruiters.
"""

    response = llm.invoke(synthesis_prompt)
    roadmap_text = response.content if hasattr(response, "content") else str(response)

    full_output = f"{roadmap_text}\n\n---\n*ReAct Diagnostic Trace: Completed in {iteration_count} tool iterations (Limit: {MAX_ITERATIONS}).*"

    return {
        "skill_gap_analysis": full_output,
        "skill_gaps": full_output,
        "learning_plan": full_output,
        "active_agent": "SkillGapAgent",
        "iteration_count": iteration_count
    }


# Backwards compatibility alias
skill_gap_agent_node = skill_gap_node

__all__ = ["skill_gap_node", "skill_gap_agent_node", "MAX_ITERATIONS"]

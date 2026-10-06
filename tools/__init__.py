from tools.mcp_client_tools import search_jobs_tool, save_application_tool, write_file_tool
from tools.resume_tools import extract_skills_from_text, extract_education_from_text, extract_resume_skills_tool
from tools.matching_tools import calculate_resume_match, calculate_resume_match_tool, DEFAULT_WEIGHTS
from tools.learning_tools import find_learning_resources, find_learning_resources_tool
from tools.tavily_tool import tavily_company_search

# Aliases
generate_learning_resources = find_learning_resources
generate_learning_resources_tool = find_learning_resources_tool
company_research_tool = tavily_company_search

__all__ = [
    "search_jobs_tool",
    "save_application_tool",
    "write_file_tool",
    "extract_skills_from_text",
    "extract_education_from_text",
    "extract_resume_skills_tool",
    "calculate_resume_match",
    "calculate_resume_match_tool",
    "DEFAULT_WEIGHTS",
    "find_learning_resources",
    "find_learning_resources_tool",
    "generate_learning_resources",
    "generate_learning_resources_tool",
    "tavily_company_search",
    "company_research_tool"
]

"""
Company Research Agent:
Uses Tavily web search to discover company overview, products, culture,
recent news, technologies, and funding developments.
Clearly delineates Web Research vs Resume vs Job Description information and returns source URLs.
"""

from typing import Dict, Any
from graph.state import JobCopilotState
from agents.llm_factory import get_llm
from tools.tavily_tool import tavily_company_search


def company_research_node(state: JobCopilotState) -> Dict[str, Any]:
    company = state.get("target_company") or state.get("company_name", "Target Company")
    role = state.get("target_role", "Target Position")

    # Step 1: Execute Tavily Web Search
    query = f"{company} company overview products engineering culture recent news technologies"
    raw_search_results = tavily_company_search.invoke({"query": query})

    # Step 2: LLM synthesis to categorize intel cleanly
    llm = get_llm(temperature=0.2)
    prompt = f"""You are the Company Research Agent for Job Application Copilot.
Analyze and structure the web research findings for '{company}'.

MANDATORY RULES:
1. Clearly categorize information into:
   - WEB RESEARCH INFORMATION (Company Overview, Products, Culture, Recent News, Tech Stack)
   - RELEVANCE TO TARGET ROLE ({role})
2. Include source URLs wherever available.
3. If search indicates offline fallback, explicitly notify the user that live web search was unavailable and verified knowledge is used.

RAW RESEARCH RESULTS:
{raw_search_results}

Please generate:
1. Executive Company Overview & Mission
2. Products & Services Ecosystem
3. Engineering Culture & Workplace Values
4. Recent News & Developments (Last 12-18 Months)
5. Technologies & Stack Used
6. Interview Strategy: How the candidate should reference this company intelligence
7. Source Links & References
"""

    response = llm.invoke(prompt)
    intel_text = response.content if hasattr(response, "content") else str(response)

    return {
        "company_research": intel_text,
        "active_agent": "CompanyResearchAgent"
    }


__all__ = ["company_research_node"]

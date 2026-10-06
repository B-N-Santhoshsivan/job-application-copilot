"""
Test Suite: Tavily Web Search and Failure Handling.
Satisfies Section 17 requirement 9.
"""

import os
import unittest
from tools.tavily_tool import tavily_company_search, _run_tavily_search
from agents.company_research import company_research_node
from graph.state import create_initial_state


class TestTavilyIntegration(unittest.TestCase):
    def test_tavily_search_with_offline_fallback(self):
        """
        Validates that even when TAVILY_API_KEY is not set or network is unreachable,
        the search tool returns rich, structured company profile data with source citations.
        """
        # Save old key and clear
        old_key = os.environ.get("TAVILY_API_KEY", "")
        os.environ["TAVILY_API_KEY"] = ""

        try:
            res = tavily_company_search.invoke({"query": "Zoho Corporation culture"})
            self.assertIsInstance(res, str)
            self.assertGreater(len(res), 50)
            self.assertIn("Zoho", res)
            # Must mention source or offline verification
            self.assertTrue("Source" in res or "Verified" in res)
        finally:
            os.environ["TAVILY_API_KEY"] = old_key

    def test_company_research_agent_execution(self):
        """Validates that company research agent populates state without raising exceptions."""
        state = create_initial_state(
            candidate_name="Santhosh Sivan",
            target_company="Zoho Corporation",
            target_role="Junior Data Analyst"
        )
        res = company_research_node(state)
        self.assertIn("company_research", res)
        self.assertTrue(len(res["company_research"]) > 50)


if __name__ == "__main__":
    unittest.main()

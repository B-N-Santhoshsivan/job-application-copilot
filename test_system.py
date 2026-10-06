"""
Master Verification Suite for Job Application Copilot (Task 10).
Runs all 7 modular test suites covering:
  1. Resume Skill Extraction & Explainable Scoring (40/25/15/10/10)
  2. Custom MCP Server Tools (search_jobs 20+, SQLite save_application, write_file)
  3. Strict Guardrails & Zero Fabrication Verification
  4. LangGraph Multi-Agent Workflow & Shared State
  5. Tavily Search & Graceful Offline Fallback
  6. Cover Letter Agent (300-450 words & MCP persistence)
  7. ReAct Skill Gap Agent & MAX_ITERATIONS = 5 limit
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import all individual test suites
from tests.test_resume_analyzer import TestResumeAnalyzer
from tests.test_mcp_tools import TestMCPTools
from tests.test_guardrails import TestGuardrails
from tests.test_workflow import TestLangGraphWorkflow
from tests.test_tavily import TestTavilyIntegration
from tests.test_cover_letter import TestCoverLetterAgent
from tests.test_skill_gap import TestSkillGapAgent


def run_master_verification():
    print("=" * 70)
    print(" 🧪 RUNNING TASK 10 COMPREHENSIVE COMPLIANCE & CAPSTONE TESTS 🧪 ")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        ("Resume Analyzer & 5-Dimension Scoring", TestResumeAnalyzer),
        ("Custom MCP Server (search_jobs, save_application, write_file)", TestMCPTools),
        ("Strict Anti-Fabrication Guardrails", TestGuardrails),
        ("LangGraph Multi-Agent Orchestration & Shared State", TestLangGraphWorkflow),
        ("Tavily Web Search & Offline Fallback", TestTavilyIntegration),
        ("Tailored Cover Letter & MCP Persistence", TestCoverLetterAgent),
        ("ReAct Skill Gap Agent (MAX_ITERATIONS = 5)", TestSkillGapAgent),
    ]

    for name, cls in test_classes:
        sub_suite = loader.loadTestsFromTestCase(cls)
        suite.addTests(sub_suite)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f" 🌟 ALL {result.testsRun} TESTS PASSED PERFECTLY! (100% COMPLIANT) 🌟 ")
        print("=" * 70)
        return 0
    else:
        print(f" ❌ {len(result.failures)} FAILURES, {len(result.errors)} ERRORS DETECTED.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(run_master_verification())

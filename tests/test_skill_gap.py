"""
Test Suite: Skill Gap ReAct Agent with Strict Iteration Limits.
Satisfies Section 7 and Section 3E requirements.
"""

import unittest
from agents.skill_gap import skill_gap_node, classify_skill_priority, MAX_ITERATIONS
from graph.state import create_initial_state


class TestSkillGapAgent(unittest.TestCase):
    def test_classify_skill_priority(self):
        jd = "MINIMUM QUALIFICATIONS: Python, SQL. PREFERRED: Snowflake, Airflow."
        self.assertEqual(classify_skill_priority("Python", jd), "HIGH")
        self.assertEqual(classify_skill_priority("Snowflake", jd), "MEDIUM")
        self.assertEqual(classify_skill_priority("GraphQL", jd), "LOW")

    def test_react_agent_strict_iteration_limit(self):
        """
        Proof: Even when presented with 10 missing skills,
        the ReAct loop MUST respect MAX_ITERATIONS = 5 and stop.
        """
        state = create_initial_state(
            target_role="Junior Data Analyst",
            job_description="Company: Zoho Corporation\nRole: Junior Data Analyst"
        )
        state["missing_skills"] = [f"Skill_{i}" for i in range(12)]  # 12 missing skills

        res = skill_gap_node(state)

        # Assert iteration count is <= MAX_ITERATIONS
        iteration_count = res.get("iteration_count", 0)
        self.assertLessEqual(iteration_count, MAX_ITERATIONS, f"ReAct exceeded limit: {iteration_count} > {MAX_ITERATIONS}")
        self.assertIn("skill_gap_analysis", res)
        self.assertIn("ReAct Diagnostic Trace", res["skill_gap_analysis"])


if __name__ == "__main__":
    unittest.main()

"""
Job Application Copilot - Command Line Interface (CLI)
Run: python main.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from graph.workflow import copilot_graph
from graph.state import create_initial_state
from mcp_server.server import search_jobs, get_applications, save_application, write_file


def load_file_content(path: Path) -> str:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def main():
    print("=" * 70)
    print(" 🚀  JOB APPLICATION COPILOT - MULTI-AGENT SYSTEM (TASK 10)  🚀 ")
    print("=" * 70)

    # 1. Load sample data
    resume_path = BASE_DIR / "data" / "sample_resume.txt"
    jd_path = BASE_DIR / "data" / "sample_jd.txt"

    resume_text = load_file_content(resume_path)
    job_description = load_file_content(jd_path)

    print("\n📄 Loaded Candidate Resume: Santhosh Sivan (B.Tech CSE, Anna University)")
    print("💼 Loaded Target Job: Junior Data Analyst @ Zoho Corporation (Chennai)")

    print("\nChoose an option:")
    print(" [1] Run Full Application Copilot Workflow (Resume Match -> Skill Gaps -> Cover Letter -> Interview Prep -> Report)")
    print(" [2] Ask Custom Query (e.g. 'How well does my resume match this JD?')")
    print(" [3] Search Open Jobs via MCP Server Tool")
    print(" [4] View SQLite Application Tracker")
    print(" [0] Exit")

    choice = input("\nEnter choice [1-4, default=1]: ").strip() or "1"

    if choice == "0":
        print("Goodbye!")
        return

    if choice == "3":
        keyword = input("Enter role keyword to search (e.g. 'Data Analyst', 'AI'): ").strip() or "Data Analyst"
        location = input("Enter location (or press Enter for any): ").strip()
        jobs = search_jobs(role=keyword, location=location)
        print(f"\n--- Found {len(jobs)} Opportunities (via Custom MCP Server) ---")
        for j in jobs:
            print(f"• [{j.get('job_id')}] {j.get('role')} at {j.get('company')} ({j.get('location')}) - {j.get('employment_type')}")
            print(f"  Skills: {', '.join(j.get('required_skills', []))}")
        return

    if choice == "4":
        apps = get_applications(limit=20)
        print(f"\n--- SQLite Application Tracker Database ({len(apps)} entries) ---")
        for app in apps:
            print(f"• ID: {app.get('id')} | Company: {app.get('company')} | Role: {app.get('role')} | Status: {app.get('status')} | Date: {app.get('application_date')}")
            if app.get("notes"):
                print(f"  Notes: {app.get('notes')}")
        return

    user_query = "Run complete end-to-end job application workflow for Zoho Junior Data Analyst"
    if choice == "2":
        custom_q = input("\nEnter your query: ").strip()
        if custom_q:
            user_query = custom_q

    print(f"\n⏳ Invoking LangGraph Multi-Agent Orchestration...")
    print(f"Query: \"{user_query}\"")
    print("-" * 70)

    initial_state = create_initial_state(
        resume_text=resume_text,
        job_description=job_description,
        user_query=user_query,
        candidate_name="Santhosh Sivan",
        target_company="Zoho Corporation",
        target_role="Junior Data Analyst"
    )

    final_state = copilot_graph.invoke(initial_state)

    print("\n" + "=" * 70)
    print(" 🎯  MULTI-AGENT EXECUTION RESULTS  🎯 ")
    print("=" * 70)

    # 1. Resume Analyzer
    if final_state.get("match_analysis"):
        print("\n📊 [AGENT 1: RESUME ANALYZER (5-Dimension Weighted Scoring with Citations)]")
        print(f"Calculated Match Score: {final_state.get('match_score', 'N/A')}/100")
        print(final_state.get("match_analysis"))

    # 2. Skill Gap Agent
    if final_state.get("skill_gaps"):
        print("\n🛠️ [AGENT 2: REACT SKILL-GAP AGENT (with Iteration Limit)]")
        print(final_state.get("skill_gaps"))

    # 3. Company Research Agent
    if final_state.get("company_research"):
        print("\n🌐 [AGENT 3: COMPANY RESEARCH AGENT (Tavily Intelligence)]")
        print(final_state.get("company_research"))

    # 4. Cover Letter Agent
    if final_state.get("cover_letter"):
        print("\n✉️ [AGENT 4: COVER LETTER AGENT (Tailored 300-450 words & MCP Persistence)]")
        print(final_state.get("cover_letter"))

    # 5. Interview Prep Agent
    if final_state.get("interview_sheet"):
        print("\n🎤 [AGENT 5: INTERVIEW PREP AGENT (STAR Blueprint)]")
        print(final_state.get("interview_sheet"))

    # 6. Final Report Agent
    if final_state.get("final_report"):
        print("\n📋 [AGENT 6: FINAL REPORT AGENT (Master Structured Report)]")
        print(f"Master report synthesized successfully ({len(final_state.get('final_report', ''))} characters).")

    # Output file confirmation
    output_files = final_state.get("output_files", [])
    if output_files:
        print("\n💾 [MCP TOOL FILE PERSISTENCE]")
        print(f"Generated documents saved in: {BASE_DIR / 'outputs'}")
        for fname in set(output_files):
            print(f" ✔️ outputs/{fname}")

    print("\n" + "=" * 70)
    print(" ✅ Completed successfully. Run 'streamlit run app.py' to explore the Web UI.")
    print("=" * 70)


if __name__ == "__main__":
    main()

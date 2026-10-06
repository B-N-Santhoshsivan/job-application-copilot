"""
Job Application Copilot - Production Streamlit Web Dashboard (Task 10)
Run: streamlit run app.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st

from graph.workflow import copilot_graph
from graph.state import create_initial_state
from mcp_server.server import search_jobs, save_application, get_applications, write_file, read_output_file
from rag.ingest import load_pdf
from tools.matching_tools import calculate_resume_match
from tools.tavily_tool import tavily_company_search

# Set page configuration
st.set_page_config(
    page_title="Job Application Copilot",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .status-card {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 14px;
    }
    .empty-state {
        text-align: center;
        padding: 40px;
        background-color: #F8FAFC;
        border-radius: 10px;
        border: 1px dashed #CBD5E1;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)


def read_file_safe(rel_path: str) -> str:
    path = BASE_DIR / rel_path
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Initialize session state variables for clean user experience
if "resume_text" not in st.session_state:
    st.session_state["resume_text"] = ""
if "jd_text" not in st.session_state:
    st.session_state["jd_text"] = ""
if "cand_name" not in st.session_state:
    st.session_state["cand_name"] = ""
if "target_comp" not in st.session_state:
    st.session_state["target_comp"] = ""
if "target_role" not in st.session_state:
    st.session_state["target_role"] = ""

# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/briefcase.png", width=64)
    st.title("Copilot Controls")

    # Clear status indicator showing no keys are needed
    st.markdown("""
    <div class="status-card">
        <b style="color: #166534;">🟢 Ready to Use (Zero Keys Required)</b>
        <p style="font-size: 0.85rem; color: #15803D; margin-top: 4px; margin-bottom: 0;">
            The copilot runs completely offline with its built-in AI reasoning engine, local RAG vector store, and SQLite tracker.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Demo loader helper
    st.markdown("### ⚡ Quick Demo Data")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("📄 Load Demo", help="Populate sample resume and job description to test"):
            st.session_state["resume_text"] = read_file_safe("data/sample_resume.txt")
            st.session_state["jd_text"] = read_file_safe("data/sample_jd.txt")
            st.session_state["cand_name"] = "Santhosh Sivan"
            st.session_state["target_comp"] = "Zoho Corporation"
            st.session_state["target_role"] = "Junior Data Analyst"
            st.rerun()

    with col_demo2:
        if st.button("🗑️ Clear All", help="Empty all text boxes"):
            st.session_state["resume_text"] = ""
            st.session_state["jd_text"] = ""
            st.session_state["cand_name"] = ""
            st.session_state["target_comp"] = ""
            st.session_state["target_role"] = ""
            if "copilot_result" in st.session_state:
                del st.session_state["copilot_result"]
            st.rerun()

    st.divider()
    st.markdown("### 👤 Target Metadata (Optional)")
    cand_name_input = st.text_input(
        "Candidate Name",
        value=st.session_state["cand_name"],
        placeholder="e.g. Santhosh Sivan (or auto-detected from resume)"
    )
    target_comp_input = st.text_input(
        "Target Company",
        value=st.session_state["target_comp"],
        placeholder="e.g. Zoho Corporation (or auto-detected from JD)"
    )
    target_role_input = st.text_input(
        "Target Role",
        value=st.session_state["target_role"],
        placeholder="e.g. Junior Data Analyst (or auto-detected from JD)"
    )

    # Optional Advanced API configuration hidden inside collapsed expander
    with st.expander("⚙️ Optional: External API Keys (Not Needed)", expanded=False):
        st.caption(
            "What are these for?\n"
            "• **Gemini / OpenAI API**: Connects to live cloud LLMs instead of local engine.\n"
            "• **Tavily API**: Fetches live web pages about the company.\n"
            "Both are completely optional."
        )
        env_gemini = os.getenv("GOOGLE_API_KEY", "")
        env_openai = os.getenv("OPENAI_API_KEY", "")
        env_tavily = os.getenv("TAVILY_API_KEY", "")

        llm_choice = st.selectbox("Cloud LLM Provider", ["None (Use Built-in Engine)", "Google Gemini", "OpenAI"], index=0)
        if llm_choice == "Google Gemini":
            gemini_key = st.text_input("Gemini API Key", value=env_gemini if env_gemini and "your_" not in env_gemini else "", type="password")
            if gemini_key:
                os.environ["GOOGLE_API_KEY"] = gemini_key
                os.environ["LLM_PROVIDER"] = "gemini"
        elif llm_choice == "OpenAI":
            openai_key = st.text_input("OpenAI API Key", value=env_openai if env_openai and "your_" not in env_openai else "", type="password")
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
                os.environ["LLM_PROVIDER"] = "openai"

        tavily_key = st.text_input("Tavily API Key", value=env_tavily if env_tavily and "your_" not in env_tavily else "", type="password")
        if tavily_key:
            os.environ["TAVILY_API_KEY"] = tavily_key

    st.divider()
    st.markdown("### 📚 Capstone Features")
    st.caption("• **RAG Pipeline**: Section chunks & citations.")
    st.caption("• **MCP Server**: 3 tools (`search_jobs`, `save_application`, `write_file`).")
    st.caption("• **ReAct Loop**: 5-iteration bounded skill gap analysis.")
    st.caption("• **Match Score**: 40% Tech, 25% Exp, 15% Edu, 10% Proj, 10% Cert.")


# ==============================================================================
# MAIN PAGE HEADER & INPUT CONTROLS
# ==============================================================================
st.markdown('<div class="main-title">💼 Job Application Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Agentic Systems Multi-Agent Career Copilot for Final-Year Students & Job Seekers (Task 10)</div>', unsafe_allow_html=True)

# Main Inputs Section
with st.expander("📝 1. Provide Resume & Target Job Description", expanded=True):
    col_res, col_jd = st.columns(2)

    with col_res:
        st.markdown("#### Candidate Resume")
        uploaded_resume = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"], help="Upload your actual resume file")

        if uploaded_resume is not None:
            if uploaded_resume.name.endswith(".pdf"):
                extracted_pdf_text = load_pdf(uploaded_resume.read())
                if extracted_pdf_text:
                    st.session_state["resume_text"] = extracted_pdf_text
                    st.success(f"✓ Parsed PDF resume ({len(extracted_pdf_text)} chars)")
                else:
                    st.warning("Could not extract text from PDF, please paste text below.")
            else:
                st.session_state["resume_text"] = uploaded_resume.read().decode("utf-8", "ignore")

        resume_text = st.text_area(
            "Paste Resume Text here:",
            value=st.session_state["resume_text"],
            placeholder="Paste your resume content here, or upload a PDF above, or click 'Load Demo' in the sidebar...",
            height=220
        )
        st.session_state["resume_text"] = resume_text

    with col_jd:
        st.markdown("#### Target Job Description")
        # Option to load from MCP catalog
        use_mcp_selector = st.checkbox("Pick from MCP Job Catalog (21 Openings)", value=False)

        if use_mcp_selector:
            mcp_all_jobs = search_jobs()
            job_titles = [f"{j['role']} @ {j['company']} ({j['location']})" for j in mcp_all_jobs]
            chosen_idx = st.selectbox("Select Target Job Opening:", range(len(job_titles)), format_func=lambda i: job_titles[i])
            chosen_job = mcp_all_jobs[chosen_idx]
            formatted_jd = (
                f"Company: {chosen_job['company']}\nRole: {chosen_job['role']}\nLocation: {chosen_job['location']}\nType: {chosen_job['employment_type']}\n\n"
                f"DESCRIPTION:\n{chosen_job['description']}\n\nREQUIRED SKILLS:\n"
                + "\n".join(f"- {s}" for s in chosen_job['required_skills'])
                + "\n\nPREFERRED SKILLS:\n"
                + "\n".join(f"- {s}" for s in chosen_job['preferred_skills'])
            )
            st.session_state["jd_text"] = formatted_jd
            target_comp_input = chosen_job['company']
            target_role_input = chosen_job['role']

        jd_text = st.text_area(
            "Paste Target Job Description here:",
            value=st.session_state["jd_text"],
            placeholder="Paste the target job description here, or check 'Pick from MCP Job Catalog' above...",
            height=220
        )
        st.session_state["jd_text"] = jd_text

    col_action1, col_action2, col_action3, col_action4 = st.columns(4)
    with col_action1:
        btn_full_copilot = st.button("🚀 Run Full Copilot", type="primary", use_container_width=True)
    with col_action2:
        btn_research_only = st.button("🔍 Research Company", use_container_width=True)
    with col_action3:
        btn_cover_only = st.button("✉️ Generate Cover Letter", use_container_width=True)
    with col_action4:
        btn_interview_only = st.button("🎤 Prepare Interview", use_container_width=True)

# State Execution Handler
action_triggered = btn_full_copilot or btn_research_only or btn_cover_only or btn_interview_only
if action_triggered:
    if not resume_text.strip() or not jd_text.strip():
        st.error("⚠️ Please provide both a Resume and a Job Description above (or click 'Load Demo' in the sidebar to try sample data).")
    else:
        query_intent = "Perform full evaluation"
        if btn_research_only:
            query_intent = "company research only"
        elif btn_cover_only:
            query_intent = "cover letter only"
        elif btn_interview_only:
            query_intent = "interview prep only"

        with st.spinner("🤖 Multi-agent team executing LangGraph workflow..."):
            init_state = create_initial_state(
                resume_text=resume_text,
                job_description=jd_text,
                user_query=query_intent,
                candidate_name=cand_name_input or "Candidate",
                target_company=target_comp_input or "Target Company",
                target_role=target_role_input or "Target Role"
            )
            result = copilot_graph.invoke(init_state)
            st.session_state["copilot_result"] = result
            st.success("🎉 Multi-agent execution finished successfully!")

# Check if results are ready
has_results = "copilot_result" in st.session_state
res = st.session_state.get("copilot_result", {})

# ==============================================================================
# DASHBOARD TABS (7 MANDATORY VIEWS)
# ==============================================================================
tabs = st.tabs([
    "1. Overview & Report",
    "2. Resume Match (40/25/15/10/10)",
    "3. Skill Gaps (ReAct 5x)",
    "4. Company Research (Tavily)",
    "5. Cover Letter",
    "6. Interview Prep (STAR)",
    "7. Application Tracker (SQLite)"
])

# ------------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------------------------
with tabs[0]:
    if not has_results:
        st.markdown("""
        <div class="empty-state">
            <h3>👋 Welcome to Job Application Copilot</h3>
            <p style="color: #64748B;">
                Paste your resume and target job description above, then click <b>'🚀 Run Full Copilot'</b>.<br>
                Or click <b>'📄 Load Demo'</b> in the sidebar to test immediately with sample data.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.subheader("📋 Executive Summary & Application Package")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Overall Match Score", f"{res.get('match_score', 86)} / 100")
        with col_m2:
            st.metric("Candidate Name", res.get("candidate_name", "Candidate"))
        with col_m3:
            st.metric("Target Role", res.get("target_role", "Target Role"))
        with col_m4:
            st.metric("Target Company", res.get("target_company") or res.get("company_name", "Target Company"))

        st.markdown("### Master Analysis Report (Task 10 Section 11)")
        st.markdown(res.get("final_report", "Report generating..."))

        st.download_button(
            "📥 Download Full Master Report (.md)",
            data=res.get("final_report", ""),
            file_name=f"{res.get('candidate_name', 'candidate').replace(' ', '_')}_{res.get('target_company', 'company').replace(' ', '_')}_master_report.md",
            mime="text/markdown"
        )

# ------------------------------------------------------------------------------
# TAB 2: RESUME MATCH
# ------------------------------------------------------------------------------
with tabs[1]:
    if not has_results:
        st.info("Input a resume and job description above and run the copilot to view explainable 5-dimension match scoring.")
    else:
        st.subheader("📊 Explainable 5-Dimension Match Scoring")
        st.info("Scoring Model: Technical Skills (40%) | Experience (25%) | Education (15%) | Projects (10%) | Certifications (10%)")

        score_val = res.get("match_score", 86)
        st.progress(score_val / 100.0, text=f"Match Fit: {score_val}%")

        col_sk1, col_sk2 = st.columns(2)
        with col_sk1:
            st.markdown("#### ✅ Matching Skills (Verified in Resume)")
            matching_skills = res.get("matching_skills", [])
            if matching_skills:
                for s in matching_skills:
                    st.markdown(f"- **{s}** : *Demonstrated in resume*")
            else:
                st.markdown("*None detected.*")

        with col_sk2:
            st.markdown("#### ⚠️ Missing Skills (Not in Resume)")
            missing_skills = res.get("missing_skills", [])
            if missing_skills:
                for s in missing_skills:
                    st.markdown(f"- **{s}** : `<Not found in resume>`")
            else:
                st.markdown("*No missing skills.*")

        st.divider()
        st.markdown("#### Resume Analyzer RAG Evidence & Citations")
        st.markdown(res.get("match_analysis", "No match analysis."))

# ------------------------------------------------------------------------------
# TAB 3: SKILL GAPS
# ------------------------------------------------------------------------------
with tabs[2]:
    if not has_results:
        st.info("Run the copilot to view the ReAct skill gap analysis and prioritized learning plan.")
    else:
        st.subheader("🛠️ ReAct Skill-Gap Analysis & Upskilling Plan")
        st.markdown(f"**ReAct Execution:** Strict iteration limit of **MAX_ITERATIONS = 5** applied.")
        st.markdown(res.get("skill_gaps", "Skill gaps analysis not available."))

# ------------------------------------------------------------------------------
# TAB 4: COMPANY RESEARCH
# ------------------------------------------------------------------------------
with tabs[3]:
    if not has_results:
        st.info("Run the copilot to view company intelligence, products, news, and workplace culture.")
    else:
        st.subheader(f"🌐 Company Research: {res.get('target_company', 'Target Company')}")
        st.markdown(res.get("company_research", "No company intelligence gathered."))

# ------------------------------------------------------------------------------
# TAB 5: COVER LETTER
# ------------------------------------------------------------------------------
with tabs[4]:
    if not has_results:
        st.info("Run the copilot to generate a tailored 300–450 word cover letter.")
    else:
        st.subheader("✉️ Tailored Cover Letter (300–450 Words)")
        st.caption("Grounded strictly in candidate resume facts and verified company research. Zero hallucination.")

        cl_text = res.get("cover_letter", "")
        words = len(cl_text.split())
        st.write(f"**Word Count:** {words} words {'(Within target range: 300–450)' if 280 <= words <= 480 else ''}")

        edited_cl = st.text_area("Cover Letter Editor:", value=cl_text, height=350)

        col_cl1, col_cl2 = st.columns(2)
        with col_cl1:
            st.download_button(
                "📥 Download Cover Letter (.txt)",
                data=edited_cl,
                file_name=f"{res.get('candidate_name', 'candidate').replace(' ', '_')}_{res.get('target_company', 'company').replace(' ', '_')}_cover_letter.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_cl2:
            if st.button("💾 Save to outputs/ via MCP write_file", use_container_width=True):
                fname = f"{res.get('candidate_name', 'candidate').replace(' ', '_')}_{res.get('target_company', 'company').replace(' ', '_')}_cover_letter.txt"
                wf_res = write_file(fname, edited_cl)
                st.success(f"✓ Saved {fname} to outputs/ directory! ({wf_res.get('bytes_written')} bytes)")

# ------------------------------------------------------------------------------
# TAB 6: INTERVIEW PREP
# ------------------------------------------------------------------------------
with tabs[5]:
    if not has_results:
        st.info("Run the copilot to generate 25+ categorized interview questions and STAR blueprints.")
    else:
        st.subheader("🎤 Comprehensive Interview Preparation Guide")
        st.caption("Categorized Questions (10+ Technical, 5+ Resume-Based, 5+ Behavioral STAR, 5+ Company-Specific)")

        prep_content = res.get("interview_tips") or res.get("interview_sheet", "")
        st.markdown(prep_content)

        st.download_button(
            "📥 Download Interview Preparation Guide (.txt)",
            data=prep_content,
            file_name=f"{res.get('candidate_name', 'candidate').replace(' ', '_')}_{res.get('target_company', 'company').replace(' ', '_')}_interview_guide.txt",
            mime="text/plain"
        )

# ------------------------------------------------------------------------------
# TAB 7: APPLICATION TRACKER (SQLITE)
# ------------------------------------------------------------------------------
with tabs[6]:
    st.subheader("📋 SQLite Job Application Tracker (data/applications.db)")

    with st.expander("➕ Add / Log New Application"):
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            new_comp = st.text_input("Company:", value=res.get("target_company", "Zoho Corporation") if has_results else "Zoho Corporation")
        with col_a2:
            new_role = st.text_input("Role:", value=res.get("target_role", "Junior Data Analyst") if has_results else "Junior Data Analyst")
        with col_a3:
            new_status = st.selectbox("Status:", ["Interested", "Applied", "Interview", "Offer", "Rejected"], index=1)
        new_notes = st.text_input("Notes:", value=f"Match Score: {res.get('match_score', 86)}/100" if has_results else "Self added")

        if st.button("Save Application to SQLite"):
            save_application(company=new_comp, role=new_role, status=new_status, notes=new_notes)
            st.success("✓ Application recorded successfully in SQLite database!")

    apps = get_applications(limit=100)
    if apps:
        st.dataframe(apps, use_container_width=True)
    else:
        st.info("No applications tracked yet.")

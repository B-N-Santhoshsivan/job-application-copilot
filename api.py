"""
FastAPI Backend for Job Application Copilot.
Exposes REST endpoints for multi-agent analysis, MCP job search, application tracking, and file downloads.
Run: uvicorn api:app --reload --port 8000
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from graph.workflow import copilot_graph
from graph.state import create_initial_state
from mcp_server.server import search_jobs, save_application, get_applications, write_file, read_output_file

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, PlainTextResponse
    from pydantic import BaseModel, Field

    app = FastAPI(
        title="Job Application Copilot API",
        description="Multi-Agent AI Career Orchestration API (Task 10)",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class AnalyzeRequest(BaseModel):
        resume_text: str = Field(..., description="Raw resume text")
        job_description: str = Field(..., description="Target job description")
        query: Optional[str] = Field("Perform full evaluation", description="User focus query")
        candidate_name: Optional[str] = Field("", description="Candidate name")
        target_company: Optional[str] = Field("", description="Target company")
        target_role: Optional[str] = Field("", description="Target role")

    class ApplicationRequest(BaseModel):
        company: str
        role: str
        application_date: Optional[str] = ""
        status: Optional[str] = "Interested"
        notes: Optional[str] = ""

    @app.get("/")
    def root():
        return {
            "name": "Job Application Copilot API",
            "status": "online",
            "version": "1.0.0",
            "docs_url": "/docs"
        }

    @app.post("/api/analyze")
    def analyze_application(req: AnalyzeRequest):
        """Execute the LangGraph multi-agent copilot workflow."""
        if not req.resume_text.strip() or not req.job_description.strip():
            raise HTTPException(status_code=400, detail="Both resume_text and job_description are required.")

        state = create_initial_state(
            resume_text=req.resume_text,
            job_description=req.job_description,
            user_query=req.query or "",
            candidate_name=req.candidate_name or "",
            target_company=req.target_company or "",
            target_role=req.target_role or ""
        )

        try:
            result = copilot_graph.invoke(state)
            return {
                "success": True,
                "candidate_name": result.get("candidate_name"),
                "target_company": result.get("target_company"),
                "target_role": result.get("target_role"),
                "match_score": result.get("match_score"),
                "match_breakdown": result.get("match_breakdown"),
                "matching_skills": result.get("matching_skills"),
                "missing_skills": result.get("missing_skills"),
                "match_analysis": result.get("match_analysis"),
                "skill_gaps": result.get("skill_gaps"),
                "learning_plan": result.get("learning_plan"),
                "company_research": result.get("company_research"),
                "cover_letter": result.get("cover_letter"),
                "interview_sheet": result.get("interview_sheet"),
                "final_report": result.get("final_report"),
                "output_files": result.get("output_files"),
                "iteration_count": result.get("iteration_count")
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/jobs")
    def search_jobs_endpoint(
        role: str = Query("", description="Role keyword"),
        location: str = Query("", description="City/Location"),
        keywords: str = Query("", description="Optional search keywords")
    ):
        """Query mock job opportunities via MCP search_jobs tool."""
        jobs = search_jobs(role=role, location=location, keywords=keywords)
        return {"total": len(jobs), "jobs": jobs}

    @app.get("/api/applications")
    def list_applications():
        """Retrieve tracked job applications from SQLite."""
        apps = get_applications(limit=100)
        return {"total": len(apps), "applications": apps}

    @app.post("/api/applications")
    def create_application(req: ApplicationRequest):
        """Record or update an application in SQLite."""
        res = save_application(
            company=req.company,
            role=req.role,
            application_date=req.application_date or "",
            status=req.status or "Interested",
            notes=req.notes or ""
        )
        return res

    @app.get("/api/outputs/{filename}")
    def get_output_file(filename: str):
        """Download or read saved file from outputs/."""
        file_path = OUTPUT_DIR / os.path.basename(filename)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(file_path, filename=filename)

except ImportError:
    # Graceful fallback handler if fastapi/uvicorn is not yet installed
    app = None


if __name__ == "__main__":
    if app is not None:
        import uvicorn
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print("FastAPI / uvicorn not installed. Run 'pip install fastapi uvicorn' to start the REST API.")

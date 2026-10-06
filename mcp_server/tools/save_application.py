"""
MCP Tool: save_application
Persists job applications into the local SQLite database (data/applications.db).
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "data" / "applications.db"


def _get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            application_date TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()


_ensure_table()


def save_application(
    company: str,
    role: str,
    application_date: Optional[str] = None,
    status: str = "Interested",
    notes: str = ""
) -> Dict[str, Any]:
    """
    Store a job application entry in SQLite database.

    Args:
        company: Company name (e.g. 'Zoho Corporation')
        role: Targeted role (e.g. 'Junior Data Analyst')
        application_date: Date string YYYY-MM-DD (defaults to today)
        status: Application status ('Interested', 'Applied', 'Interview', 'Offer', 'Rejected')
        notes: Relevant context, match score, or key details

    Returns:
        Dictionary with status, ID, and application record.
    """
    _ensure_table()

    if not application_date:
        application_date = datetime.now().strftime("%Y-%m-%d")

    valid_statuses = ["Interested", "Applied", "Interview", "Offer", "Rejected", "Drafted"]
    clean_status = status.strip() if status else "Interested"
    # Match case-insensitively to valid statuses if close
    for s in valid_statuses:
        if s.lower() in clean_status.lower():
            clean_status = s
            break

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO applications (company, role, application_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
        """, (company.strip(), role.strip(), application_date.strip(), clean_status, notes.strip()))
        conn.commit()
        app_id = cursor.lastrowid

    record = {
        "id": app_id,
        "company": company.strip(),
        "role": role.strip(),
        "application_date": application_date.strip(),
        "status": clean_status,
        "notes": notes.strip()
    }

    return {
        "success": True,
        "message": f"Application recorded successfully with ID {app_id}.",
        "application": record
    }


def get_applications(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve all tracked applications ordered by ID descending.
    """
    _ensure_table()
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, company, role, application_date, status, notes, created_at FROM applications ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


if __name__ == "__main__":
    res = save_application("Zoho Corporation", "Junior Data Analyst", notes="Test save from MCP tool")
    print("Saved application:", res)
    print("Total tracked:", len(get_applications()))

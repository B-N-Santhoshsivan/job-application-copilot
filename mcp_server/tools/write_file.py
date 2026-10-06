"""
MCP Tool: write_file
Safely saves generated documents (such as cover letters, interview sheets, and reports)
to the local outputs/ directory.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_file(filename: str, content: str) -> Dict[str, Any]:
    """
    Save generated text content to a designated file in outputs/.

    Args:
        filename: Destination filename (e.g. 'Santhosh_Sivan_Zoho_cover_letter.txt')
        content: Text content to write into the file

    Returns:
        Dictionary with status, filepath, and metadata.
    """
    # Sanitize filename - strip path traversal characters
    safe_name = os.path.basename(filename.strip().replace("..", "").replace("/", "_").replace("\\", "_"))
    if not safe_name:
        safe_name = f"document_{int(datetime.now().timestamp())}.txt"

    file_path = OUTPUT_DIR / safe_name
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return {
        "success": True,
        "filename": safe_name,
        "filepath": str(file_path),
        "bytes_written": len(content.encode("utf-8")),
        "message": f"Successfully wrote {len(content)} characters to {safe_name}."
    }


def read_output_file(filename: str) -> str:
    """
    Helper to read back a saved file from outputs/.
    """
    safe_name = os.path.basename(filename.strip())
    file_path = OUTPUT_DIR / safe_name
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


if __name__ == "__main__":
    res = write_file("test_mcp.txt", "Hello from MCP write_file tool!")
    print("Write file test:", res)

import csv
import re
import warnings
from pathlib import Path

from pypdf import PdfReader

BASE = Path(__file__).resolve().parent
STOP = {"the", "and", "for", "with", "that", "this", "are", "has", "have",
        "pending", "is", "to", "of", "in"}


# ---------- Notes: reading TXT / DOCX ----------
def _docx_to_text(path):
    """Convert a .docx note into the same '## Heading' text format as the .txt notes."""
    try:
        from docx import Document
    except ImportError:
        warnings.warn(f"python-docx is not installed; skipping {path.name}")
        return ""
    lines = []
    for p in Document(str(path)).paragraphs:
        text = p.text.strip()
        if not text:
            continue
        if p.style is not None and p.style.name.lower().startswith("heading"):
            lines.append(f"## {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def _read_note_file(path):
    if path.suffix.lower() == ".docx":
        return _docx_to_text(path)
    return path.read_text(encoding="utf-8")


# ---------- Notes: chunking + search ----------
def load_chunks(folder="meeting_notes"):
    """Split every note file into sections; each chunk carries its metadata."""
    folder_path = BASE / folder
    files = sorted(list(folder_path.glob("*.txt")) + list(folder_path.glob("*.docx")))
    chunks = []
    for f in files:
        if f.name.startswith("~$"):          # Word temp/lock file
            continue
        text = _read_note_file(f)
        pid = re.search(r"Project:\s*(\S+)", text)
        dt = re.search(r"Date:\s*(\S+)", text)
        for part in re.split(r"^## ", text, flags=re.M)[1:]:
            title, _, body = part.partition("\n")
            chunks.append({
                "project_id": pid.group(1) if pid else None,
                "meeting_date": dt.group(1) if dt else None,
                "doc": f.name,
                "section": title.strip(),
                "text": body.strip(),
            })
    return chunks


def list_meetings(project_id):
    """Previous meetings for a project as a sorted list of (meeting_date, doc)."""
    seen = {}
    for c in load_chunks():
        if c["project_id"] == project_id:
            seen[c["doc"]] = c["meeting_date"]
    return sorted((date, doc) for doc, date in seen.items())


def search_notes(project_id, query="", meeting_date=None):
    """Find note chunks for one project (optionally one meeting) matching the query."""
    chunks = [c for c in load_chunks() if c["project_id"] == project_id]
    if not chunks:
        return {"found": False,
                "message": f"No notes for {project_id}; proceeding with tracker.",
                "results": []}
    if meeting_date and meeting_date != "all":
        chunks = [c for c in chunks if c["meeting_date"] == meeting_date]
        if not chunks:
            return {"found": False,
                    "message": f"No notes for {project_id} on {meeting_date}; proceeding with tracker.",
                    "results": []}
    words = {w for w in re.findall(r"\w+", query.lower())
             if len(w) > 2 and w not in STOP}
    hits = [c for c in chunks
            if not words or words & set(re.findall(r"\w+", c["text"].lower()))]
    return {"found": bool(hits),
            "message": "" if hits else "No matching notes.",
            "results": hits}


# ---------- CSV tools (read-only) ----------
def _read(name):
    path = BASE / name
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def get_pending_actions(project_id, include_done=False):
    pid = project_id.strip().upper()
    rows = [r for r in _read("action_tracker.csv")
            if r["project_id"].strip().upper() == pid]
    if not include_done:
        rows = [r for r in rows if r["status"].strip().lower() != "done"]
    return rows


def get_project_updates(project_id, from_date=None, to_date=None):
    pid = project_id.strip().upper()
    rows = [r for r in _read("project_updates.csv")
            if r["project_id"].strip().upper() == pid]
    if from_date:
        rows = [r for r in rows if r["date"] >= from_date]
    if to_date:
        rows = [r for r in rows if r["date"] <= to_date]
    return rows


# ---------- Guidelines PDF (indexed by section so it can be cited) ----------
def get_meeting_guidelines():
    """Full guideline text (kept for convenience)."""
    pdf_path = BASE / "meeting_guidelines.pdf"
    if not pdf_path.exists():
        return "Meeting guidelines PDF is missing."
    reader = PdfReader(str(pdf_path))
    pages = [p.extract_text().strip() for p in reader.pages if p.extract_text()]
    return "\n".join(pages) if pages else "No readable text found in guidelines PDF."


def load_guideline_chunks():
    """Split the guidelines PDF into numbered sections: '1. Agenda Structure', ..."""
    pdf_path = BASE / "meeting_guidelines.pdf"
    if not pdf_path.exists():
        return []
    reader = PdfReader(str(pdf_path))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    parts = re.split(r"^\s*(\d+)\.\s+(.+)$", text, flags=re.M)
    chunks = []
    for i in range(1, len(parts) - 2, 3):
        chunks.append({
            "doc": pdf_path.name,
            "section": f"{parts[i]}. {parts[i + 1].strip()}",
            "text": " ".join(parts[i + 2].split()),
        })
    return chunks


def get_guideline(keyword):
    """Return the guideline section whose title contains the keyword, or None."""
    for c in load_guideline_chunks():
        if keyword.lower() in c["section"].lower():
            return c
    return None

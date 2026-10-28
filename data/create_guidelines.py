from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

BASE_DIR = Path(__file__).resolve().parent
pdf_path = BASE_DIR / "meeting_guidelines.pdf"

doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
styles = getSampleStyleSheet()

content = [
    Paragraph("Meeting Preparation Guidelines", styles["Title"]),
    Spacer(1, 16),

    Paragraph("1. Agenda Structure", styles["Heading2"]),
    Paragraph(
        "Start with high-priority and overdue actions. "
        "Include the action description, owner, status, and due date.",
        styles["BodyText"]
    ),
    Spacer(1, 10),

    Paragraph("2. Time Boxes", styles["Heading2"]),
    Paragraph(
        "Allocate 10 minutes per agenda item. "
        "Never exceed the available meeting duration. "
        "Defer lower-priority items when time is insufficient.",
        styles["BodyText"]
    ),
    Spacer(1, 10),

    Paragraph("3. Decision Logging", styles["Heading2"]),
    Paragraph(
        "Record decisions only when supported by the source notes. "
        "Do not invent decisions or attendees.",
        styles["BodyText"]
    ),
    Spacer(1, 10),

    Paragraph("4. Conflicting Sources", styles["Heading2"]),
    Paragraph(
        "If meeting notes say an action is complete but the tracker "
        "says Open, flag the discrepancy. Never change tracker status "
        "automatically.",
        styles["BodyText"]
    ),
    Spacer(1, 10),

    Paragraph("5. Missing Notes", styles["Heading2"]),
    Paragraph(
        "If meeting notes are missing, state this clearly and prepare "
        "the brief using available project updates and the action tracker.",
        styles["BodyText"]
    ),
]

doc.build(content)
print(f"Guidelines PDF created: {pdf_path}")
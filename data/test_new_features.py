import pytest

import retriever
from agent_tools import allocate_agenda_time, prioritise_agenda_items
from app import apply_edit, build_brief, needs_meeting_choice
from retriever import (get_pending_actions, get_project_updates, list_meetings,
                       load_chunks, load_guideline_chunks)

DATE = "2026-10-28"


def _state(**extra):
    return {"project_id": "PRJ-7", "meeting_date": DATE, "objective": "Review status",
            "duration": 30, "exclude_done": True, **extra}


def test_missing_notes_brief_still_built(tmp_path, monkeypatch):
    (tmp_path / "action_tracker.csv").write_text(
        "action_id,project_id,description,owner,due_date,priority,status\n"
        "B-1,PRJ-9,Write spec,Asha,2026-10-20,High,Open\n", encoding="utf-8")
    (tmp_path / "project_updates.csv").write_text(
        "project_id,date,update,blocker\n", encoding="utf-8")
    monkeypatch.setattr(retriever, "BASE", tmp_path)
    brief = build_brief(_state(project_id="PRJ-9"))
    assert "No notes" in brief["notes_message"]
    assert [i["action_ids"] for i in brief["agenda"]] == [["B-1"]]


def test_last_item_is_shortened_not_skipped():
    items = prioritise_agenda_items(get_pending_actions("PRJ-7"),
                                    get_project_updates("PRJ-7"), DATE)
    plan = allocate_agenda_time(items, 25)
    assert [i["minutes"] for i in plan["agenda"]] == [10, 10, 5]
    assert "shortened" in plan["agenda"][-1]["note"]


def test_multiple_meetings_need_a_choice():
    assert len(list_meetings("PRJ-7")) == 2
    state = _state()
    assert needs_meeting_choice(state) is True
    assert apply_edit(state, "use 2026-10-20 meeting")
    assert state["previous_meeting"] == "2026-10-20"
    assert needs_meeting_choice(state) is False


def test_selected_meeting_limits_notes_and_conflicts():
    old = build_brief(_state(previous_meeting="2026-10-20"))
    assert old["conflicts"] == []
    assert {n["doc"] for n in old["notes_used"]} == {"notes_2026-10-20.txt"}
    both = build_brief(_state(previous_meeting="all"))
    assert [c["action_id"] for c in both["conflicts"]] == ["A-18"]


def test_guideline_sections_loaded():
    sections = [g["section"] for g in load_guideline_chunks()]
    assert sections[0] == "1. Agenda Structure"
    assert len(sections) == 5


def test_brief_cites_guidelines_and_notes():
    brief = build_brief(_state(previous_meeting="all"))
    titles = [g["section"] for g in brief["guidelines"]]
    assert "2. Time Boxes" in titles and "4. Conflicting Sources" in titles
    assert "meeting_guidelines.pdf" in brief["sources"]
    assert all(n["doc"] and n["section"] and n["meeting_date"] for n in brief["notes_used"])


def test_docx_notes_are_read(tmp_path, monkeypatch):
    docx = pytest.importorskip("docx")
    folder = tmp_path / "meeting_notes"
    folder.mkdir()
    d = docx.Document()
    d.add_paragraph("Project: PRJ-5")
    d.add_paragraph("Date: 2026-10-15")
    d.add_heading("Decisions", level=2)
    d.add_paragraph("Ship the beta on Friday.")
    d.save(str(folder / "notes_2026-10-15.docx"))
    monkeypatch.setattr(retriever, "BASE", tmp_path)
    assert load_chunks() == [{"project_id": "PRJ-5", "meeting_date": "2026-10-15",
                              "doc": "notes_2026-10-15.docx", "section": "Decisions",
                              "text": "Ship the beta on Friday."}]
import pytest

import agent_tools
from agent_tools import (prioritise_agenda_items, allocate_agenda_time,
                         detect_conflicts, save_meeting_brief)
from retriever import get_pending_actions, get_project_updates, load_chunks, search_notes
from app import check_guardrails, validate, apply_edit

DATE = "2026-10-28"


def _items(duration_actions=None):
    actions = duration_actions or get_pending_actions("PRJ-7")
    return prioritise_agenda_items(actions, get_project_updates("PRJ-7"), DATE)


# 1. Missing notes
def test_missing_notes():
    result = search_notes("PRJ-9")
    assert result["found"] is False
    assert "No notes" in result["message"]


# 2. Completed actions excluded by default, included on request
def test_completed_actions_excluded():
    default = get_pending_actions("PRJ-7")
    assert all(a["status"].lower() != "done" for a in default)
    everything = get_pending_actions("PRJ-7", include_done=True)
    assert any(a["status"].lower() == "done" for a in everything)


# 3. Conflicting status is flagged, not silently resolved
def test_conflict_flagged():
    all_actions = get_pending_actions("PRJ-7", include_done=True)
    chunks = [c for c in load_chunks() if c["project_id"] == "PRJ-7"]
    conflicts = detect_conflicts(all_actions, chunks)
    assert {c["action_id"] for c in conflicts} == {"A-18"}
    assert conflicts[0]["tracker_status"] == "Open"
    assert "notes_2026-10-26.txt" in conflicts[0]["source"]


# 4. Duplicate topics are merged
def test_duplicate_topics_merged():
    a = {"action_id": "X-1", "description": "Fix API", "priority": "High",
         "due_date": "2026-11-01", "owner": "Sam", "status": "Open"}
    b = {**a, "action_id": "X-2"}
    items = prioritise_agenda_items([a, b], [], DATE)
    assert len(items) == 1
    assert items[0]["action_ids"] == ["X-1", "X-2"]


# 5. Insufficient time: never overrun, defer low priority, explain
@pytest.mark.parametrize("minutes", [5, 10, 20, 30, 60])
def test_time_budget_never_exceeded(minutes):
    plan = allocate_agenda_time(_items(), minutes)
    assert sum(i["minutes"] for i in plan["agenda"]) <= minutes


def test_low_priority_deferred_with_reason():
    plan = allocate_agenda_time(_items(), 20)
    assert plan["deferred"]
    assert all(d["reason"] for d in plan["deferred"])
    scheduled = [i["action_ids"][0] for i in plan["agenda"]]
    assert scheduled[0] == "A-18"          # blocker first
    assert "A-20" not in scheduled         # low priority is deferred


# 6. Send invite is declined
def test_send_invite_declined():
    assert "can't send invitations" in check_guardrails("Send the invite")


def test_status_change_declined():
    assert check_guardrails("Mark A-12 as done") is not None


def test_normal_edit_not_blocked():
    assert check_guardrails("remove completed actions") is None


# Ordering rule: blockers -> overdue -> priority
def test_blocker_first_then_overdue():
    ids = [i["action_ids"][0] for i in _items()]
    assert ids[0] == "A-18"
    assert ids.index("A-12") < ids.index("A-20")


# Validation
def test_validation():
    assert validate({"project_id": "PRJ-7", "meeting_date": "28-10-2026", "duration": "30"})[0] == "meeting_date"
    assert validate({"project_id": "PRJ-7", "meeting_date": DATE, "duration": "0"})[0] == "duration"
    assert validate({"project_id": "PRJ-9", "meeting_date": DATE, "duration": "30"})[0] == "project_id"
    assert validate({"project_id": "prj-7", "meeting_date": DATE, "duration": "30"}) is None


# Memory edits
def test_apply_edit():
    state = {"duration": 30, "exclude_done": False}
    assert apply_edit(state, "reduce to 20 minutes")
    assert state["duration"] == 20
    assert apply_edit(state, "remove completed actions")
    assert state["exclude_done"] is True
    assert not apply_edit(state, "hello")


# Saving: duplicate-safe and never changes records
def test_save_is_idempotent_and_read_only(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_tools, "BASE", tmp_path)
    before = (agent_tools.Path(__file__).parent / "action_tracker.csv").read_bytes()
    plan = allocate_agenda_time(_items(), 30)
    brief = {**plan, "project_id": "PRJ-7", "meeting_date": DATE,
             "objective": "Review", "conflicts": [], "sources": ["action_tracker.csv"]}
    first = save_meeting_brief(brief)
    second = save_meeting_brief(brief)
    assert first["created"] is True and second["created"] is False
    assert first["brief_id"] == second["brief_id"]
    after = (agent_tools.Path(__file__).parent / "action_tracker.csv").read_bytes()
    assert before == after
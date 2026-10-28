import re
from datetime import date

from retriever import (get_guideline, get_pending_actions, get_project_updates,
                       list_meetings, load_chunks, search_notes)
from agent_tools import (prioritise_agenda_items, allocate_agenda_time,
                         detect_conflicts, save_meeting_brief)

INVITE = re.compile(r"\binvit", re.I)
SEND = re.compile(r"\b(send|email|mail|schedule|book|create)\b", re.I)
TRACKER_EDIT = re.compile(r"\b(mark|change|update|edit|set)\b.*\b(status|done|complete\w*)\b", re.I)

REQUIRED = ["project_id", "meeting_date", "objective", "duration"]
PROMPTS = {
    "project_id": "Project ID (e.g. PRJ-7): ",
    "meeting_date": "Meeting date (YYYY-MM-DD): ",
    "objective": "Meeting objective: ",
    "duration": "Available minutes: ",
}


# ---------- Guardrails ----------
def check_guardrails(text):
    if INVITE.search(text) and SEND.search(text):
        return "I can't send invitations. I can only prepare a meeting brief."
    if TRACKER_EDIT.search(text):
        return ("I can't change the tracker or any action status. "
                "I can only flag discrepancies in the brief.")
    return None


# ---------- Validation ----------
def validate(state):
    """Returns (field, message) if something is invalid, else None."""
    try:
        date.fromisoformat(state["meeting_date"])
    except ValueError:
        return "meeting_date", "Enter the date as YYYY-MM-DD (e.g. 2026-10-28)."
    try:
        state["duration"] = int(state["duration"])
        if state["duration"] <= 0:
            raise ValueError
    except ValueError:
        return "duration", "Minutes must be a positive whole number."
    pid = state["project_id"].strip().upper()
    if not get_pending_actions(pid, include_done=True):
        return "project_id", f"Project {pid} was not found in the action tracker."
    state["project_id"] = pid
    return None


# ---------- Which previous meeting? ----------
def needs_meeting_choice(state):
    """True when several previous meetings exist and the user has not picked one."""
    return len(list_meetings(state["project_id"])) > 1 and not state.get("previous_meeting")


def meeting_choice_is_valid(state, choice):
    dates = [d for d, _ in list_meetings(state["project_id"])]
    return choice == "all" or choice in dates


# ---------- Brief building ----------
def build_brief(state):
    pid = state["project_id"]
    meeting = state.get("previous_meeting")          # None, "all" or a date
    actions = get_pending_actions(pid, include_done=not state.get("exclude_done", True))
    all_actions = get_pending_actions(pid, include_done=True)
    updates = get_project_updates(pid)

    # retrieve -> grade -> bounded rewrite (only once)
    notes = search_notes(pid, " ".join(a["description"] for a in actions), meeting)
    if not notes["found"]:
        notes = search_notes(pid, state["objective"], meeting)

    project_chunks = [c for c in load_chunks() if c["project_id"] == pid]
    selected = [c for c in project_chunks
                if meeting in (None, "all") or c["meeting_date"] == meeting]

    items = prioritise_agenda_items(actions, updates, state["meeting_date"])
    plan = allocate_agenda_time(items, state["duration"])
    conflicts = detect_conflicts(all_actions, selected)

    # which guideline sections were applied (cited from the PDF)
    wanted = ["Agenda Structure", "Time Boxes"]
    if notes["results"]:
        wanted.append("Decision Logging")
    if conflicts:
        wanted.append("Conflicting Sources")
    if not project_chunks:
        wanted.append("Missing Notes")
    guidelines = [g for g in (get_guideline(k) for k in wanted) if g]

    return {
        **plan,
        "project_id": pid,
        "meeting_date": state["meeting_date"],
        "objective": state["objective"],
        "duration": state["duration"],
        "conflicts": conflicts,
        "notes_used": notes["results"],
        "notes_message": notes["message"],
        "guidelines": guidelines,
        "sources": ["action_tracker.csv", "project_updates.csv"]
                   + sorted({c["doc"] for c in selected})
                   + (["meeting_guidelines.pdf"] if guidelines else []),
    }


# ---------- Memory: user edits ----------
def apply_edit(state, text):
    low = text.lower()
    changed = False
    m = re.search(r"(\d+)\s*min", low)
    if m:
        state["duration"] = int(m.group(1))
        changed = True
    if re.search(r"(remove|exclude|hide)", low) and re.search(r"(complet|done)", low):
        state["exclude_done"] = True
        changed = True
    if re.search(r"(include|show)", low) and re.search(r"(complet|done)", low):
        state["exclude_done"] = False
        changed = True
    d = re.search(r"\d{4}-\d{2}-\d{2}", low)
    if d and meeting_choice_is_valid(state, d.group(0)):
        state["previous_meeting"] = d.group(0)
        changed = True
    elif re.search(r"\ball\b.*\bmeetings?\b", low):
        state["previous_meeting"] = "all"
        changed = True
    return changed


# ---------- CLI ----------
def collect(state):
    while True:
        for k in REQUIRED:
            if not state.get(k):
                state[k] = input(PROMPTS[k]).strip()
        err = validate(state)
        if not err:
            return
        field, msg = err
        print(msg)
        state[field] = ""


def choose_meeting(state):
    if not needs_meeting_choice(state):
        return
    meetings = list_meetings(state["project_id"])
    print("\nMultiple previous meetings found:")
    for d, doc in meetings:
        print(f"- {d} ({doc})")
    while True:
        choice = input("Which meeting should I use? (enter a date or 'all'): ").strip().lower()
        if meeting_choice_is_valid(state, choice):
            state["previous_meeting"] = choice
            return
        print("Please enter one of the dates above, or 'all'.")


def print_brief(b):
    print(f"\n=== Meeting Brief: {b['project_id']} ({b['meeting_date']}, {b['duration']} min) ===")
    print("Objective:", b["objective"])
    print("(All items are proposals, not decisions.)")
    print("\n--- Agenda ---")
    for i in b["agenda"]:
        print(f"- {i['description']} ({i['minutes']} min) | owner: {i['owner']} | {', '.join(i['action_ids'])}{i.get('note', '')}")
    print("\n--- Deferred ---")
    for d in b["deferred"]:
        print(f"- {d['topic']}: {d['reason']}")
    if not b["deferred"]:
        print("None")
    print("\n--- Conflicts (notes vs tracker) ---")
    for c in b["conflicts"]:
        print(f"- {c['action_id']}: \"{c['note']}\" vs tracker {c['tracker_status']} [{c['source']}]")
    if not b["conflicts"]:
        print("None")
    print("\n--- Previous meeting notes ---")
    for n in b["notes_used"]:
        for line in n["text"].splitlines():
            print(f"- ({n['meeting_date']}) {line.strip('- ').strip()} [{n['doc']} > {n['section']}]")
    if b["notes_message"]:
        print("-", b["notes_message"])
    print("\n--- Guidelines applied ---")
    for g in b["guidelines"]:
        print(f"- {g['section']}: {g['text']} [{g['doc']}]")
    print("\nSources:", ", ".join(b["sources"]))


def main():
    state = {"exclude_done": True}
    first = input("What do you need? (e.g. 'Prepare brief for PRJ-7'): ")
    msg = check_guardrails(first)
    if msg:
        print(msg)
        return
    m = re.search(r"PRJ-\d+", first, re.I)
    if m:
        state["project_id"] = m.group(0).upper()
    collect(state)
    choose_meeting(state)

    while True:
        brief = build_brief(state)
        print_brief(brief)
        cmd = input("\nEdit (e.g. 'reduce to 20 minutes', 'remove completed actions', "
                    "'use 2026-10-26 meeting') or 'save' / 'quit': ").strip()
        low = cmd.lower()
        if low in ("quit", "exit"):
            return
        if low == "save":
            print(save_meeting_brief(brief))
            return
        msg = check_guardrails(cmd)
        if msg:
            print(msg)
        elif not apply_edit(state, cmd):
            print("Not understood. Try changing the minutes, removing completed actions, "
                  "or choosing a meeting date.")


if __name__ == "__main__":
    main()

import hashlib
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
RANK = {"high": 1, "medium": 2, "low": 3}

# Guidelines > "2. Time Boxes": 10 minutes per agenda item, never exceed the slot.
TIME_BOX = 10
MIN_SLOT = 5

DONE = re.compile(r"\b(done|completed|finished|finali[sz]ed)\b", re.I)
# "pending", "to be", "needs" etc. mean the work is not finished yet
NOT_DONE = re.compile(r"\b(not|yet|pending|still|to be|needs|should|required)\b", re.I)


def _words(text):
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) > 3}


# ---------- Prioritise ----------
def prioritise_agenda_items(actions, updates, meeting_date):
    """Order: blocker -> overdue -> priority -> due date. Duplicate topics merge."""
    blockers = [u for u in updates
                if u.get("blocker", "").strip().upper() in ("Y", "YES", "TRUE")]

    merged = {}
    for a in actions:
        key = a["description"].strip().casefold()
        if key in merged:
            merged[key]["action_ids"].append(a["action_id"])
        else:
            merged[key] = {**a, "action_ids": [a["action_id"]]}

    items = []
    for a in merged.values():
        a["has_blocker"] = any(
            _words(a["description"]) & _words(u["update"]) for u in blockers
        )
        a["overdue"] = a["due_date"] < meeting_date
        items.append(a)

    items.sort(key=lambda a: (
        not a["has_blocker"],
        not a["overdue"],
        RANK.get(a["priority"].lower(), 4),
        a["due_date"],
    ))
    return items


# ---------- Time allocation ----------
def allocate_agenda_time(items, available_minutes):
    """10-minute time boxes; the last item is shortened to fit; the rest are deferred."""
    agenda, deferred, left = [], [], available_minutes
    for it in items:
        if left >= MIN_SLOT:
            mins = min(TIME_BOX, left)
            note = f" [shortened from {TIME_BOX} min]" if mins < TIME_BOX else ""
            agenda.append({**it, "minutes": mins, "note": note})
            left -= mins
        else:
            deferred.append({
                "topic": it["description"],
                "action_ids": it["action_ids"],
                "reason": "No time left in the slot; ranked below the scheduled items.",
            })
    return {"agenda": agenda, "deferred": deferred, "unused_minutes": left}


# ---------- Conflicts ----------
def detect_conflicts(all_actions, chunks):
    """Notes vs tracker mismatch (both directions). Never picks a status."""
    out = []
    for a in all_actions:
        aw = _words(a["description"])
        tracker_done = a["status"].strip().lower() == "done"
        for c in chunks:
            for line in c["text"].splitlines():
                if not (aw & _words(line)):
                    continue
                notes_open = bool(NOT_DONE.search(line))
                notes_done = bool(DONE.search(line)) and not notes_open
                if (notes_done and not tracker_done) or (notes_open and tracker_done):
                    out.append({
                        "action_id": a["action_id"],
                        "tracker_status": a["status"],
                        "note": line.strip("- ").strip(),
                        "source": f'{c["doc"]} > {c["section"]}',
                        "warning": "Notes and tracker disagree. Confirm the real status.",
                    })
    return out


# ---------- Save brief (no record changes, duplicate-safe) ----------
def render_markdown(b):
    L = [f'# Meeting Brief: {b["project_id"]} ({b["meeting_date"]})',
         f'**Objective:** {b["objective"]}', "",
         "> All items below are proposals, not decisions.", "", "## Agenda"]
    for i in b["agenda"]:
        L.append(f'- {i["description"]} ({i["minutes"]} min) | owner: {i["owner"]} '
                 f'| {", ".join(i["action_ids"])}{i.get("note", "")}')
    L += ["", "## Deferred"]
    L += [f'- {d["topic"]}: {d["reason"]}' for d in b["deferred"]] or ["- None"]
    L += ["", "## Conflicts"]
    L += [f'- {c["action_id"]}: "{c["note"]}" vs tracker {c["tracker_status"]}. '
          f'{c["warning"]} [{c["source"]}]' for c in b["conflicts"]] or ["- None"]

    L += ["", "## Previous meeting notes"]
    for n in b.get("notes_used", []):
        for line in n["text"].splitlines():
            L.append(f'- ({n["meeting_date"]}) {line.strip("- ").strip()} '
                     f'[{n["doc"]} > {n["section"]}]')
    if b.get("notes_message"):
        L.append(f'- {b["notes_message"]}')
    if not b.get("notes_used") and not b.get("notes_message"):
        L.append("- None")

    L += ["", "## Guidelines applied"]
    L += [f'- {g["section"]}: {g["text"]} [{g["doc"]}]'
          for g in b.get("guidelines", [])] or ["- None"]

    L += ["", "## Sources"] + [f"- {s}" for s in b["sources"]]
    return "\n".join(L)


def save_meeting_brief(brief):
    body = render_markdown(brief)
    h = hashlib.sha1(body.encode("utf-8")).hexdigest()[:8]
    brief_id = f'BRIEF-{brief["project_id"]}-{brief["meeting_date"]}-{h}'
    out = BASE / "briefs"
    out.mkdir(exist_ok=True)
    path = out / f"{brief_id}.md"
    created = not path.exists()
    if created:
        path.write_text(body, encoding="utf-8")
    return {"brief_id": brief_id, "path": str(path), "created": created}

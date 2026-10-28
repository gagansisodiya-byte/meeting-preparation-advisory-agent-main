"""HTML pieces for the Streamlit app. Pure functions (no streamlit import), so they
can be tested on their own. Every HTML string is one line: Streamlit's markdown
treats indented lines as code blocks."""
import html

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&display=swap');
:root{--rs-ink:#17212B;--rs-paper:#F5F7F6;--rs-rule:#D5DCD9;--rs-soft:#E8EEEC;
--rs-teal:#0F766E;--rs-signal:#C2410C;--rs-amber:#A16207;--rs-mute:#5B6770;}
.stApp{background:var(--rs-paper);}
.block-container{padding-top:2.2rem;max-width:1100px;}
.rs-head{border-top:6px solid var(--rs-ink);padding:14px 0 18px;margin-bottom:6px;color:var(--rs-ink);}
.rs-proj{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:2.4rem;line-height:1.05;letter-spacing:-.02em;margin:0;}
.rs-obj{font-size:1.15rem;margin:.35rem 0 0;max-width:62ch;}
.rs-facts{display:flex;flex-wrap:wrap;gap:6px 22px;margin-top:10px;color:var(--rs-mute);font-size:.95rem;}
.rs-facts b{color:var(--rs-ink);font-weight:600;}
.rs-pill{display:inline-block;border:1px solid var(--rs-ink);border-radius:4px;padding:1px 8px;font-size:.82rem;color:var(--rs-ink);margin-left:12px;vertical-align:middle;font-family:'Source Sans Pro','Source Sans 3',sans-serif;font-weight:600;letter-spacing:0;}
.rs-sec{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.25rem;color:var(--rs-ink);margin:26px 0 8px;}
.rs-sub{color:var(--rs-mute);font-size:.92rem;margin:-4px 0 10px;max-width:70ch;}
.rs-bar{display:flex;height:46px;border:1.5px solid var(--rs-ink);border-radius:6px;overflow:hidden;background:#fff;}
.rs-seg{display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:.95rem;border-right:2px solid var(--rs-paper);min-width:0;overflow:hidden;white-space:nowrap;}
.rs-seg:last-child{border-right:0;}
.rs-seg.regular{background:var(--rs-teal);}
.rs-seg.overdue{background:var(--rs-amber);}
.rs-seg.blocker{background:var(--rs-signal);}
.rs-seg.free{background:repeating-linear-gradient(135deg,#fff 0 7px,var(--rs-soft) 7px 14px);color:var(--rs-mute);font-weight:600;}
.rs-axis{display:flex;justify-content:space-between;color:var(--rs-mute);font-size:.85rem;margin-top:4px;}
.rs-legend{display:flex;flex-wrap:wrap;gap:4px 18px;margin-top:8px;font-size:.9rem;color:var(--rs-ink);}
.rs-key{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:6px;vertical-align:-1px;}
.rs-key.regular{background:var(--rs-teal);}.rs-key.overdue{background:var(--rs-amber);}.rs-key.blocker{background:var(--rs-signal);}
.rs-row{display:grid;grid-template-columns:64px 1fr auto;gap:6px 16px;padding:14px 0;border-top:1px solid var(--rs-rule);align-items:start;color:var(--rs-ink);}
.rs-row:last-child{border-bottom:1px solid var(--rs-rule);}
.rs-t{font-variant-numeric:tabular-nums;font-weight:700;font-size:1.05rem;border-left:4px solid var(--rs-teal);padding-left:10px;line-height:1.35;}
.rs-row.overdue .rs-t{border-color:var(--rs-amber);}.rs-row.blocker .rs-t{border-color:var(--rs-signal);}
.rs-title{font-weight:600;font-size:1.08rem;line-height:1.3;}
.rs-meta{display:flex;flex-wrap:wrap;gap:2px 16px;color:var(--rs-mute);font-size:.9rem;margin-top:3px;}
.rs-meta b{color:var(--rs-ink);font-weight:600;}
.rs-tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;}
.rs-tag{border-radius:4px;padding:1px 8px;font-size:.8rem;font-weight:600;border:1px solid currentColor;white-space:nowrap;}
.rs-tag.blocker{color:var(--rs-signal);}.rs-tag.overdue{color:var(--rs-amber);}.rs-tag.cut{color:var(--rs-mute);}
.rs-dur{font-variant-numeric:tabular-nums;font-weight:700;white-space:nowrap;}
.rs-row.off{opacity:.78;}.rs-row.off .rs-t{border-color:var(--rs-rule);color:var(--rs-mute);}
.rs-alert{border:1.5px solid var(--rs-signal);border-left-width:8px;border-radius:6px;background:#fff;padding:14px 18px;margin:16px 0 4px;color:var(--rs-ink);}
.rs-alert h4{font-family:'Bricolage Grotesque',sans-serif;margin:0 0 2px;font-size:1.15rem;color:var(--rs-signal);}
.rs-alert .rs-id{font-weight:700;}
.rs-vs{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0 4px;}
.rs-side{background:var(--rs-paper);border-radius:4px;padding:8px 12px;font-size:.95rem;}
.rs-side small{display:block;color:var(--rs-mute);font-size:.8rem;margin-bottom:2px;}
.rs-ok{border:1px solid var(--rs-rule);border-radius:6px;background:#fff;padding:10px 16px;color:var(--rs-ink);margin-top:14px;}
.rs-src{display:inline-block;background:var(--rs-soft);border-radius:4px;padding:0 7px;font-size:.8rem;color:var(--rs-mute);margin-left:6px;white-space:nowrap;}
.rs-note{padding:9px 0;border-top:1px solid var(--rs-rule);color:var(--rs-ink);}
.rs-note:last-child{border-bottom:1px solid var(--rs-rule);}
.rs-note small{color:var(--rs-mute);margin-right:8px;font-variant-numeric:tabular-nums;}
.rs-guide{padding:11px 0;border-top:1px solid var(--rs-rule);color:var(--rs-ink);}
.rs-guide:last-child{border-bottom:1px solid var(--rs-rule);}
.rs-guide b{font-family:'Bricolage Grotesque',sans-serif;font-size:1.02rem;}
.rs-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:22px;margin-top:18px;color:var(--rs-ink);}
.rs-step{border-top:3px solid var(--rs-ink);padding-top:8px;}
.rs-step b{font-family:'Bricolage Grotesque',sans-serif;font-size:1.1rem;display:block;}
@media (max-width:640px){.rs-row{grid-template-columns:52px 1fr;}.rs-tags,.rs-dur{grid-column:2;justify-content:flex-start;}.rs-vs{grid-template-columns:1fr;}.rs-proj{font-size:1.9rem;}}
</style>"""


def esc(value):
    return html.escape(str(value), quote=True)


def kind(item):
    return "blocker" if item.get("has_blocker") else "overdue" if item.get("overdue") else "regular"


def clock(minutes):
    return f"{minutes // 60}:{minutes % 60:02d}"


# ---------- header ----------
def header_html(b):
    meetings = b.get("meeting_label", "")
    facts = (f'<span><b>{esc(b["meeting_date"])}</b> meeting date</span>'
             f'<span><b>{b["duration"]} min</b> available</span>'
             f'<span><b>{len(b["agenda"])}</b> on the agenda</span>'
             f'<span><b>{len(b["deferred"])}</b> deferred</span>')
    if meetings:
        facts += f'<span>notes from <b>{esc(meetings)}</b></span>'
    return (f'<div class="rs-head"><h1 class="rs-proj">{esc(b["project_id"])}'
            f'<span class="rs-pill">Proposal, not a decision</span></h1>'
            f'<p class="rs-obj">{esc(b["objective"])}</p><div class="rs-facts">{facts}</div></div>')


# ---------- the minute bar ----------
def time_bar_html(b):
    total = max(b["duration"], 1)
    segs = ""
    for i in b["agenda"]:
        pct = i["minutes"] / total * 100
        segs += f'<div class="rs-seg {kind(i)}" style="width:{pct:.2f}%" title="{esc(i["description"])}">{i["minutes"]}</div>'
    free = b["unused_minutes"]
    if free > 0:
        segs += f'<div class="rs-seg free" style="width:{free / total * 100:.2f}%">{free} free</div>'
    axis = f'<div class="rs-axis"><span>0:00</span><span>{clock(total)}</span></div>'
    legend = ('<div class="rs-legend"><span><i class="rs-key blocker"></i>Blocked by an open issue</span>'
              '<span><i class="rs-key overdue"></i>Overdue</span>'
              '<span><i class="rs-key regular"></i>On track</span></div>')
    return (f'<div class="rs-sec">How the {total} minutes are used</div>'
            f'<div class="rs-bar">{segs}</div>{axis}{legend}')


# ---------- run sheet ----------
def run_sheet_html(b):
    if not b["agenda"]:
        return '<div class="rs-ok">Nothing fits in this slot. Add minutes or reduce the scope.</div>'
    rows, start = "", 0
    for i in b["agenda"]:
        k = kind(i)
        tags = ""
        if i.get("has_blocker"):
            tags += '<span class="rs-tag blocker">Blocker</span>'
        if i.get("overdue"):
            tags += '<span class="rs-tag overdue">Overdue</span>'
        if i.get("note"):
            tags += '<span class="rs-tag cut">Shortened</span>'
        meta = (f'<span>Owner <b>{esc(i["owner"])}</b></span>'
                f'<span>Due <b>{esc(i["due_date"])}</b></span>'
                f'<span>Priority <b>{esc(i["priority"])}</b></span>'
                f'<span>{esc(", ".join(i["action_ids"]))}</span>')
        rows += (f'<div class="rs-row {k}"><div class="rs-t">{clock(start)}</div>'
                 f'<div><div class="rs-title">{esc(i["description"])}</div><div class="rs-meta">{meta}</div></div>'
                 f'<div><div class="rs-dur">{i["minutes"]} min</div><div class="rs-tags">{tags}</div></div></div>')
        start += i["minutes"]
    return (f'<div class="rs-sec">Run sheet</div>'
            f'<div class="rs-sub">Times show minutes since the meeting starts. Order: blockers, then overdue, then priority.</div>{rows}')


def deferred_html(b):
    if not b["deferred"]:
        return ""
    rows = ""
    for d in b["deferred"]:
        rows += (f'<div class="rs-row off"><div class="rs-t">Off</div><div><div class="rs-title">{esc(d["topic"])}</div>'
                 f'<div class="rs-meta"><span>{esc(d["reason"])}</span></div></div>'
                 f'<div class="rs-dur">{esc(", ".join(d["action_ids"]))}</div></div>')
    return ('<div class="rs-sec">Left off this agenda</div>'
            '<div class="rs-sub">These ranked below the items above. Add minutes to bring them back.</div>' + rows)


# ---------- conflicts ----------
def conflicts_html(b):
    if not b["conflicts"]:
        return '<div class="rs-ok">Notes and tracker agree. No status conflicts found.</div>'
    out = ""
    for c in b["conflicts"]:
        out += (f'<div class="rs-alert"><h4>Resolve before the meeting</h4>'
                f'<span class="rs-id">{esc(c["action_id"])}</span> has two different statuses. Neither has been changed.'
                f'<div class="rs-vs"><div class="rs-side"><small>Action tracker</small><b>{esc(c["tracker_status"])}</b></div>'
                f'<div class="rs-side"><small>Meeting notes</small>&ldquo;{esc(c["note"])}&rdquo;'
                f'<span class="rs-src">{esc(c["source"])}</span></div></div></div>')



# ---------- run sheet ----------
def run_sheet_html(b):
    if not b["agenda"]:
        return '<div class="rs-ok">Nothing fits in this slot. Add minutes or reduce the scope.</div>'
    rows, start = "", 0
    for i in b["agenda"]:
        k = kind(i)
        tags = ""
        if i.get("has_blocker"):
            tags += '<span class="rs-tag blocker">Blocker</span>'
        if i.get("overdue"):
            tags += '<span class="rs-tag overdue">Overdue</span>'
        if i.get("note"):
            tags += '<span class="rs-tag cut">Shortened</span>'
        meta = (f'<span>Owner <b>{esc(i["owner"])}</b></span>'
                f'<span>Due <b>{esc(i["due_date"])}</b></span>'
                f'<span>Priority <b>{esc(i["priority"])}</b></span>'
                f'<span>{esc(", ".join(i["action_ids"]))}</span>')
        rows += (f'<div class="rs-row {k}"><div class="rs-t">{clock(start)}</div>'
                 f'<div><div class="rs-title">{esc(i["description"])}</div><div class="rs-meta">{meta}</div></div>'
                 f'<div><div class="rs-dur">{i["minutes"]} min</div><div class="rs-tags">{tags}</div></div></div>')
        start += i["minutes"]
    return (f'<div class="rs-sec">Run sheet</div>'
            f'<div class="rs-sub">Times show minutes since the meeting starts. Order: blockers, then overdue, then priority.</div>{rows}')


def deferred_html(b):
    if not b["deferred"]:
        return ""
    rows = ""
    for d in b["deferred"]:
        rows += (f'<div class="rs-row off"><div class="rs-t">Off</div><div><div class="rs-title">{esc(d["topic"])}</div>'
                 f'<div class="rs-meta"><span>{esc(d["reason"])}</span></div></div>'
                 f'<div class="rs-dur">{esc(", ".join(d["action_ids"]))}</div></div>')
    return ('<div class="rs-sec">Left off this agenda</div>'
            '<div class="rs-sub">These ranked below the items above. Add minutes to bring them back.</div>' + rows)


# ---------- conflicts ----------
def conflicts_html(b):
    if not b["conflicts"]:
        return '<div class="rs-ok">Notes and tracker agree. No status conflicts found.</div>'
    out = ""
    for c in b["conflicts"]:
        out += (f'<div class="rs-alert"><h4>Resolve before the meeting</h4>'
                f'<span class="rs-id">{esc(c["action_id"])}</span> has two different statuses. Neither has been changed.'
                f'<div class="rs-vs"><div class="rs-side"><small>Action tracker</small><b>{esc(c["tracker_status"])}</b></div>'
                f'<div class="rs-side"><small>Meeting notes</small>&ldquo;{esc(c["note"])}&rdquo;'
                f'<span class="rs-src">{esc(c["source"])}</span></div></div></div>')
    return out


# ---------- notes and guidelines ----------
def notes_html(b):
    if not b["notes_used"] and not b["notes_message"]:
        return '<div class="rs-ok">No notes used.</div>'
    out = ""
    for n in b["notes_used"]:
        for line in n["text"].splitlines():
            line = line.strip("- ").strip()
            if line:
                out += (f'<div class="rs-note"><small>{esc(n["meeting_date"])}</small>{esc(line)}'
                        f'<span class="rs-src">{esc(n["doc"])} &gt; {esc(n["section"])}</span></div>')
    if b["notes_message"]:
        out += f'<div class="rs-ok">{esc(b["notes_message"])}</div>'
    return out


def guidelines_html(b):
    if not b["guidelines"]:
        return '<div class="rs-ok">No guideline sections applied.</div>'
    return "".join(
        f'<div class="rs-guide"><b>{esc(g["section"])}</b><span class="rs-src">{esc(g["doc"])}</span><br>{esc(g["text"])}</div>'
        for g in b["guidelines"])


# ---------- empty state ----------
def landing_html():
    steps = [("Describe the meeting", "Project, date, objective and how many minutes you have."),
             ("Review the run sheet", "Blockers come first, then overdue work. Whatever does not fit is left off, with the reason."),
             ("Check the flags", "If notes say done but the tracker says open, you see both. Nothing is changed for you.")]
    body = "".join(f'<div class="rs-step"><b>{n}. {esc(t)}</b>{esc(d)}</div>'
                   for n, (t, d) in enumerate(steps, 1))
    return ('<div class="rs-head"><h1 class="rs-proj">Meeting prep, sourced</h1>'
            '<p class="rs-obj">Fill in the meeting details on the left to get a brief with a time-boxed agenda '
            'and a citation for every note.</p></div>'
            f'<div class="rs-steps">{body}</div>')        
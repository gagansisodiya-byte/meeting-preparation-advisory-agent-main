import streamlit as st

import ui_components as ui
from agent_tools import render_markdown, save_meeting_brief
from app import apply_edit, build_brief, check_guardrails, validate
from retriever import list_meetings

st.set_page_config(page_title="Meeting Preparation Advisory Agent", page_icon="📋", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)

st.session_state.setdefault("state", None)
st.session_state.setdefault("brief", None)
st.session_state.setdefault("last_cmd", "")


def _label(state):
    choice = state.get("previous_meeting")
    return "all meetings" if choice in (None, "all") else choice


# ---------- sidebar: meeting setup ----------
with st.sidebar:
    st.header("Meeting setup")
    project_id = st.text_input("Project ID", value="PRJ-7")
    meeting_date = st.date_input("Meeting date")
    duration = st.slider("Minutes available", min_value=5, max_value=180, value=30, step=5)
    objective = st.text_input("Objective", placeholder="e.g. Review project status")
    hide_done = st.toggle("Hide completed actions", value=True)

    meetings = list_meetings(project_id.strip().upper()) if project_id.strip() else []
    previous = None
    if len(meetings) > 1:
        options = ["all"] + [d for d, _ in meetings]
        previous = st.selectbox("Which earlier meeting?", options,
                                format_func=lambda v: "All meetings" if v == "all" else v)
    elif len(meetings) == 1:
        previous = meetings[0][0]

    go = st.button("Prepare brief", type="primary")
    st.caption("This tool only reads your files. It never sends invitations or changes the tracker.")

if go:
    if not objective.strip():
        st.sidebar.error("Add a meeting objective.")
    else:
        state = {"project_id": project_id, "meeting_date": meeting_date.isoformat(),
                 "objective": objective.strip(), "duration": duration,
                 "exclude_done": hide_done, "previous_meeting": previous}
        problem = validate(state)
        if problem:
            st.sidebar.error(problem[1])
        else:
            st.session_state["state"] = state
            st.session_state["brief"] = build_brief(state)
            st.session_state["last_cmd"] = ""

# ---------- adjust with plain words (edit memory) ----------
notice = None
state = st.session_state["state"]
cmd = (st.session_state.get("cmd") or "").strip()
if state and cmd and cmd != st.session_state["last_cmd"]:
    st.session_state["last_cmd"] = cmd
    declined = check_guardrails(cmd)
    if declined:
        notice = ("warning", declined)
    elif apply_edit(state, cmd):
        st.session_state["brief"] = build_brief(state)
        notice = ("success", "Brief updated.")
    else:
        notice = ("info", "Not understood. Try a number of minutes, 'remove completed actions' "
                          "or 'use 2026-10-20 meeting'.")

brief = st.session_state["brief"]

if not brief:
    st.markdown(ui.landing_html(), unsafe_allow_html=True)
else:
    brief["meeting_label"] = _label(st.session_state["state"])
    st.markdown(ui.header_html(brief), unsafe_allow_html=True)
    st.markdown(ui.time_bar_html(brief), unsafe_allow_html=True)

    st.text_input("Adjust the brief", key="cmd",
                  placeholder="reduce to 20 minutes, remove completed actions, use 2026-10-20 meeting")
    if notice:
        getattr(st, notice[0])(notice[1])

    agenda_tab, flags_tab, notes_tab, guide_tab, file_tab = st.tabs(
        ["Agenda", f"Flags ({len(brief['conflicts'])})", "Earlier notes", "Guidelines", "Brief file"])

    with agenda_tab:
        st.markdown(ui.run_sheet_html(brief) + ui.deferred_html(brief), unsafe_allow_html=True)
    with flags_tab:
        st.markdown(ui.conflicts_html(brief), unsafe_allow_html=True)
    with notes_tab:
        st.markdown('<div class="rs-sub">Every line shows the file and section it came from.</div>'
                    + ui.notes_html(brief), unsafe_allow_html=True)
    with guide_tab:
        st.markdown('<div class="rs-sub">Sections of the guidelines PDF that shaped this brief.</div>'
                    + ui.guidelines_html(brief), unsafe_allow_html=True)
    with file_tab:
        markdown_text = render_markdown(brief)
        st.download_button("Download brief (.md)", data=markdown_text,
                           file_name=f"brief_{brief['project_id']}_{brief['meeting_date']}.md",
                           mime="text/markdown")
        if st.button("Save brief to briefs folder"):
            saved = save_meeting_brief(brief)
            st.success(f"{'Saved' if saved['created'] else 'Already saved'}: {saved['brief_id']}")
            st.code(saved["path"])
        st.markdown(markdown_text)
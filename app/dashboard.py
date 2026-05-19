"""gemini-rpa-agent dashboard."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gemini_rpa_agent.runner import ask  # noqa: E402


st.set_page_config(page_title="gemini-rpa-agent", layout="wide", page_icon=":robot_face:")
st.title("gemini-rpa-agent")
st.caption(
    "RPA / workflow-automation failure-diagnosis agent on Google Cloud "
    "Agent Builder (ADK) + Gemini 2.5, wired to an n8n-style RPA MCP "
    "server. Quotes the failing step error verbatim. Apache 2.0."
)

with st.sidebar:
    st.header("Diagnose a failed run")
    question = st.text_area(
        "Your question",
        value=(
            "Workflow wf-onboarding-pro-2026-001 had a failure at 09:14 "
            "UTC. Walk the RPA tools and tell me which step broke, the "
            "verbatim error payload, and how to fix it."
        ),
        height=160,
    )
    model = st.selectbox(
        "Gemini model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite"],
        index=0,
    )
    stub = st.toggle(
        "Use stub RPA MCP",
        value=True,
        help="On = local stub with canned workflows and runs. Off = real RPA orchestrator (set RPA_API_URL + RPA_API_TOKEN).",
    )
    run = st.button("Run diagnosis", type="primary", use_container_width=True)
    st.divider()
    st.caption(
        f"Project: `{os.getenv('GOOGLE_CLOUD_PROJECT', 'not-set')}`  "
        f"Vertex AI: `{os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'true')}`"
    )

st.markdown(
    """
The agent walks these RPA MCP tools end-to-end to diagnose a failed
workflow run:
- **list_workflows** to find the workflow whose last run failed
- **get_workflow_run** to pull the step-by-step trace
- **get_step_output** to grab the verbatim error payload from the failed step
- **suggest_retry** to fetch the canonical fix + retry command

The answer is five labeled sections: ANSWER, EVIDENCE, ROOT CAUSE,
REMEDIATION, NEXT STEP. EVIDENCE is copied byte-for-byte from the tool
output — no paraphrasing.
"""
)

if run:
    with st.status("Running Vertex AI Gemini...", expanded=True) as status:
        t0 = time.perf_counter()
        try:
            resp = ask(question, stub=stub, model=model)
        except Exception as e:  # pragma: no cover
            status.update(label=f"Error: {e}", state="error")
            st.exception(e)
            st.stop()
        elapsed = (time.perf_counter() - t0) * 1000
        status.update(label=f"Done in {elapsed:.0f} ms", state="complete")

    st.subheader("Diagnosis")
    st.markdown(resp.final_text or "_(no final response)_")

    with st.expander(f"Agent event trace ({len(resp.events)} events)"):
        for i, ev in enumerate(resp.events):
            st.markdown(f"**{i}.** author=`{ev.get('author')}` final=`{ev.get('is_final')}`")
            text = ev.get("text") or ""
            if text:
                st.code(text[:1500], language=None)
else:
    st.info("Use the sidebar to fire a diagnosis through the stub RPA MCP.")

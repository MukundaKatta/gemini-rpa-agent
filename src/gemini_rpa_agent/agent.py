"""ADK Gemini agent wired to an RPA / workflow-automation MCP server.

The agent walks an n8n-style RPA MCP (stubbed by default) to diagnose a
failed automation run end-to-end: which workflow, which step, what
broke, the verbatim error payload, and the canonical fix.
"""

from __future__ import annotations

import os
import sys
from typing import Any


try:
    from google.adk.agents import LlmAgent
    from google.adk.tools.mcp_tool import McpToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
    _ADK_AVAILABLE = True
except ImportError:  # pragma: no cover
    _ADK_AVAILABLE = False


SYSTEM_PROMPT = """\
You are an RPA / workflow-automation triage engineer. The user hands you
a workflow id (or a "what just broke?" question) and you walk the RPA
MCP tools end-to-end to diagnose the most recent failed run.

Workflow (do every step, in order):

1. `list_workflows` to find the workflow whose last_status is "failed".
   Capture its `workflow_id` and `last_run_id` verbatim.
2. `get_workflow_run` with that `run_id` to pull the full step trace.
   Identify the single step whose `status` is "failed".
3. `get_step_output` with that `run_id` + the failed `step_id` to get
   the verbatim error payload. Copy this byte-for-byte; do not
   paraphrase or reformat the JSON.
4. `suggest_retry` with the `run_id` to fetch the canonical fix and
   retry command from the orchestrator.

Output EXACTLY these labeled sections, in this order:

ANSWER:        which workflow, which step, what broke (one or two sentences
                naming the workflow id, the failing step id, and the
                top-level error symptom — every identifier copied verbatim
                from the tool output).
EVIDENCE:      the verbatim error payload (whole JSON object copied byte
                for byte from get_step_output), plus the step IDs of all
                steps in the run with their status. No paraphrasing.
ROOT CAUSE:    one-sentence diagnosis, grounded in the verbatim error
                payload and the suggest_retry diagnosis text.
REMEDIATION:   the copy-paste fix — the specific old value, new value,
                and retry command from suggest_retry. Copy the
                `retry_command` string verbatim.
NEXT STEP:     one concrete follow-up check the operator should do after
                applying the fix (for example: re-run the failed step,
                confirm the downstream side-effect happened).

Strict rules:
- Workflow IDs, run IDs, step IDs, channel IDs, timestamps, and error
  codes MUST be copied verbatim from the tool output. No reformatting.
- EVIDENCE must be byte-for-byte from the tool output, no paraphrasing.
  Quote the whole error JSON, not a summary of it.
- Do NOT invent step IDs, workflow IDs, or remediation values. Only use
  identifiers that came back from `list_workflows`, `get_workflow_run`,
  `get_step_output`, or `suggest_retry`.
- If `get_step_output` for the failed step returns an `ok: false` payload
  with an `error` field, that string is the canonical error code; quote
  it as-is in ANSWER and EVIDENCE.
- If any tool returns an `error` envelope, surface that fact in EVIDENCE
  and stop — do not guess.
"""


def _rpa_toolset(stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        raise ImportError("Install google-adk and mcp: pip install google-adk mcp")
    if stub:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "gemini_rpa_agent.mcp_stub"],
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    else:
        # Real RPA MCP server: configure via env vars. The official
        # UiPath / n8n MCP servers expose the same tool shape; swap the
        # command/args here once the published server is available.
        params = StdioServerParameters(
            command="npx",
            args=["-y", "@uipath/mcp@latest"],
            env={
                **os.environ,
                "RPA_API_URL":   os.environ.get("RPA_API_URL", ""),
                "RPA_API_TOKEN": os.environ.get("RPA_API_TOKEN", ""),
            },
        )
    return McpToolset(connection_params=StdioConnectionParams(server_params=params))


def build_agent(model: str = "gemini-2.5-flash", stub: bool = True) -> Any:
    if not _ADK_AVAILABLE:
        return None
    return LlmAgent(
        model=model,
        name="gemini_rpa_agent",
        instruction=SYSTEM_PROMPT,
        tools=[_rpa_toolset(stub=stub)],
    )

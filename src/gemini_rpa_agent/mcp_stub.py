"""Stub RPA / workflow-automation MCP server.

Exposes a slice of an n8n-style RPA MCP server's tool surface:
  - `list_workflows(active_only)` — registered workflows + last-run status
  - `get_workflow_run(run_id)`     — step-by-step trace of one run
  - `get_step_output(run_id, step_id)` — verbatim output / error payload
  - `suggest_retry(run_id)`        — remediation snippet for a failed run

Returns canned, realistic responses so judges can reproduce the demo
without standing up a real RPA orchestrator. The agent code is unchanged
when swapping to a real RPA MCP server — only the StdioServerParameters
in `agent.py` change.

Run with: python -m gemini_rpa_agent.mcp_stub

Submission: UiPath AgentHack 2026 ($50K, deadline 2026-06-29).
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


NOW = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Canned RPA workflow data
# ---------------------------------------------------------------------------


# A small registry of RPA workflows. The "interesting" one is
# wf-onboarding-pro-2026-001 — it has a failed run that the agent will
# diagnose end-to-end.
_WORKFLOWS: list[dict[str, Any]] = [
    {
        "workflow_id":     "wf-onboarding-pro-2026-001",
        "name":            "New Hire Onboarding (Pro)",
        "active":          True,
        "last_status":     "failed",
        "last_run_id":     "run-2026-05-18-09-14",
        "last_run_at":     "2026-05-18T09:14:00Z",
        "owner":           "people-ops@acme.example",
        "trigger":         "webhook:greenhouse.new_hire_signed",
        "steps_total":     3,
    },
    {
        "workflow_id":     "wf-invoice-sync-2026-014",
        "name":            "Invoice Sync (NetSuite → S3)",
        "active":          True,
        "last_status":     "success",
        "last_run_id":     "run-2026-05-18-08-02",
        "last_run_at":     "2026-05-18T08:02:00Z",
        "owner":           "finance-ops@acme.example",
        "trigger":         "schedule:0 */2 * * *",
        "steps_total":     5,
    },
    {
        "workflow_id":     "wf-support-router-2026-007",
        "name":            "Support Ticket Router",
        "active":          True,
        "last_status":     "success",
        "last_run_id":     "run-2026-05-18-09-03",
        "last_run_at":     "2026-05-18T09:03:00Z",
        "owner":           "cx-ops@acme.example",
        "trigger":         "webhook:zendesk.ticket.created",
        "steps_total":     4,
    },
]


# Full traces keyed by run_id. Each run is a 3-step sequence; the
# onboarding run fails on step 3 (slack-notify).
_RUNS: dict[str, dict[str, Any]] = {
    "run-2026-05-18-09-14": {
        "run_id":      "run-2026-05-18-09-14",
        "workflow_id": "wf-onboarding-pro-2026-001",
        "workflow_name": "New Hire Onboarding (Pro)",
        "status":      "failed",
        "started_at":  "2026-05-18T09:14:00Z",
        "finished_at": "2026-05-18T09:14:03Z",
        "trigger_payload": {
            "event":    "greenhouse.new_hire_signed",
            "hire_id":  "h-49217",
            "name":     "Priya Chandrasekar",
            "start_date": "2026-05-25",
            "department": "Engineering",
        },
        "steps": [
            {
                "step_id":    "fetch-hire-record",
                "name":       "Fetch hire record from Greenhouse",
                "type":       "http-request",
                "status":     "success",
                "started_at": "2026-05-18T09:14:00Z",
                "finished_at":"2026-05-18T09:14:01Z",
                "duration_ms": 842,
            },
            {
                "step_id":    "create-google-account",
                "name":       "Provision Google Workspace account",
                "type":       "google-admin",
                "status":     "success",
                "started_at": "2026-05-18T09:14:01Z",
                "finished_at":"2026-05-18T09:14:02Z",
                "duration_ms": 1310,
            },
            {
                "step_id":    "slack-notify",
                "name":       "Notify #new-hires in Slack",
                "type":       "slack-post-message",
                "status":     "failed",
                "started_at": "2026-05-18T09:14:02Z",
                "finished_at":"2026-05-18T09:14:03Z",
                "duration_ms": 612,
                "error_summary": "Slack API returned channel_not_found",
            },
        ],
    },
}


# Verbatim per-step outputs / error payloads. The slack-notify failure is
# the verbatim payload the agent will quote in EVIDENCE.
_STEP_OUTPUTS: dict[str, dict[str, Any]] = {
    "run-2026-05-18-09-14::fetch-hire-record": {
        "ok": True,
        "hire_id": "h-49217",
        "name": "Priya Chandrasekar",
        "email": "priya.c@acme.example",
        "start_date": "2026-05-25",
    },
    "run-2026-05-18-09-14::create-google-account": {
        "ok": True,
        "user": "priya.c@acme.example",
        "ou_path": "/Engineering",
        "provisioned_at": "2026-05-18T09:14:02Z",
    },
    "run-2026-05-18-09-14::slack-notify": {
        "ok": False,
        "error": "channel_not_found",
        "ts": "1747559640.000100",
        "channel_attempted": "#new-hires",
    },
}


# Remediation snippets keyed by run_id.
_RETRIES: dict[str, dict[str, Any]] = {
    "run-2026-05-18-09-14": {
        "run_id":      "run-2026-05-18-09-14",
        "workflow_id": "wf-onboarding-pro-2026-001",
        "failed_step": "slack-notify",
        "diagnosis": (
            "Slack rejected the post because the slack-notify step is "
            "addressing the channel by display name '#new-hires'. Slack's "
            "API requires a canonical channel ID; the display name was "
            "recently changed so the cached lookup is stale."
        ),
        "fix": {
            "replace_in_step": "slack-notify",
            "field":           "channel",
            "old_value":       "#new-hires",
            "new_value":       "C09NEW123HIRE",
            "note":            "Use the canonical channel ID. Stable across renames.",
        },
        "retry_command": (
            "rpa runs retry run-2026-05-18-09-14 "
            "--from-step slack-notify "
            "--patch channel=C09NEW123HIRE"
        ),
    },
}


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------


def list_workflows_response(active_only: bool = True) -> dict[str, Any]:
    workflows = [w for w in _WORKFLOWS if (not active_only) or w["active"]]
    return {
        "active_only": active_only,
        "count":       len(workflows),
        "workflows":   workflows,
        "fetched_at":  NOW.isoformat(),
    }


def get_workflow_run_response(run_id: str) -> dict[str, Any]:
    run = _RUNS.get(run_id)
    if run is None:
        return {"error": f"unknown run_id {run_id!r}",
                "known_run_ids": list(_RUNS.keys())}
    return run


def get_step_output_response(run_id: str, step_id: str) -> dict[str, Any]:
    key = f"{run_id}::{step_id}"
    output = _STEP_OUTPUTS.get(key)
    if output is None:
        return {"error": f"no output captured for {key!r}",
                "run_id": run_id, "step_id": step_id}
    return {"run_id": run_id, "step_id": step_id, "output": output}


def suggest_retry_response(run_id: str) -> dict[str, Any]:
    rec = _RETRIES.get(run_id)
    if rec is None:
        return {"error": f"no retry suggestion for {run_id!r}",
                "hint": "suggest_retry only fires for known failed runs"}
    return rec


# ---------------------------------------------------------------------------
# MCP server wiring
# ---------------------------------------------------------------------------


def _make_server() -> Server:
    server = Server("rpa-stub")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="list_workflows",
                 description=("List registered RPA workflows with their last-run "
                              "status. Set active_only=false to include disabled "
                              "workflows. Use this to find the failed one."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "active_only": {"type": "boolean", "default": True},
                              },
                              "required": []}),
            Tool(name="get_workflow_run",
                 description=("Fetch the full step-by-step trace of one workflow "
                              "run by run_id. Returns each step's id, name, "
                              "status, timestamps, and a short error_summary "
                              "if the step failed."),
                 inputSchema={"type": "object",
                              "properties": {"run_id": {"type": "string"}},
                              "required": ["run_id"]}),
            Tool(name="get_step_output",
                 description=("Fetch the verbatim output (or error payload) for "
                              "one step of one run. Use this on the failed step "
                              "to get the byte-for-byte error JSON you should "
                              "cite in EVIDENCE."),
                 inputSchema={"type": "object",
                              "properties": {
                                  "run_id":  {"type": "string"},
                                  "step_id": {"type": "string"},
                              },
                              "required": ["run_id", "step_id"]}),
            Tool(name="suggest_retry",
                 description=("Ask the orchestrator for a remediation snippet "
                              "for a failed run: which step to patch, the "
                              "specific old/new field values, and the retry "
                              "CLI command. Only call after you have the "
                              "verbatim step error in hand."),
                 inputSchema={"type": "object",
                              "properties": {"run_id": {"type": "string"}},
                              "required": ["run_id"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        a = arguments
        if name == "list_workflows":
            payload = list_workflows_response(bool(a.get("active_only", True)))
        elif name == "get_workflow_run":
            payload = get_workflow_run_response(str(a.get("run_id", "")))
        elif name == "get_step_output":
            payload = get_step_output_response(str(a.get("run_id", "")),
                                                str(a.get("step_id", "")))
        elif name == "suggest_retry":
            payload = suggest_retry_response(str(a.get("run_id", "")))
        else:
            payload = {"error": f"unknown tool {name!r}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]

    return server


async def _main() -> None:
    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()

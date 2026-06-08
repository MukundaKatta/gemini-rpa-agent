"""Canned RPA / workflow-automation data and pure response builders.

This module is intentionally **dependency-free** — it imports only the
Python standard library. All the canned workflow data and the four
response builders (``list_workflows_response``, ``get_workflow_run_response``,
``get_step_output_response``, ``suggest_retry_response``) live here so they
can be imported and unit-tested without the ``mcp`` / ``google-adk`` stack.

``mcp_stub`` re-exports everything from this module and adds the MCP server
transport wiring on top. Swapping to a real RPA orchestrator only touches
``agent.py`` (the ``StdioServerParameters``); this data is the deterministic
fixture used for the demo and the tests.

The "interesting" workflow is ``wf-onboarding-pro-2026-001`` — it has a
failed run (``run-2026-05-18-09-14``) whose ``slack-notify`` step returns a
verbatim ``channel_not_found`` error that the agent diagnoses end-to-end.

Submission: UiPath AgentHack 2026 ($50K, deadline 2026-06-29).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

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
    """Return the registered workflows + their last-run status.

    Args:
        active_only: When True (the default), disabled workflows are
            filtered out. All three seeded workflows are active, so the
            count is 3 in both modes for this fixture.

    Returns:
        A dict with ``active_only``, ``count``, ``workflows`` (the list of
        workflow records), and a ``fetched_at`` ISO-8601 timestamp.
    """
    workflows = [w for w in _WORKFLOWS if (not active_only) or w["active"]]
    return {
        "active_only": active_only,
        "count":       len(workflows),
        "workflows":   workflows,
        "fetched_at":  NOW.isoformat(),
    }


def get_workflow_run_response(run_id: str) -> dict[str, Any]:
    """Return the full step-by-step trace for a single run.

    Args:
        run_id: The run identifier (for example ``run-2026-05-18-09-14``).

    Returns:
        The run record (with its ``steps`` list) if ``run_id`` is known,
        otherwise an ``{"error": ..., "known_run_ids": [...]}`` envelope so
        the agent can surface the failure instead of guessing.
    """
    run = _RUNS.get(run_id)
    if run is None:
        return {"error": f"unknown run_id {run_id!r}",
                "known_run_ids": list(_RUNS.keys())}
    return run


def get_step_output_response(run_id: str, step_id: str) -> dict[str, Any]:
    """Return the verbatim output / error payload for one step of one run.

    Args:
        run_id: The run identifier.
        step_id: The step identifier within that run.

    Returns:
        ``{"run_id", "step_id", "output"}`` where ``output`` is the
        byte-for-byte payload the agent must quote in EVIDENCE, or an
        ``{"error": ...}`` envelope if no output was captured for the pair.
    """
    key = f"{run_id}::{step_id}"
    output = _STEP_OUTPUTS.get(key)
    if output is None:
        return {"error": f"no output captured for {key!r}",
                "run_id": run_id, "step_id": step_id}
    return {"run_id": run_id, "step_id": step_id, "output": output}


def suggest_retry_response(run_id: str) -> dict[str, Any]:
    """Return the canonical remediation snippet for a failed run.

    Args:
        run_id: The run identifier of a known failed run.

    Returns:
        A remediation record (``failed_step``, ``diagnosis``, ``fix`` with
        old/new values, and a copy-paste ``retry_command``) for known
        failed runs, otherwise an ``{"error": ..., "hint": ...}`` envelope.
    """
    rec = _RETRIES.get(run_id)
    if rec is None:
        return {"error": f"no retry suggestion for {run_id!r}",
                "hint": "suggest_retry only fires for known failed runs"}
    return rec

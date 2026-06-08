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

The canned data and the four response builders live in the
dependency-free :mod:`gemini_rpa_agent.rpa_data` module and are
re-exported here for backwards compatibility. The ``mcp`` package is
imported lazily inside :func:`_make_server`, so this module can be
imported (and the response builders exercised) without ``mcp`` installed.

Run with: python -m gemini_rpa_agent.mcp_stub

Submission: UiPath AgentHack 2026 ($50K, deadline 2026-06-29).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

# Re-export the canned data and pure response builders. These have no
# third-party dependency, so they stay importable even when ``mcp`` is not.
from gemini_rpa_agent.rpa_data import (
    NOW,
    _RETRIES,
    _RUNS,
    _STEP_OUTPUTS,
    _WORKFLOWS,
    get_step_output_response,
    get_workflow_run_response,
    list_workflows_response,
    suggest_retry_response,
)

__all__ = [
    "NOW",
    "_RETRIES",
    "_RUNS",
    "_STEP_OUTPUTS",
    "_WORKFLOWS",
    "get_step_output_response",
    "get_workflow_run_response",
    "list_workflows_response",
    "suggest_retry_response",
    "main",
]


# ---------------------------------------------------------------------------
# MCP server wiring (imports ``mcp`` lazily — only needed to serve, not to
# call the response builders directly)
# ---------------------------------------------------------------------------


def _make_server() -> Any:
    from mcp.server import Server
    from mcp.types import TextContent, Tool

    server = Server("rpa-stub")

    @server.list_tools()
    async def list_tools() -> list["Tool"]:
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
    async def call_tool(name: str, arguments: dict[str, Any]) -> list["TextContent"]:
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
    from mcp.server.stdio import stdio_server

    server = _make_server()
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()

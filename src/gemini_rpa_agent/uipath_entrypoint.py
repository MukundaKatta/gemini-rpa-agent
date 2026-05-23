"""UiPath Maestro entry point for gemini-rpa-agent.

This is the function UiPath Orchestrator invokes when Maestro hits the
"start agent" Service Task. The function:

1. Builds the ADK ``LlmAgent`` with ``UiPathGemini`` as the model — so
   every Gemini call goes through UiPath's LLM Gateway (this is what
   satisfies AgentHack's "orchestration must run through the UiPath
   Platform" rule).
2. Walks the RPA MCP tool surface end-to-end on whatever query Maestro
   passes in (defaults to the canonical "diagnose the most recent
   failed run" prompt).
3. Returns the structured 5-section report (ANSWER / EVIDENCE / ROOT
   CAUSE / REMEDIATION / NEXT STEP) plus a list of tool-call events for
   downstream Maestro tasks (e.g. a "post Slack" task that consumes
   ``report`` directly).

Local dev::

    uv run uipath run agent '{"query": "Diagnose the most recent failed run."}'

Pack + publish to Orchestrator::

    uv run uipath pack
    uv run uipath publish

Then reference the published agent in a Maestro BPMN process via a
"Start and wait for external agent" Service Task.
"""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field

from gemini_rpa_agent.agent import build_agent


class Input(BaseModel):
    """Maestro-side input contract."""

    query: str = Field(
        default="Diagnose the most recent failed workflow run end-to-end.",
        description="What the operator wants the triage agent to do.",
    )
    model: str = Field(
        default="gemini-2.5-flash",
        description="Gemini model name; routed through UiPath LLM Gateway.",
    )
    stub: bool = Field(
        default=True,
        description=(
            "Use the bundled n8n/UiPath-shaped MCP stub for deterministic "
            "demo output. Set False to point at a real RPA MCP server "
            "configured via RPA_API_URL + RPA_API_TOKEN env vars."
        ),
    )


class ToolEvent(BaseModel):
    author: str | None = None
    is_final: bool = False
    text: str = ""


class Output(BaseModel):
    """Maestro-side output contract."""

    report: str = Field(
        description="The 5-section triage report (ANSWER / EVIDENCE / ROOT CAUSE / REMEDIATION / NEXT STEP)."
    )
    events: list[ToolEvent] = Field(
        default_factory=list,
        description="Ordered list of LLM/tool events for downstream Maestro tasks.",
    )
    error: str | None = None


async def main(input_data: Input) -> Output:
    """UiPath entry point (async — the runtime already owns the loop)."""
    # Import ADK lazily so that schema-generation passes (uipath init /
    # uipath pack) don't require ADK to be importable in the build env.
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
    except ImportError as exc:
        return Output(
            report="",
            events=[],
            error=f"google-adk not installed: {exc}",
        )

    # Production (Maestro / Orchestrator) routes through the UiPath LLM
    # Gateway. ``UIPATH_LOCAL_TEST=1`` flips to plain Vertex so the
    # entrypoint can be smoke-tested locally without UiPath auth.
    use_gateway = os.environ.get("UIPATH_LOCAL_TEST") != "1"
    agent = build_agent(
        model=input_data.model,
        stub=input_data.stub,
        use_uipath_gateway=use_gateway,
    )
    if agent is None:
        return Output(
            report="",
            events=[],
            error="build_agent returned None (ADK not available).",
        )

    session_service = InMemorySessionService()
    app_name = "gemini-rpa-agent"
    user_id = os.getenv("UIPATH_USER", "uipath")
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    runner = Runner(
        agent=agent, app_name=app_name, session_service=session_service
    )
    content = types.Content(
        role="user", parts=[types.Part(text=input_data.query)]
    )

    events: list[ToolEvent] = []
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=content
    ):
        author = getattr(event, "author", None)
        is_final = (
            event.is_final_response()
            if hasattr(event, "is_final_response")
            else False
        )
        text = ""
        if hasattr(event, "content") and event.content is not None:
            parts = getattr(event.content, "parts", []) or []
            text = "".join(
                getattr(p, "text", "") or "" for p in parts
            )
            if is_final:
                final_text = text
        events.append(ToolEvent(author=author, is_final=is_final, text=text))

    return Output(report=final_text, events=events)

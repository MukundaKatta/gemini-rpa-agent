# Devpost submission package — gemini-rpa-agent

Pre-filled fields for **UiPath AgentHack** (primary, $50K, deadline Jun 29 2026)
and any cross-submission to Mega Agent-A-Thon / USAII Global AI / generic agent
hackathons.

## 📋 Basic Information

**Project Title**

    gemini-rpa-agent

**Tagline / Short Description**

    A Gemini 2.5 RPA-diagnosis agent that walks an n8n-style MCP toolchain to pin
    down which workflow step broke, the verbatim error payload, and the exact
    remediation — copied byte-for-byte from the failing run.

**Long Description**

    gemini-rpa-agent is a workflow-automation diagnosis agent. When an RPA run
    fails at 09:14 UTC and the on-call asks "why?", the agent walks four
    MCP tools end-to-end and answers with cited evidence:

    1. list_workflows(active_only)        — finds the failing workflow id
    2. get_workflow_run(run_id)           — walks the step trace
    3. get_step_output(run_id, step_id)   — fetches the verbatim error payload
    4. suggest_retry(run_id)              — emits the canonical retry command

    Every output sits in 5 strictly-labeled sections:

      ANSWER:      which workflow, which step, what broke
      EVIDENCE:    verbatim error payload + step IDs (no paraphrasing)
      ROOT CAUSE:  one-sentence diagnosis
      REMEDIATION: copy-paste fix
      NEXT STEP:   one follow-up check

    EVIDENCE is byte-for-byte from the tool result. The system prompt rejects
    paraphrasing. If the live tool result was "channel_not_found", the agent
    quotes "channel_not_found", not "the channel could not be found".

    Built on Google Cloud Agent Builder (ADK) with Gemini 2.5 Flash on Vertex AI,
    wired to an RPA MCP server. The repo ships a local stub seeded with a real
    failure pattern (Slack notify failing because the workflow used a channel
    name instead of a channel ID), plus one-env-var swap to any real n8n / UiPath
    MCP server.

**Technology & Category Tags**

    python, gemini, gemini-2-5, vertex-ai, google-cloud-agent-builder,
    agent-development-kit, mcp, model-context-protocol, rpa, n8n, uipath,
    workflow-automation, streamlit, google-cloud-run, apache-2

## 💻 App Hosting & Code Repository

**Public GitHub Repository**

    https://github.com/MukundaKatta/gemini-rpa-agent

**Demo Application Platform**

    Google Cloud Run (us-central1)

**Application URL**

    https://gemini-rpa-agent-1029931682737.us-central1.run.app

## 📸 Cover Image and Presentation

**Cover Image**

    Regenerate via the gemini-bright-agent cover script with new colors, or use
    a screenshot from the dashboard. (Quick path: copy
    /Users/ubl/gemini-bright-agent/scripts/make_cover.py, change title to
    "gemini-rpa-agent" and accent to UiPath orange #fa4616.)

**Video Presentation**

    https://youtu.be/PASTE_AFTER_UPLOAD
    (Source MP4: /Users/ubl/gemini-rpa-agent/.video-build/demo.mp4 — 2:13)

## Cross-submission targets

| Hackathon | URL | Notes |
|---|---|---|
| **UiPath AgentHack** | https://uipath-agenthack.devpost.com/ | Primary. $50K. Agentic + enterprise theme. |
| Mega Agent-A-Thon | https://mega-agent-a-thon.devpost.com/ | Generic agent. Any repo accepted. |
| USAII Global AI | https://usaii-global-ai-hackathon-2026.devpost.com/ | $15K. Verify eligibility. |

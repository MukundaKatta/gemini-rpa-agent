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

    gemini-rpa-agent is a workflow-automation diagnosis agent that runs as
    a coded UiPath agent, orchestrated by a UiPath Maestro BPMN process.
    When an RPA run fails at 09:14 UTC and the on-call asks "why?",
    Maestro hands the query to the agent, which walks four MCP tools
    end-to-end and answers with cited evidence:

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

    The coded agent is built on Google ADK with Gemini 2.5 Flash, packaged
    via the official uipath-python SDK and published to UiPath Orchestrator
    (uipath pack + uipath publish). Every Gemini call is routed through the
    UiPath LLM Gateway via UiPathGemini from uipath-google-adk — the gateway
    is on the hot path, not a side channel. The Streamlit dashboard on Cloud
    Run is a side-channel UI for demos and debugging; production traffic
    enters through Maestro.

**Technology & Category Tags**

    python, uipath, uipath-maestro, uipath-orchestrator, uipath-llm-gateway,
    gemini, gemini-2-5, agent-development-kit, mcp, model-context-protocol,
    rpa, workflow-automation, streamlit, google-cloud-run, apache-2

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

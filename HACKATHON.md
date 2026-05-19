# UiPath AgentHack 2026 submission

Hackathon: UiPath AgentHack 2026
Prize pool: $50K
Deadline: 2026-06-29

## Elevator pitch

A Gemini-powered RPA triage agent that walks an n8n-style RPA MCP
server end-to-end to diagnose a failed automation run — workflow, step,
verbatim error payload, and the canonical fix.

## Rule compliance

| Rule | How we meet it |
|---|---|
| RPA / workflow-automation theme | Tool surface (`list_workflows`, `get_workflow_run`, `get_step_output`, `suggest_retry`) matches an n8n / UiPath RPA MCP shape; stub for demos, real orchestrator via env vars |
| AI agent (not just a script) | `google.adk.agents.LlmAgent` with Gemini 2.5 Flash on Vertex AI walks the tools across multiple turns; output is structured with byte-for-byte verbatim EVIDENCE |
| Original work | Standalone repo, Apache 2.0 |
| Runs on the web | Streamlit dashboard, Cloud Run deployable |

## Description

`gemini-rpa-agent` treats every failed RPA run as a four-tool walk:

1. `list_workflows` — find the workflow whose `last_status` is `failed`,
   capture its `workflow_id` and `last_run_id`.
2. `get_workflow_run(run_id)` — pull the step-by-step trace, identify
   the single failing step.
3. `get_step_output(run_id, step_id)` — fetch the verbatim error payload
   from the failing step (byte-for-byte JSON).
4. `suggest_retry(run_id)` — fetch the canonical fix and retry command.

The agent's answer is a 5-section report (ANSWER / EVIDENCE / ROOT
CAUSE / REMEDIATION / NEXT STEP). EVIDENCE is copied byte-for-byte from
the tool output — the system prompt explicitly rejects paraphrasing.

On the canned `wf-onboarding-pro-2026-001` workflow the agent identifies
that the `slack-notify` step failed at 2026-05-18T09:14:03Z with
`{"error":"channel_not_found","ts":"1747559640.000100","channel_attempted":"#new-hires"}`,
quotes the orchestrator's diagnosis verbatim, and recommends replacing
the display name with the canonical channel ID `C09NEW123HIRE`.

## Built with

python, gemini, gemini-2-5, vertex-ai, google-cloud-agent-builder,
agent-development-kit, mcp, model-context-protocol, rpa, n8n, uipath,
streamlit, google-cloud-run, apache-2

## Try it out

- Code repo: https://github.com/MukundaKatta/gemini-rpa-agent
- Live demo (Cloud Run): pinned after deploy
- Demo video (YouTube unlisted): pinned after upload

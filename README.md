# gemini-rpa-agent

An RPA / workflow-automation failure-diagnosis agent built on **Google
Cloud Agent Builder (ADK)**, **Gemini 2.5**, and an n8n-style **RPA MCP
server**. Submission for the **UiPath AgentHack 2026** ($50K prize pool,
deadline 2026-06-29).

**Live demo:** pinned after Cloud Run deploy
**Demo video:** pinned after upload
**License:** Apache 2.0

## What it does

You ask "workflow wf-onboarding-pro-2026-001 had a failure at 09:14 UTC,
tell me what broke and how to fix it". The agent walks the RPA MCP
tools — `list_workflows`, `get_workflow_run`, `get_step_output`,
`suggest_retry` — finds the failing step, reads the verbatim error
payload, and returns a 5-section diagnosis with the canonical fix
quoted directly from the orchestrator.

## Tool surface

The agent uses an n8n-style RPA MCP surface so the stub here is one
env-var swap away from a real RPA orchestrator (UiPath, n8n,
self-hosted):

- `list_workflows(active_only)` — workflows + last-run status
- `get_workflow_run(run_id)` — full step-by-step trace for one run
- `get_step_output(run_id, step_id)` — verbatim output / error payload for one step
- `suggest_retry(run_id)` — canonical fix + retry command

## Architecture

```
+----------------------+    +-----------------------+   +----------------------------+
| Streamlit dashboard  |--> |  ADK LlmAgent         |-->|  RPA MCP server            |
| on Cloud Run         |    |  Gemini 2.5 on Vertex |   |  (stub for demos,          |
|                      |    |  AI                   |   |   real tenant via env vars)|
| "diagnose run X..."  |    |                       |   |                            |
+----------------------+    +-----------------------+   +----------------------------+
```

## Output contract

The system prompt requires EXACTLY these labeled sections per answer:

```
ANSWER:      which workflow, which step, what broke (one or two sentences).
EVIDENCE:    verbatim error payload + step IDs (no paraphrasing).
ROOT CAUSE:  one-sentence diagnosis.
REMEDIATION: copy-paste fix (old value, new value, retry command).
NEXT STEP:   one follow-up check.
```

Strict rule: EVIDENCE must be byte-for-byte from the tool output. The
agent quotes the failing step's error JSON whole, never paraphrases.

## Try it locally

```bash
git clone https://github.com/MukundaKatta/gemini-rpa-agent
cd gemini-rpa-agent
uv venv -q && uv pip install -q -e ".[dev]"

gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1

PYTHONPATH=src .venv/bin/streamlit run app/dashboard.py
```

## Try it against a real RPA orchestrator

```bash
export RPA_API_URL="https://your-orchestrator.example/api"
export RPA_API_TOKEN="..."
```

Untick "Use stub RPA MCP" in the sidebar. The agent now spawns the real
RPA MCP server in place of the stub.

## Tests

```bash
.venv/bin/pytest -q
```

The suite pins the diagnosis chain end-to-end: `list_workflows` finds
the failed onboarding workflow, `get_workflow_run` returns its
three-step trace with `slack-notify` as the single failure,
`get_step_output` returns the verbatim `channel_not_found` payload, and
`suggest_retry` proposes the canonical channel-ID fix.

## License

Apache 2.0. Mukunda Katta, independent.

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
+---------------------+   +----------------------+   +----------------------+   +-----------------+
| UiPath Maestro      |-->| ADK LlmAgent         |-->| UiPath LLM Gateway   |-->| RPA MCP server  |
| BPMN process        |   | (uipath_entrypoint   |   | (UiPathGemini routes |   | (stub or real   |
| Service Task hits   |   |  main coroutine)     |   |  every Gemini call)  |   | RPA orchestr.)  |
| the coded agent     |   |                      |   |                      |   |                 |
+---------------------+   +----------------------+   +----------------------+   +-----------------+
```

The orchestration entry point is **UiPath Maestro**, not the Streamlit
dashboard. Maestro calls the coded agent published to UiPath
Orchestrator via `uipath publish`; the agent uses `UiPathGemini` from
`uipath-google-adk` so every Gemini call is routed through the UiPath
LLM Gateway (not direct Vertex). This is what satisfies the AgentHack
rule that "orchestration and agent logic must run through the UiPath
Platform." The Streamlit dashboard on Cloud Run remains available as a
side-channel UI for demos and local debugging.

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

## Use it as a library

### Ask the agent a question (needs `google-adk` + Vertex credentials)

```python
from gemini_rpa_agent.runner import ask

resp = ask(
    "Workflow wf-onboarding-pro-2026-001 had a failure at 09:14 UTC — "
    "tell me what broke and how to fix it.",
    stub=True,                  # use the bundled RPA MCP stub
    model="gemini-2.5-flash",
)
print(resp.final_text)          # the 5-section report
print(len(resp.events))         # ordered LLM / tool events
```

If `google-adk` is not installed, `ask()` returns an `AgentResponse`
whose `final_text` is an offline-fallback message and whose `error` is
set — it never raises, so callers can degrade gracefully.

### Call the RPA response builders directly (no third-party deps)

The deterministic stub data and the four response builders are pure
functions in `gemini_rpa_agent.rpa_data`. You can drive the diagnosis
chain yourself without any LLM:

```python
from gemini_rpa_agent.rpa_data import (
    list_workflows_response,
    get_workflow_run_response,
    get_step_output_response,
    suggest_retry_response,
)

failed = next(
    w for w in list_workflows_response()["workflows"]
    if w["last_status"] == "failed"
)
run = get_workflow_run_response(failed["last_run_id"])
bad_step = next(s for s in run["steps"] if s["status"] == "failed")
evidence = get_step_output_response(run["run_id"], bad_step["step_id"])
fix = suggest_retry_response(run["run_id"])

print(evidence["output"]["error"])   # 'channel_not_found'
print(fix["retry_command"])          # canonical retry CLI command
```

Every builder returns a plain `dict`; unknown run/step ids come back as
an `{"error": ...}` envelope rather than raising, mirroring how a real
orchestrator surfaces lookup misses.

## Try it locally (Streamlit dashboard)

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

## UiPath Maestro deployment

```bash
# 1. Pack the coded agent.
uv run uipath pack
# -> .uipath/gemini-rpa-agent.0.1.0.nupkg

# 2. Authenticate against UiPath Community / Enterprise tenant.
uv run uipath auth

# 3. Publish to Orchestrator. The agent shows up under Personal Workspace.
uv run uipath publish

# 4. Smoke-test the entry point locally (Vertex fallback, skips gateway).
UIPATH_LOCAL_TEST=1 GOOGLE_GENAI_USE_VERTEXAI=1 \
  GOOGLE_CLOUD_PROJECT=your-project GOOGLE_CLOUD_LOCATION=us-central1 \
  uv run uipath run agent '{"query": "Diagnose the most recent failed run."}'
```

Then build a Maestro BPMN process: **Start → "Start and wait for
external agent" Service Task (pointing at the published
`gemini-rpa-agent`) → End**. The Service Task's input maps to the
agent's `Input.query`; the agent's `Output.report` flows downstream.

## Try it against a real RPA orchestrator

```bash
export RPA_API_URL="https://your-orchestrator.example/api"
export RPA_API_TOKEN="..."
```

Untick "Use stub RPA MCP" in the sidebar. The agent now spawns the real
RPA MCP server in place of the stub.

## Tests

The unit suite is written against the Python **standard-library
`unittest`** runner and has **no third-party dependencies** — it does not
need `google-adk`, `mcp`, or `pydantic` installed. The tests put `src/`
on `sys.path` themselves, so no editable install is required either:

```bash
python3 -m unittest discover -s tests
```

This is exactly what CI runs (see `.github/workflows/ci.yml`, across
Python 3.10–3.12). The suite pins the diagnosis chain end-to-end:
`list_workflows` finds the failed onboarding workflow,
`get_workflow_run` returns its three-step trace with `slack-notify` as
the single failure, `get_step_output` returns the verbatim
`channel_not_found` payload, and `suggest_retry` proposes the canonical
channel-ID fix. It also covers the error-envelope paths (unknown
run/step ids) and the agent's graceful offline fallback when `google-adk`
is absent.

The canned data and the four response builders live in the
dependency-free `gemini_rpa_agent.rpa_data` module; `mcp_stub` re-exports
them and adds the MCP transport on top (importing `mcp` lazily), so the
pure logic stays unit-testable without standing up the MCP server.

### Live Vertex smoke test (requires the full stack + credentials)

```bash
uv venv -q && uv pip install -q -e ".[dev]"
GOOGLE_CLOUD_PROJECT=your-project GOOGLE_GENAI_USE_VERTEXAI=true \
  GOOGLE_CLOUD_LOCATION=us-central1 \
  .venv/bin/python scripts/smoke.py
```

This runs the question end-to-end through Gemini on the stub MCP server
and asserts the agent emits all five labeled sections and quotes the
verbatim `channel_not_found` error.

## License

Apache 2.0. Mukunda Katta, independent.

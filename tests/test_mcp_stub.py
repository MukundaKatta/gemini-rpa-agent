from gemini_rpa_agent.mcp_stub import (
    _WORKFLOWS,
    _RUNS,
    _STEP_OUTPUTS,
    _RETRIES,
    list_workflows_response,
    get_workflow_run_response,
    get_step_output_response,
    suggest_retry_response,
)


def test_data_seeded():
    assert len(_WORKFLOWS) >= 3
    assert "run-2026-05-18-09-14" in _RUNS
    assert "run-2026-05-18-09-14::slack-notify" in _STEP_OUTPUTS
    assert "run-2026-05-18-09-14" in _RETRIES


def test_list_workflows_active_only_includes_onboarding():
    payload = list_workflows_response(active_only=True)
    ids = [w["workflow_id"] for w in payload["workflows"]]
    assert "wf-onboarding-pro-2026-001" in ids
    # All three seeded workflows are active.
    assert payload["count"] == 3


def test_list_workflows_marks_onboarding_failed():
    payload = list_workflows_response()
    onboarding = next(
        w for w in payload["workflows"]
        if w["workflow_id"] == "wf-onboarding-pro-2026-001"
    )
    assert onboarding["last_status"] == "failed"
    assert onboarding["last_run_id"] == "run-2026-05-18-09-14"


def test_get_workflow_run_returns_three_step_trace():
    payload = get_workflow_run_response("run-2026-05-18-09-14")
    assert payload["workflow_id"] == "wf-onboarding-pro-2026-001"
    assert payload["status"] == "failed"
    step_ids = [s["step_id"] for s in payload["steps"]]
    assert step_ids == ["fetch-hire-record", "create-google-account", "slack-notify"]
    failed = [s for s in payload["steps"] if s["status"] == "failed"]
    assert len(failed) == 1
    assert failed[0]["step_id"] == "slack-notify"


def test_get_workflow_run_unknown_returns_error():
    payload = get_workflow_run_response("run-does-not-exist")
    assert "error" in payload
    assert "run-2026-05-18-09-14" in payload["known_run_ids"]


def test_get_step_output_returns_verbatim_slack_error():
    payload = get_step_output_response("run-2026-05-18-09-14", "slack-notify")
    output = payload["output"]
    assert output["ok"] is False
    assert output["error"] == "channel_not_found"
    assert output["channel_attempted"] == "#new-hires"
    assert output["ts"] == "1747559640.000100"


def test_get_step_output_unknown_step_returns_error():
    payload = get_step_output_response("run-2026-05-18-09-14", "nope")
    assert "error" in payload


def test_suggest_retry_swaps_to_canonical_channel_id():
    payload = suggest_retry_response("run-2026-05-18-09-14")
    fix = payload["fix"]
    assert payload["failed_step"] == "slack-notify"
    assert fix["old_value"] == "#new-hires"
    assert fix["new_value"] == "C09NEW123HIRE"
    assert "C09NEW123HIRE" in payload["retry_command"]


def test_suggest_retry_unknown_run_returns_error():
    payload = suggest_retry_response("run-not-here")
    assert "error" in payload


def test_workflow_diagnosis_chain_is_consistent():
    """The agent's killer move: list_workflows → get_workflow_run →
    get_step_output, then suggest_retry. The chain stays consistent:

    - The failed workflow surfaced by list_workflows is
      wf-onboarding-pro-2026-001 with last_run_id run-2026-05-18-09-14.
    - The run trace points to the slack-notify step as the single failure.
    - get_step_output on that step returns the verbatim
      channel_not_found error with the #new-hires channel.
    - suggest_retry's diagnosis names the same step and a fix that
      replaces #new-hires with the canonical channel ID.
    """
    listing = list_workflows_response(active_only=True)
    failed = [w for w in listing["workflows"] if w["last_status"] == "failed"]
    assert len(failed) == 1
    wf = failed[0]
    assert wf["workflow_id"] == "wf-onboarding-pro-2026-001"

    run = get_workflow_run_response(wf["last_run_id"])
    assert run["workflow_id"] == wf["workflow_id"]
    failed_step = next(s for s in run["steps"] if s["status"] == "failed")
    assert failed_step["step_id"] == "slack-notify"

    out = get_step_output_response(run["run_id"], failed_step["step_id"])
    # channel_not_found must appear verbatim in the payload — that's what
    # the agent will quote in EVIDENCE.
    assert out["output"]["error"] == "channel_not_found"

    retry = suggest_retry_response(run["run_id"])
    # Suggested fix must name the same step and swap to the canonical ID.
    assert retry["failed_step"] == "slack-notify"
    assert retry["fix"]["new_value"] == "C09NEW123HIRE"
    # wf-onboarding-pro-2026-001 must appear in both list and run.
    assert wf["workflow_id"] == "wf-onboarding-pro-2026-001"
    assert run["workflow_id"] == "wf-onboarding-pro-2026-001"

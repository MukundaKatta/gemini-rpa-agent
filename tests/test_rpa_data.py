"""Unit tests for the dependency-free RPA data and response builders.

These tests use only the standard-library ``unittest`` framework and the
``gemini_rpa_agent.rpa_data`` module, which has no third-party
dependencies. They exercise the real response builders the MCP stub
serves, plus the full diagnosis chain the agent walks at runtime.

Run with::

    PYTHONPATH=src python3 -m unittest discover -s tests
"""

import os
import sys
import unittest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from gemini_rpa_agent.rpa_data import (  # noqa: E402
    _RETRIES,
    _RUNS,
    _STEP_OUTPUTS,
    _WORKFLOWS,
    get_step_output_response,
    get_workflow_run_response,
    list_workflows_response,
    suggest_retry_response,
)


class SeedDataTests(unittest.TestCase):
    def test_data_seeded(self):
        self.assertGreaterEqual(len(_WORKFLOWS), 3)
        self.assertIn("run-2026-05-18-09-14", _RUNS)
        self.assertIn("run-2026-05-18-09-14::slack-notify", _STEP_OUTPUTS)
        self.assertIn("run-2026-05-18-09-14", _RETRIES)

    def test_every_workflow_has_required_keys(self):
        required = {
            "workflow_id", "name", "active", "last_status",
            "last_run_id", "owner", "trigger", "steps_total",
        }
        for wf in _WORKFLOWS:
            self.assertTrue(required.issubset(wf), f"missing keys in {wf}")

    def test_exactly_one_failed_workflow_in_fixture(self):
        failed = [w for w in _WORKFLOWS if w["last_status"] == "failed"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["workflow_id"], "wf-onboarding-pro-2026-001")


class ListWorkflowsTests(unittest.TestCase):
    def test_active_only_includes_onboarding(self):
        payload = list_workflows_response(active_only=True)
        ids = [w["workflow_id"] for w in payload["workflows"]]
        self.assertIn("wf-onboarding-pro-2026-001", ids)
        # All three seeded workflows are active.
        self.assertEqual(payload["count"], 3)

    def test_count_matches_workflow_list_length(self):
        payload = list_workflows_response()
        self.assertEqual(payload["count"], len(payload["workflows"]))

    def test_marks_onboarding_failed(self):
        payload = list_workflows_response()
        onboarding = next(
            w for w in payload["workflows"]
            if w["workflow_id"] == "wf-onboarding-pro-2026-001"
        )
        self.assertEqual(onboarding["last_status"], "failed")
        self.assertEqual(onboarding["last_run_id"], "run-2026-05-18-09-14")

    def test_active_only_flag_echoed(self):
        self.assertTrue(list_workflows_response(active_only=True)["active_only"])
        self.assertFalse(list_workflows_response(active_only=False)["active_only"])

    def test_fetched_at_present(self):
        self.assertIn("fetched_at", list_workflows_response())


class GetWorkflowRunTests(unittest.TestCase):
    def test_returns_three_step_trace(self):
        payload = get_workflow_run_response("run-2026-05-18-09-14")
        self.assertEqual(payload["workflow_id"], "wf-onboarding-pro-2026-001")
        self.assertEqual(payload["status"], "failed")
        step_ids = [s["step_id"] for s in payload["steps"]]
        self.assertEqual(
            step_ids,
            ["fetch-hire-record", "create-google-account", "slack-notify"],
        )
        failed = [s for s in payload["steps"] if s["status"] == "failed"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["step_id"], "slack-notify")

    def test_unknown_run_returns_error_envelope(self):
        payload = get_workflow_run_response("run-does-not-exist")
        self.assertIn("error", payload)
        self.assertIn("run-2026-05-18-09-14", payload["known_run_ids"])

    def test_empty_run_id_returns_error_envelope(self):
        payload = get_workflow_run_response("")
        self.assertIn("error", payload)


class GetStepOutputTests(unittest.TestCase):
    def test_returns_verbatim_slack_error(self):
        payload = get_step_output_response("run-2026-05-18-09-14", "slack-notify")
        output = payload["output"]
        self.assertIs(output["ok"], False)
        self.assertEqual(output["error"], "channel_not_found")
        self.assertEqual(output["channel_attempted"], "#new-hires")
        self.assertEqual(output["ts"], "1747559640.000100")

    def test_returns_successful_step_output(self):
        payload = get_step_output_response(
            "run-2026-05-18-09-14", "fetch-hire-record"
        )
        self.assertIs(payload["output"]["ok"], True)
        self.assertEqual(payload["run_id"], "run-2026-05-18-09-14")
        self.assertEqual(payload["step_id"], "fetch-hire-record")

    def test_unknown_step_returns_error_envelope(self):
        payload = get_step_output_response("run-2026-05-18-09-14", "nope")
        self.assertIn("error", payload)
        self.assertEqual(payload["step_id"], "nope")


class SuggestRetryTests(unittest.TestCase):
    def test_swaps_to_canonical_channel_id(self):
        payload = suggest_retry_response("run-2026-05-18-09-14")
        fix = payload["fix"]
        self.assertEqual(payload["failed_step"], "slack-notify")
        self.assertEqual(fix["old_value"], "#new-hires")
        self.assertEqual(fix["new_value"], "C09NEW123HIRE")
        self.assertIn("C09NEW123HIRE", payload["retry_command"])

    def test_unknown_run_returns_error_envelope(self):
        payload = suggest_retry_response("run-not-here")
        self.assertIn("error", payload)
        self.assertIn("hint", payload)


class DiagnosisChainTests(unittest.TestCase):
    """The agent's killer move: list_workflows -> get_workflow_run ->
    get_step_output -> suggest_retry, with every identifier staying
    consistent across the chain.
    """

    def test_chain_is_consistent(self):
        listing = list_workflows_response(active_only=True)
        failed = [w for w in listing["workflows"] if w["last_status"] == "failed"]
        self.assertEqual(len(failed), 1)
        wf = failed[0]
        self.assertEqual(wf["workflow_id"], "wf-onboarding-pro-2026-001")

        run = get_workflow_run_response(wf["last_run_id"])
        self.assertEqual(run["workflow_id"], wf["workflow_id"])
        failed_step = next(s for s in run["steps"] if s["status"] == "failed")
        self.assertEqual(failed_step["step_id"], "slack-notify")

        out = get_step_output_response(run["run_id"], failed_step["step_id"])
        # channel_not_found must appear verbatim — that's the EVIDENCE quote.
        self.assertEqual(out["output"]["error"], "channel_not_found")

        retry = suggest_retry_response(run["run_id"])
        self.assertEqual(retry["failed_step"], "slack-notify")
        self.assertEqual(retry["fix"]["new_value"], "C09NEW123HIRE")
        # The failed step named by the run trace and the retry agree.
        self.assertEqual(retry["failed_step"], failed_step["step_id"])

    def test_retry_old_value_matches_step_output_channel(self):
        """The fix's old_value should be the channel the failed step
        actually attempted, so the remediation is grounded in evidence."""
        out = get_step_output_response("run-2026-05-18-09-14", "slack-notify")
        retry = suggest_retry_response("run-2026-05-18-09-14")
        self.assertEqual(
            retry["fix"]["old_value"], out["output"]["channel_attempted"]
        )


if __name__ == "__main__":
    unittest.main()

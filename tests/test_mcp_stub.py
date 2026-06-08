"""Tests that ``mcp_stub`` re-exports the response builders and data.

``mcp_stub`` keeps a backwards-compatible surface: the canned data tables
and the four response builders are importable from it directly, even when
the ``mcp`` transport package is not installed (the ``mcp`` import is
deferred to :func:`gemini_rpa_agent.mcp_stub._make_server`).

Standard-library ``unittest`` only.
"""

import os
import sys
import unittest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

import gemini_rpa_agent.mcp_stub as stub  # noqa: E402
import gemini_rpa_agent.rpa_data as data  # noqa: E402


class ReExportTests(unittest.TestCase):
    def test_response_builders_reexported(self):
        for name in (
            "list_workflows_response",
            "get_workflow_run_response",
            "get_step_output_response",
            "suggest_retry_response",
        ):
            self.assertTrue(hasattr(stub, name), f"{name} not re-exported")
            # Same object as the canonical definition in rpa_data.
            self.assertIs(getattr(stub, name), getattr(data, name))

    def test_data_tables_reexported(self):
        for name in ("_WORKFLOWS", "_RUNS", "_STEP_OUTPUTS", "_RETRIES"):
            self.assertTrue(hasattr(stub, name), f"{name} not re-exported")
            self.assertIs(getattr(stub, name), getattr(data, name))

    def test_builders_callable_through_stub(self):
        payload = stub.list_workflows_response()
        self.assertEqual(payload["count"], 3)
        out = stub.get_step_output_response("run-2026-05-18-09-14", "slack-notify")
        self.assertEqual(out["output"]["error"], "channel_not_found")

    def test_main_is_exported(self):
        self.assertTrue(callable(stub.main))


if __name__ == "__main__":
    unittest.main()

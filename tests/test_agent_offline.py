"""Tests for the agent / runner behaviour when google-adk is not installed.

The agent and runner are written to degrade gracefully: when the ADK /
Gemini stack is unavailable, ``build_agent`` returns ``None`` and
``runner.ask`` returns an ``AgentResponse`` carrying an offline-fallback
message instead of raising. These tests pin that contract.

If google-adk *is* installed (developer machine, CI with the full
extras), the offline-specific assertions are skipped and the agent is
constructed for real instead.

Standard-library ``unittest`` only.
"""

import os
import sys
import unittest

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from gemini_rpa_agent.agent import _ADK_AVAILABLE, SYSTEM_PROMPT, build_agent  # noqa: E402
from gemini_rpa_agent.runner import AgentResponse, ask  # noqa: E402


class SystemPromptTests(unittest.TestCase):
    def test_prompt_lists_all_five_sections(self):
        for section in (
            "ANSWER:", "EVIDENCE:", "ROOT CAUSE:",
            "REMEDIATION:", "NEXT STEP:",
        ):
            self.assertIn(section, SYSTEM_PROMPT)

    def test_prompt_names_every_tool(self):
        for tool in (
            "list_workflows", "get_workflow_run",
            "get_step_output", "suggest_retry",
        ):
            self.assertIn(tool, SYSTEM_PROMPT)


class BuildAgentOfflineTests(unittest.TestCase):
    @unittest.skipIf(_ADK_AVAILABLE, "google-adk installed; agent builds for real")
    def test_build_agent_returns_none_without_adk(self):
        self.assertIsNone(build_agent(stub=True))

    @unittest.skipUnless(_ADK_AVAILABLE, "requires google-adk")
    def test_build_agent_constructs_with_adk(self):
        agent = build_agent(stub=True)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "gemini_rpa_agent")
        tools = list(getattr(agent, "tools", []) or [])
        self.assertGreaterEqual(len(tools), 1)


class RunnerOfflineTests(unittest.TestCase):
    @unittest.skipIf(_ADK_AVAILABLE, "google-adk installed; runner calls Gemini")
    def test_ask_returns_offline_fallback(self):
        resp = ask("Diagnose the most recent failed run.")
        self.assertIsInstance(resp, AgentResponse)
        self.assertIn("offline-fallback", resp.final_text)
        self.assertIsNotNone(resp.error)
        self.assertEqual(resp.events, [])


if __name__ == "__main__":
    unittest.main()

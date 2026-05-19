"""Real Vertex AI smoke test for gemini-rpa-agent.

Runs the RPA-failure-diagnosis question end-to-end through Gemini 2.5
Flash on the stub RPA MCP server, and verifies the agent walks
list_workflows → get_workflow_run → get_step_output → suggest_retry,
emits all 5 labeled sections, and quotes the verbatim "channel_not_found"
error from the stub.

Usage:
    GOOGLE_CLOUD_PROJECT=careersavvy-mukunda \\
    GOOGLE_GENAI_USE_VERTEXAI=true \\
    GOOGLE_CLOUD_LOCATION=us-central1 \\
    .venv/bin/python scripts/smoke.py
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "careersavvy-mukunda")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from gemini_rpa_agent.runner import ask  # noqa: E402


QUESTION = (
    "Workflow wf-onboarding-pro-2026-001 had a failure at 09:14 UTC. "
    "Walk the RPA tools and tell me which step broke, the verbatim "
    "error payload, and how to fix it."
)


def main() -> int:
    print("== gemini-rpa-agent smoke ==")
    print(f"project={os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"location={os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    print(f"vertexai={os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}")
    print()
    print(f"> {QUESTION}")
    print()

    resp = ask(QUESTION, stub=True)
    print("--- FINAL TEXT ---")
    print(resp.final_text or "(no final text)")
    print("--- END FINAL TEXT ---")
    print(f"events: {len(resp.events)}")

    text = resp.final_text or ""
    upper = text.upper()
    checks = {
        "has ANSWER section":      "ANSWER" in upper,
        "has EVIDENCE section":    "EVIDENCE" in upper,
        "has ROOT CAUSE section":  "ROOT CAUSE" in upper,
        "has REMEDIATION section": "REMEDIATION" in upper,
        "has NEXT STEP section":   "NEXT STEP" in upper,
        "quotes channel_not_found verbatim": "channel_not_found" in text,
        "names wf-onboarding-pro-2026-001":  "wf-onboarding-pro-2026-001" in text,
        "names slack-notify step":           "slack-notify" in text,
    }
    print()
    print("--- CHECKS ---")
    for label, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

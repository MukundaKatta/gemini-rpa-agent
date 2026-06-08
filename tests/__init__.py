"""Test package for gemini-rpa-agent.

Makes the ``src/`` layout importable during plain ``unittest`` discovery
(``python3 -m unittest discover -s tests``) without needing ``pip install
-e .`` or ``PYTHONPATH=src`` to be set first. ``unittest`` imports this
package before loading the test modules, so the path tweak here runs early
enough for ``import gemini_rpa_agent`` to resolve.
"""

import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

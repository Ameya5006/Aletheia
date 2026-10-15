"""Run the real browser workflow against the isolated Compose milestone stack.

This compatibility entrypoint preserves the browser-check command while using
actual registry approval, signed-token verification and PostgreSQL persistence.
No API mocks or host-only database publication are required.
"""

import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "browser", *sys.argv[1:]]
    runpy.run_path(
        str(Path(__file__).with_name("interactive_stack.py")), run_name="__main__"
    )

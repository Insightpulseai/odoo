#!/usr/bin/env python3
"""
scripts/odoo_debugpy_entrypoint.py
---
Thin wrapper that optionally attaches debugpy before handing off to Odoo.

Environment variables (all optional — defaults are safe for production):
  IPAI_DEBUGPY        "1" to enable, "0" or unset to skip  (default: 0)
  IPAI_DEBUGPY_HOST   listen address                        (default: 0.0.0.0)
  IPAI_DEBUGPY_PORT   listen port                           (default: 5678)
  IPAI_DEBUGPY_WAIT   "1" to block until a client attaches  (default: 0)

Usage (compose command override):
  python3 scripts/odoo_debugpy_entrypoint.py -- odoo --config=... [odoo args]

The "--" separator is stripped; everything after it is the Odoo command.
If "--" is absent, all arguments are treated as the Odoo command.

Exit codes mirror the Odoo process exit code.
"""

import os
import sys


def main() -> None:
    args = sys.argv[1:]

    # Strip optional "--" separator
    if "--" in args:
        sep_idx = args.index("--")
        odoo_args = args[sep_idx + 1 :]
    else:
        odoo_args = args

    if not odoo_args:
        # Default: invoke odoo with no extra flags — let compose command supply them.
        # This makes the wrapper a no-op pass-through when args are empty.
        odoo_args = ["odoo"]

    enabled = os.environ.get("IPAI_DEBUGPY", "0") == "1"

    if enabled:
        host = os.environ.get("IPAI_DEBUGPY_HOST", "0.0.0.0")
        port = int(os.environ.get("IPAI_DEBUGPY_PORT", "5678"))
        wait = os.environ.get("IPAI_DEBUGPY_WAIT", "0") == "1"

        try:
            import debugpy  # noqa: PLC0415  (late import is intentional)
        except ImportError:
            print(
                "ERROR: IPAI_DEBUGPY=1 but debugpy is not installed.\n"
                "  Fix: pip install debugpy  OR  rebuild the Docker image.",
                file=sys.stderr,
            )
            sys.exit(1)

        debugpy.listen((host, port))
        print(
            f"[debugpy] listening on {host}:{port}"
            + (" — waiting for client…" if wait else ""),
            flush=True,
        )
        if wait:
            debugpy.wait_for_client()

    # Replace current process with Odoo — preserves signal handling and PID 1
    # behaviour inside containers (no subprocess wrapper overhead).
    os.execvp(odoo_args[0], odoo_args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
scripts/odoo_debugpy_entrypoint.py
---
Thin wrapper that optionally attaches debugpy before handing off to Odoo.

Environment variables (all optional — defaults are safe for production):
  IPAI_DEBUGPY        "1"|"true"|"yes" to enable, anything else → disabled
  IPAI_DEBUGPY_HOST   listen address                (default: 0.0.0.0)
  IPAI_DEBUGPY_PORT   listen port                   (default: 5678)
  IPAI_DEBUGPY_WAIT   "1"|"true"|"yes" — block until a client attaches (default: no)

Usage (compose command override):
  python3 scripts/odoo_debugpy_entrypoint.py -- odoo --config=... [odoo args]

The "--" separator is stripped; everything after it is the Odoo command.
If "--" is absent, all arguments are treated as the Odoo command.

Exit codes:
  0   — Odoo exited cleanly (os.execvp replaces this process, so this is Odoo's exit)
  2   — debugpy requested (IPAI_DEBUGPY=1) but not installed; rebuild with dev image
"""

import json
import os
import sys

_TRUTHY = frozenset(("1", "true", "TRUE", "yes", "YES"))


def _is_truthy(val: str) -> bool:
    return val.strip() in _TRUTHY


def main() -> None:
    args = sys.argv[1:]

    # Strip optional "--" separator
    if "--" in args:
        sep_idx = args.index("--")
        odoo_args = args[sep_idx + 1 :]
    else:
        odoo_args = args

    if not odoo_args:
        # Default: invoke odoo with no extra flags.
        # Makes the wrapper a zero-overhead pass-through when args are empty.
        odoo_args = ["odoo"]

    enabled = _is_truthy(os.environ.get("IPAI_DEBUGPY", "0"))

    if enabled:
        host = os.environ.get("IPAI_DEBUGPY_HOST", "0.0.0.0")
        port = int(os.environ.get("IPAI_DEBUGPY_PORT", "5678"))
        wait = _is_truthy(os.environ.get("IPAI_DEBUGPY_WAIT", "0"))

        try:
            import debugpy  # noqa: PLC0415  (late import — dev-only dependency)
        except ImportError:
            # Exit 2 is distinct from all Odoo exit codes (1 = startup failure).
            # Greppable in CI: DEBUGPY_MISSING
            print(
                "DEBUGPY_MISSING: IPAI_DEBUGPY=1 but debugpy is not installed "
                "in this image. Use the dev image (docker/dev/Dockerfile) or "
                "disable IPAI_DEBUGPY.",
                file=sys.stderr,
            )
            sys.exit(2)

        # Greppable one-line JSON summary for CI log parsing.
        print(
            json.dumps({"ipai_debugpy": True, "port": port, "wait": wait}),
            flush=True,
        )

        debugpy.listen((host, port))
        if wait:
            debugpy.wait_for_client()

    # Replace current process with Odoo — preserves signal handling and PID 1
    # behaviour inside containers (no subprocess wrapper overhead).
    os.execvp(odoo_args[0], odoo_args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
scripts/ci/check_claude_settings_auth.py — Guard: no GH_TOKEN/GITHUB_TOKEN in .claude/settings.json

ROOT CAUSE (documented 2026-03-02):
  Claude Code injects the `env` block from .claude/settings.json into EVERY
  child process's environment BEFORE the process starts. If GH_TOKEN="" (empty
  string) is present, gh CLI sees GH_TOKEN="" and treats that as an explicit
  empty token — it NEVER falls back to the keyring. The keyring is only
  consulted when GH_TOKEN is completely absent from the environment.

  Effect: all GitHub-authenticated tools (gh CLI, MCP GitHub server, VS Code
  GitHub extension, Claude GitHub app) return HTTP 401 Bad credentials until
  the shell is restarted or the variable is manually unset.

  Trigger: someone (or an agent) adds
      "GH_TOKEN": "${GITHUB_TOKEN}"
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
  to the env block. ${GITHUB_TOKEN} expands to empty in most terminals → empty
  string injected → 401 everywhere.

FIX APPLIED:
  Remove GH_TOKEN and GITHUB_TOKEN from .claude/settings.json env block.
  gh CLI authenticates via macOS keyring (jgtolentino account) when neither
  env var is present.

CORRECT PATTERN (GitHub Actions):
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}   ← only in CI jobs, never in settings.json
  gh CLI locally → keyring (gh auth login), no env var needed.

Usage:
  python scripts/ci/check_claude_settings_auth.py           # detect only (CI mode)
  python scripts/ci/check_claude_settings_auth.py --fix     # detect + auto-remove bad entries
  python scripts/ci/check_claude_settings_auth.py --fix --quiet  # fix silently

Exit codes:
  0  — clean (no bad entries, or bad entries removed by --fix)
  1  — bad entries detected (--fix not requested, or removal failed)
"""

import json
import sys
import argparse
from pathlib import Path

SETTINGS_PATH = Path(".claude/settings.json")

# Any of these keys in the env block will trigger a failure.
# Real PATs are never stored here — gh CLI uses keyring locally,
# GITHUB_TOKEN is injected by the Actions runner in CI jobs only.
FORBIDDEN_ENV_KEYS = {"GH_TOKEN", "GITHUB_TOKEN"}


def load_settings(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def save_settings(path: Path, data: dict) -> None:
    with path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def check(settings: dict) -> list[str]:
    """Return list of offending keys found in settings.env."""
    env_block = settings.get("env", {})
    return [k for k in FORBIDDEN_ENV_KEYS if k in env_block]


def fix(settings: dict, bad_keys: list[str]) -> dict:
    """Remove bad keys from settings.env and return the modified dict."""
    for k in bad_keys:
        settings["env"].pop(k, None)
    return settings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard: prevent GH_TOKEN/GITHUB_TOKEN in .claude/settings.json"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-remove bad env entries (default: detect only)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output (errors always shown)",
    )
    parser.add_argument(
        "--path",
        default=str(SETTINGS_PATH),
        help=f"Path to settings.json (default: {SETTINGS_PATH})",
    )
    args = parser.parse_args()

    path = Path(args.path)

    if not path.exists():
        if not args.quiet:
            print(f"OK: {path} not found — nothing to check.")
        return 0

    try:
        settings = load_settings(path)
    except json.JSONDecodeError as e:
        print(f"ERROR: {path} is not valid JSON: {e}", file=sys.stderr)
        return 1

    bad_keys = check(settings)

    if not bad_keys:
        if not args.quiet:
            print(f"OK: {path} — no forbidden GitHub token env vars detected.")
        return 0

    # Bad keys found
    print(
        f"ERROR: {path} has forbidden env keys: {bad_keys}",
        file=sys.stderr,
    )
    print(
        """
ROOT CAUSE: Claude Code injects the 'env' block into every child process.
  GH_TOKEN="" (empty string) overrides the gh CLI keyring → HTTP 401 everywhere.

FIX: Remove GH_TOKEN / GITHUB_TOKEN from .claude/settings.json env block.
  gh CLI authenticates via keyring locally (gh auth login → jgtolentino).
  In GitHub Actions: inject GH_TOKEN: ${{ secrets.GITHUB_TOKEN }} per-job only.

Run:  python scripts/ci/check_claude_settings_auth.py --fix
""",
        file=sys.stderr,
    )

    if args.fix:
        settings = fix(settings, bad_keys)
        save_settings(path, settings)
        if not args.quiet:
            print(f"FIXED: removed {bad_keys} from {path}.env block.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

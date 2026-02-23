#!/usr/bin/env bash
# Copyright 2026 InsightPulse AI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
# Git safety preflight — run before any agent commit to guard against
# concurrent git processes and corrupted index state.
#
# Exit codes:
#   0  safe to proceed
#   2  unsafe — caller must NOT delete index.lock or force-continue
#
# Usage:
#   ./scripts/git_safety_preflight.sh
#   # then:
#   git add <files> && git commit -m "..."
#
# Agent integration:
#   Call this script before every git commit in agent workflows.
#   Never delete .git/index.lock automatically — stop and report.
#
set -euo pipefail

SCRIPT="[git_safety_preflight]"

# ── 1. Lock file guard ────────────────────────────────────────────────────────
LOCK=".git/index.lock"
if [ -f "$LOCK" ]; then
    echo "$SCRIPT ERROR: $LOCK exists." >&2
    echo "$SCRIPT Another git process may be running (editor, rebase, cherry-pick, CI runner)." >&2
    echo "$SCRIPT Resolution:" >&2
    echo "$SCRIPT   1. Check for running processes: lsof | grep 'index.lock'" >&2
    echo "$SCRIPT   2. If no process holds the lock AND you are certain no concurrent git op is running:" >&2
    echo "$SCRIPT      rm $LOCK  (manual — never automated)" >&2
    echo "$SCRIPT   3. Re-run this preflight." >&2
    exit 2
fi

# ── 2. Repo integrity check ───────────────────────────────────────────────────
if ! git status --porcelain >/dev/null 2>&1; then
    echo "$SCRIPT ERROR: 'git status' failed. Repo may be in a bad state." >&2
    echo "$SCRIPT Resolution: check for ongoing rebase/merge/cherry-pick (see .git/CHERRY_PICK_HEAD, MERGE_HEAD, REBASE_MERGE)." >&2
    exit 2
fi

# ── 3. Mid-operation guard ────────────────────────────────────────────────────
for STATE_FILE in ".git/CHERRY_PICK_HEAD" ".git/REBASE_MERGE" ".git/MERGE_HEAD"; do
    if [ -e "$STATE_FILE" ]; then
        echo "$SCRIPT WARNING: $STATE_FILE exists — a git operation is in progress." >&2
        echo "$SCRIPT Finish or abort it before committing (cherry-pick --continue/--abort, rebase --abort, etc.)." >&2
        # Warn but don't block — some agents legitimately commit mid-cherry-pick
    fi
done

echo "$SCRIPT OK"

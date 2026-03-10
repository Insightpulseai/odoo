#!/usr/bin/env bash
# git_state_preflight.sh — hard-fail if git is mid-operation
# Run before any automation that does git add/commit/push.
# Exit 0 = clean state. Exit 2 = unsafe to proceed.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

fail() { echo "[git_state_preflight] ERROR: $*" >&2; exit 2; }

[ -f .git/index.lock ]   && fail ".git/index.lock exists (another git process running?)."
[ -d .git/sequencer ]    && fail "cherry-pick/revert sequence in progress (run: git cherry-pick --abort)."
[ -f .git/CHERRY_PICK_HEAD ] && fail "cherry-pick in progress (run: git cherry-pick --abort)."
[ -f .git/MERGE_HEAD ]   && fail "merge in progress (run: git merge --abort)."
[ -d .git/rebase-apply ] && fail "rebase in progress (run: git rebase --abort)."
[ -d .git/rebase-merge ] && fail "rebase in progress (run: git rebase --abort)."

echo "[git_state_preflight] OK — clean git state"

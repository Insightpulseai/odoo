#!/usr/bin/env bash
set -euo pipefail

# Structured Output Wrapper (Paste-to-ChatGPT Optimized)
# Usage:
#   structured_output.sh "<task_slug>" "<goal>" -- <command...>
#
# Example:
#   structured_output.sh colima-audit "Run audit + summarize severity" -- pnpm audit

TASK_SLUG="${1:-}"
GOAL="${2:-}"
shift 2 || true

if [[ "${1:-}" != "--" ]]; then
  echo "BLOCKER: missing '--' separator before command"
  echo "Example: structured_output.sh <task_slug> <goal> -- <command...>"
  exit 2
fi
shift

if [[ -z "${TASK_SLUG}" || -z "${GOAL}" || $# -lt 1 ]]; then
  echo "BLOCKER: missing task_slug, goal, or command"
  echo "Example: structured_output.sh colima-audit \"Run audit\" -- pnpm audit"
  exit 2
fi

# Prefer Asia/Manila stamp (UTC+08:00). Avoid relying on system TZ configuration.
STAMP="$(TZ=Asia/Manila date +"%Y%m%d-%H%M+0800")"
STAMP_ISO="$(TZ=Asia/Manila date -Iseconds)"

# Repo detection
REPO_ROOT="not a git repo"
BRANCH="detached/unknown"
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
  BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached/unknown")"
fi
CWD="$(pwd)"

EVID_DIR="${REPO_ROOT}/docs/evidence/${STAMP}/${TASK_SLUG}/logs"
if [[ "${REPO_ROOT}" == "not a git repo" ]]; then
  # fall back to current dir evidence folder
  EVID_DIR="${CWD}/docs/evidence/${STAMP}/${TASK_SLUG}/logs"
fi
mkdir -p "${EVID_DIR}"

CMD_LOG="${EVID_DIR}/command.txt"
OUT_LOG="${EVID_DIR}/stdout_stderr.txt"
STATUS_LOG="${EVID_DIR}/status.txt"
GIT_STATUS_LOG="${EVID_DIR}/git_status_porcelain.txt"
GIT_DIFFSTAT_LOG="${EVID_DIR}/git_diff_stat.txt"

printf "%s\n" "$*" > "${CMD_LOG}"

echo "[CONTEXT]"
echo "- repo: ${REPO_ROOT}"
echo "- branch: ${BRANCH}"
echo "- cwd: ${CWD}"
echo "- goal: ${GOAL}"
echo "- stamp: ${STAMP_ISO}"
echo
echo "[CHANGES]"
echo "- (pending; see git status/diffstat evidence after command)"
echo
echo "[EVIDENCE]"
echo "- command: $*"
echo "  saved_to: ${OUT_LOG}"
echo

set +e
("$@" 2>&1) | tee "${OUT_LOG}"
EXIT_CODE="${PIPESTATUS[0]}"
set -e

if [[ "${EXIT_CODE}" -eq 0 ]]; then
  echo "PASS" > "${STATUS_LOG}"
  RESULT_LINE="PASS (exit 0)"
else
  echo "FAIL (exit ${EXIT_CODE})" > "${STATUS_LOG}"
  RESULT_LINE="FAIL (exit ${EXIT_CODE})"
fi

echo "[DIFF SUMMARY]"
if [[ "${REPO_ROOT}" != "not a git repo" ]]; then
  (cd "${REPO_ROOT}" && git diff --stat) | tee "${GIT_DIFFSTAT_LOG}" >/dev/null || true
  echo "- saved_to: ${GIT_DIFFSTAT_LOG}"
else
  echo "- (not a git repo)"
fi
echo

echo "[NEXT - DETERMINISTIC]"
echo "- result: ${RESULT_LINE}"
echo "- evidence:"
echo "  - cmd: ${CMD_LOG}"
echo "  - out: ${OUT_LOG}"
echo "  - status: ${STATUS_LOG}"
if [[ "${REPO_ROOT}" != "not a git repo" ]]; then
  (cd "${REPO_ROOT}" && git status --porcelain) | tee "${GIT_STATUS_LOG}" >/dev/null || true
  echo "  - git_status: ${GIT_STATUS_LOG}"
  echo "  - diffstat: ${GIT_DIFFSTAT_LOG}"
fi

exit "${EXIT_CODE}"

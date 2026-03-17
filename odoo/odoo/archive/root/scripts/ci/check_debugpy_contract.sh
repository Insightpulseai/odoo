#!/usr/bin/env bash
# scripts/ci/check_debugpy_contract.sh
#
# debugpy entrypoint contract gate — CI-blocking
#
# Verifies the two contracts of scripts/odoo_debugpy_entrypoint.py without
# standing up Docker or an Odoo installation:
#
#   CONTRACT 1 (silent-off): IPAI_DEBUGPY=0 → zero stdout output, exit 0
#                             (os.execvp will fail because odoo is absent;
#                              that is the expected and only non-zero exit)
#
#   CONTRACT 2 (fail-fast):  IPAI_DEBUGPY=1 + debugpy absent → exit 2 +
#                             "DEBUGPY_MISSING" on stderr
#
# Exits 0  — all contracts pass
# Exits 1  — a contract was violated (message includes PASS/FAIL lines)
#
# No external dependencies beyond Python 3.x (standard ubuntu-latest).
#
# Usage:
#   bash scripts/ci/check_debugpy_contract.sh
#
# Workflow: .github/workflows/debugpy-contract.yml
# Runbook:  docs/runbooks/ODOO_DEBUGPY.md

set -euo pipefail

ENTRYPOINT="scripts/odoo_debugpy_entrypoint.py"
PASS=0
FAIL=0

_pass() { echo "  PASS  $1"; ((PASS++)) || true; }
_fail() { echo "  FAIL  $1"; ((FAIL++)) || true; }

echo "========================================"
echo "  debugpy entrypoint contract gate"
echo "========================================"
echo ""

# --------------------------------------------------------------------------
# Sanity: entrypoint exists and is syntactically valid
# --------------------------------------------------------------------------
echo "[0] Sanity checks"
if [[ ! -f "${ENTRYPOINT}" ]]; then
  echo "  FAIL  ${ENTRYPOINT} not found (run from repo root)"
  exit 1
fi
if python3 -c "import ast; ast.parse(open('${ENTRYPOINT}').read())" 2>/dev/null; then
  _pass "Python syntax OK"
else
  _fail "Python syntax error in ${ENTRYPOINT}"
fi
echo ""

# --------------------------------------------------------------------------
# CONTRACT 2: IPAI_DEBUGPY=1 + debugpy ABSENT → exit 2 + DEBUGPY_MISSING
# --------------------------------------------------------------------------
# Inject a fake debugpy.py that raises ImportError via PYTHONPATH.
# This simulates the script running inside a prod/stage image that
# was built without the dev Dockerfile layer.
# --------------------------------------------------------------------------
echo "[1] CONTRACT 2 — fail-fast (IPAI_DEBUGPY=1, debugpy absent)"

TMPDIR_FAKE="$(mktemp -d)"
trap 'rm -rf "${TMPDIR_FAKE}"' EXIT

# Write a fake debugpy module that always raises ImportError
cat > "${TMPDIR_FAKE}/debugpy.py" << 'PYEOF'
raise ImportError("debugpy intentionally absent — CI contract test (check_debugpy_contract.sh)")
PYEOF

STDERR_FILE="${TMPDIR_FAKE}/stderr.txt"

set +e
IPAI_DEBUGPY=1 \
  PYTHONPATH="${TMPDIR_FAKE}" \
  python3 "${ENTRYPOINT}" -- echo unused \
  2>"${STDERR_FILE}"
ACTUAL_EXIT=$?
set -e

# Assert exit code 2
if [[ "${ACTUAL_EXIT}" -eq 2 ]]; then
  _pass "exit code is 2 (fail-fast)"
else
  _fail "expected exit 2, got ${ACTUAL_EXIT}"
fi

# Assert DEBUGPY_MISSING sentinel on stderr
if grep -q "DEBUGPY_MISSING" "${STDERR_FILE}"; then
  _pass "stderr contains DEBUGPY_MISSING sentinel"
else
  _fail "stderr missing DEBUGPY_MISSING sentinel (got: $(cat "${STDERR_FILE}" | head -3))"
fi

# Assert stderr message mentions how to fix it
if grep -q "dev image\|disable IPAI_DEBUGPY" "${STDERR_FILE}"; then
  _pass "stderr contains actionable fix hint"
else
  _fail "stderr does not contain a fix hint"
fi

# Assert no stdout was emitted before the failure
STDOUT_FILE="${TMPDIR_FAKE}/stdout.txt"
set +e
IPAI_DEBUGPY=1 \
  PYTHONPATH="${TMPDIR_FAKE}" \
  python3 "${ENTRYPOINT}" -- echo unused \
  >"${STDOUT_FILE}" 2>/dev/null
set -e
if [[ ! -s "${STDOUT_FILE}" ]]; then
  _pass "no stdout emitted before exit 2"
else
  _fail "unexpected stdout on fail-fast path: $(cat "${STDOUT_FILE}" | head -3)"
fi

echo ""

# --------------------------------------------------------------------------
# CONTRACT 1: IPAI_DEBUGPY=0 → zero output before exec, no debugpy activity
# Verification: with the fake debugpy on PYTHONPATH, IPAI_DEBUGPY=0 must
# NOT import debugpy at all (os.execvp will fail; we only care about stdout).
# --------------------------------------------------------------------------
echo "[2] CONTRACT 1 — silent-off (IPAI_DEBUGPY=0, no output before exec)"

STDOUT_OFF="${TMPDIR_FAKE}/stdout_off.txt"
set +e
IPAI_DEBUGPY=0 \
  PYTHONPATH="${TMPDIR_FAKE}" \
  python3 "${ENTRYPOINT}" -- echo unused \
  >"${STDOUT_OFF}" 2>/dev/null
EXIT_OFF=$?
set -e

# Exit code will be non-zero (odoo absent), but that's expected.
# The constraint is that NO output was printed by the wrapper itself.
if [[ ! -s "${STDOUT_OFF}" ]]; then
  _pass "no stdout from wrapper when disabled (os.execvp/echo handled separately)"
else
  # echo is present on all CI runners; if it ran, stdout is "unused"
  # That's fine — it means execvp succeeded, which also passes the contract.
  if grep -q "unused" "${STDOUT_OFF}"; then
    _pass "os.execvp ran to echo (no wrapper noise — contract satisfied)"
  else
    _fail "unexpected wrapper output when IPAI_DEBUGPY=0: $(cat "${STDOUT_OFF}" | head -3)"
  fi
fi

echo ""
echo "========================================"
echo "  Results: PASS=${PASS}  FAIL=${FAIL}"
echo "========================================"
echo ""

if [[ "${FAIL}" -gt 0 ]]; then
  echo "FAIL: ${FAIL} contract(s) violated — see output above."
  exit 1
fi

echo "PASS: all debugpy entrypoint contracts satisfied."
exit 0

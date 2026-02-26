#!/usr/bin/env bash
# run_e2e_mailgun_text.sh -- Run Mailgun text e2e test inside odoo-prod container
#
# Usage:
#   bash scripts/mail/run_e2e_mailgun_text.sh
#   TO_EMAIL=other@example.com bash scripts/mail/run_e2e_mailgun_text.sh
#
# Writes evidence artifacts under web/docs/evidence/<YYYYMMDD-HHMM+0800>/mailgun-text-e2e/
# Exits 0 on PASS, non-zero on failure.

set -euo pipefail

CONTAINER="odoo-prod"
SCRIPT_SRC="scripts/mail/e2e_mailgun_text.py"
SCRIPT_DST="/tmp/e2e_mailgun_text.py"
TO_EMAIL="${TO_EMAIL:-jgtolentino.rn@gmail.com}"

STAMP="$(TZ=Asia/Manila date +%Y%m%d-%H%M%S+0800)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
EVIDENCE_DIR="${REPO_ROOT}/web/docs/evidence/${STAMP:0:13}+0800/mailgun-text-e2e"
mkdir -p "${EVIDENCE_DIR}/logs"

LOG_FILE="${EVIDENCE_DIR}/logs/e2e_run.log"
MAIL_LOG="${EVIDENCE_DIR}/logs/mail_mail_tail.txt"

echo "[run_e2e_mailgun_text] stamp: ${STAMP}"
echo "[run_e2e_mailgun_text] evidence: ${EVIDENCE_DIR}"
echo ""

# Copy script into container
docker cp "${REPO_ROOT}/${SCRIPT_SRC}" "${CONTAINER}:${SCRIPT_DST}"

# Run test, capturing output
set +e
TO_EMAIL="${TO_EMAIL}" docker exec \
  -e TO_EMAIL="${TO_EMAIL}" \
  "${CONTAINER}" \
  python3 "${SCRIPT_DST}" 2>&1 | tee "${LOG_FILE}"
EXIT_CODE=${PIPESTATUS[0]}
set -e

# Capture last 5 mail.mail rows
docker exec "${CONTAINER}" \
  bash -c "python3 -c \"
import odoo.tools.config
odoo.tools.config.parse_config(['--config=/etc/odoo/odoo.conf'])
from odoo.modules.registry import Registry
from odoo import api
reg = Registry('odoo_prod')
with reg.cursor() as cr:
    env = api.Environment(cr, 1, {})
    rows = env['mail.mail'].search([], order='id desc', limit=5)
    for r in rows:
        print(r.id, r.subject[:40] if r.subject else '-', r.email_from, r.state, r.failure_reason or '')
\"" 2>/dev/null > "${MAIL_LOG}" || true

echo ""
echo "[run_e2e_mailgun_text] logs: ${LOG_FILE}"
echo "[run_e2e_mailgun_text] mail_mail tail: ${MAIL_LOG}"

if [[ "${EXIT_CODE}" -eq 0 ]]; then
  echo "[run_e2e_mailgun_text] PASS -- exit ${EXIT_CODE}"
else
  echo "[run_e2e_mailgun_text] FAIL -- exit ${EXIT_CODE}"
fi

exit "${EXIT_CODE}"

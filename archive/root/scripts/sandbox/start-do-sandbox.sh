#!/usr/bin/env bash
set -euo pipefail

DO_HOST="${DO_HOST:-178.128.112.214}"
REMOTE_DIR="${REMOTE_DIR:-/opt/odoo-ce/repo}"
BRANCH="${BRANCH:-claude/odoo-oca-enterprise-image-TLHuU}"

echo "Connecting to ${DO_HOST} and running CE19 build/test in ${REMOTE_DIR} on branch ${BRANCH}..."

ssh "root@${DO_HOST}" << EOF
  set -euo pipefail
  cd "${REMOTE_DIR}"
  git fetch origin "${BRANCH}"
  git checkout "${BRANCH}"
  ./docker/build-ce19.sh
  ./docker/test-ce19.sh || { echo "❌ CE19 test failed"; exit 1; }
  echo "✅ CE19 build + test completed on ${DO_HOST}"
EOF

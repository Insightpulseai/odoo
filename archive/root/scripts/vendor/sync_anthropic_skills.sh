#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REPO="https://github.com/anthropics/skills.git"
UPSTREAM_REF="${UPSTREAM_REF:-main}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEST_DIR="${ROOT_DIR}/third_party/anthropic_skills"
TMP_DIR="${ROOT_DIR}/.tmp/vendor/anthropic_skills"

mkdir -p "${DEST_DIR}" "${TMP_DIR}"

if [[ -d "${TMP_DIR}/.git" ]]; then
  git -C "${TMP_DIR}" fetch --prune origin
else
  rm -rf "${TMP_DIR}"
  git clone --filter=blob:none --no-checkout "${UPSTREAM_REPO}" "${TMP_DIR}"
  git -C "${TMP_DIR}" remote set-url origin "${UPSTREAM_REPO}"
  git -C "${TMP_DIR}" fetch --prune origin
fi

git -C "${TMP_DIR}" checkout -f "${UPSTREAM_REF}"

# Replace mirror contents, but preserve our local README.md.
if [[ -f "${DEST_DIR}/README.md" ]]; then
  cp "${DEST_DIR}/README.md" "${DEST_DIR}/.README.local.bak"
fi
rm -rf "${DEST_DIR:?}/"*
cp -R "${TMP_DIR}/." "${DEST_DIR}/"
rm -rf "${DEST_DIR}/.git" || true
if [[ -f "${DEST_DIR}/.README.local.bak" ]]; then
  mv "${DEST_DIR}/.README.local.bak" "${DEST_DIR}/README.md"
fi

# Record upstream SHA for reproducibility
UPSTREAM_SHA="$(git -C "${TMP_DIR}" rev-parse HEAD)"
echo "${UPSTREAM_SHA}" > "${DEST_DIR}/UPSTREAM_REV.txt"

echo "Synced anthropics/skills @ ${UPSTREAM_REF} (${UPSTREAM_SHA}) into third_party/anthropic_skills"

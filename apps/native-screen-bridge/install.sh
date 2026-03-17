#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOST_NAME="com.insightpulseai.screen"
MANIFEST_SRC="${SCRIPT_DIR}/manifest/${HOST_NAME}.json"

# Chrome native messaging hosts directory
CHROME_NM_DIR="${HOME}/Library/Application Support/Google/Chrome/NativeMessagingHosts"

mkdir -p "${CHROME_NM_DIR}"

# Update path in manifest to point to this installation
MANIFEST_DEST="${CHROME_NM_DIR}/${HOST_NAME}.json"
sed "s|/Users/tbwa/Documents/GitHub/Insightpulseai/odoo/apps/native-screen-bridge/src/host.py|${SCRIPT_DIR}/src/host.py|" \
  "${MANIFEST_SRC}" > "${MANIFEST_DEST}"

chmod +x "${SCRIPT_DIR}/src/host.py"

echo "Installed native messaging host: ${MANIFEST_DEST}"
echo "Host script: ${SCRIPT_DIR}/src/host.py"
echo ""
echo "NOTE: Update 'allowed_origins' in ${MANIFEST_DEST} with your extension ID."
echo "Find it at chrome://extensions after loading the extension."

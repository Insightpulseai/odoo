#!/usr/bin/env bash
set -euo pipefail

# Usage: notify_slack.sh <status>

STATUS="${1:-unknown}"
WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

if [ -z "$WEBHOOK_URL" ]; then
  echo "SLACK_WEBHOOK_URL not set, skipping Slack notification."
  exit 0
fi

REPO="${GITHUB_REPOSITORY:-unknown}"
WORKFLOW="${GITHUB_WORKFLOW:-unknown}"
RUN_ID="${GITHUB_RUN_ID:-unknown}"
BRANCH="${GITHUB_REF_NAME:-unknown}"

# Pick color based on status
COLOR="#36a64f" # green/success
if [ "$STATUS" == "failure" ]; then
  COLOR="#cb2431" # red
elif [ "$STATUS" == "cancelled" ]; then
  COLOR="#ff9f1c" # orange
fi

# Construct JSON payload
# Using attachments for color coding
read -r -d '' PAYLOAD <<EOF
{
  "attachments": [
    {
      "color": "${COLOR}",
      "text": "*${REPO}* - ${WORKFLOW} #${GITHUB_RUN_NUMBER}\nStatus: *${STATUS}*\nBranch: \`${BRANCH}\`\n<https://github.com/${REPO}/actions/runs/${RUN_ID}|View Logs>",
      "mrkdwn_in": ["text"]
    }
  ]
}
EOF

# Send to Slack
curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$WEBHOOK_URL"

echo "Slack notification sent for status: $STATUS"

/**
 * Slack notification for Vercel integrations drift events.
 *
 * Posts a structured message to SLACK_WEBHOOK_URL when drift is detected.
 * Silent on no-drift runs.
 */

import type { DiffResult } from "./diff.js";

export async function slackNotify(
  webhookUrl: string,
  diff: DiffResult,
  issueUrl?: string
): Promise<void> {
  if (!diff.has_drift) return; // Nothing to report

  const counts = [
    diff.added.length > 0 ? `+${diff.added.length} added` : null,
    diff.removed.length > 0 ? `-${diff.removed.length} removed` : null,
    diff.changed.length > 0 ? `~${diff.changed.length} changed` : null,
  ]
    .filter(Boolean)
    .join(", ");

  const blocks = [
    {
      type: "header",
      text: {
        type: "plain_text",
        text: `⚠️ Vercel Integrations Drift — Team ${diff.team_id}`,
        emoji: true,
      },
    },
    {
      type: "section",
      fields: [
        { type: "mrkdwn", text: `*Team ID*\n${diff.team_id}` },
        { type: "mrkdwn", text: `*Changes*\n${counts}` },
        {
          type: "mrkdwn",
          text: `*Before*\n${diff.before_captured_at}`,
        },
        {
          type: "mrkdwn",
          text: `*After*\n${diff.after_captured_at}`,
        },
      ],
    },
  ];

  if (diff.added.length > 0) {
    blocks.push({
      type: "section",
      fields: [
        {
          type: "mrkdwn",
          text: `*➕ Added*\n${diff.added.map((i) => `\`${i.slug}\``).join(", ")}`,
        },
      ],
    } as never);
  }

  if (diff.removed.length > 0) {
    blocks.push({
      type: "section",
      fields: [
        {
          type: "mrkdwn",
          text: `*➖ Removed*\n${diff.removed.map((i) => `\`${i.slug}\``).join(", ")}`,
        },
      ],
    } as never);
  }

  if (issueUrl) {
    blocks.push({
      type: "section",
      text: { type: "mrkdwn", text: `<${issueUrl}|View GitHub Issue →>` },
    } as never);
  }

  const res = await fetch(webhookUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ blocks }),
  });

  if (!res.ok) {
    throw new Error(`Slack webhook failed: ${res.status} ${await res.text()}`);
  }
}

// server/lib/notify.ts
// Post run results back to Slack using the bot token.
//
// Uses @slack/web-api WebClient for type-safe API calls.
// Call this from agent workers (Edge Functions or queue consumers)
// AFTER a run completes — never from the inbound webhook handler
// (which must ACK immediately).
//
// SSOT contract: Slack notifications are fire-and-forget.
//   Failures are logged to ops.run_events but do not fail the run.

import { WebClient } from '@slack/web-api'

let _client: WebClient | null = null

function getWebClient(token: string): WebClient {
  if (!_client) {
    _client = new WebClient(token)
  }
  return _client
}

export interface SlackMessage {
  channel: string
  text: string
  /** Optional: reply to a thread */
  threadTs?: string
  /** Optional: Block Kit blocks for rich formatting */
  blocks?: unknown[]
}

/**
 * Post a message to a Slack channel (or thread).
 * Returns the ts (message timestamp) on success, null on error.
 */
export async function postSlackMessage(
  botToken: string,
  msg: SlackMessage,
): Promise<string | null> {
  const client = getWebClient(botToken)
  try {
    const res = await client.chat.postMessage({
      channel: msg.channel,
      text: msg.text,
      thread_ts: msg.threadTs,
      blocks: msg.blocks as Parameters<typeof client.chat.postMessage>[0]['blocks'],
    })
    return res.ts ?? null
  } catch (err) {
    // Log but don't throw — notification failure is non-fatal
    console.error('[slack-notify] postMessage error:', err instanceof Error ? err.message : String(err))
    return null
  }
}

/**
 * Format a run result as a Slack Block Kit message.
 * Produces a compact summary card.
 */
export function formatRunResult(opts: {
  runId: string
  status: 'completed' | 'failed'
  jobType: string
  output?: Record<string, unknown>
  error?: string
}): { text: string; blocks: unknown[] } {
  const icon = opts.status === 'completed' ? '✅' : '❌'
  const title = `${icon} Run \`${opts.runId.slice(0, 8)}\` — ${opts.jobType}`

  const blocks: unknown[] = [
    {
      type: 'section',
      text: { type: 'mrkdwn', text: `*${title}*` },
    },
  ]

  if (opts.status === 'failed' && opts.error) {
    blocks.push({
      type: 'section',
      text: { type: 'mrkdwn', text: `*Error:* ${opts.error}` },
    })
  }

  if (opts.output && Object.keys(opts.output).length > 0) {
    const summary = JSON.stringify(opts.output, null, 2).slice(0, 2000)
    blocks.push({
      type: 'section',
      text: { type: 'mrkdwn', text: `\`\`\`${summary}\`\`\`` },
    })
  }

  return { text: title, blocks }
}

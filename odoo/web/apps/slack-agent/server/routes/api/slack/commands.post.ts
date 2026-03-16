// server/routes/api/slack/commands.post.ts
// POST /api/slack/commands — Slack Slash Commands endpoint
//
// Slack sends application/x-www-form-urlencoded with fields:
//   command, text, trigger_id, user_id, user_name, channel_id, team_id, response_url
//
// Contract:
//   1. Verify signature
//   2. ACK 200 with immediate text response (Slack shows ephemeral message)
//   3. Enqueue ops.run async for actual processing
//   4. Use response_url for async follow-up if needed (from the worker)

import { defineEventHandler, readRawBody, getHeader, setResponseStatus, send } from 'h3'
import { useRuntimeConfig } from 'nitropack/runtime'
import { verifySlackSignature } from '../../../lib/verify'
import { slackCommandKey } from '../../../lib/idempotency'
import { enqueueSlackRun, resolveSlackCommand } from '../../../lib/taskbus'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)

  const rawBody = await readRawBody(event, false) ?? ''
  const timestamp = getHeader(event, 'x-slack-request-timestamp') ?? null
  const signature = getHeader(event, 'x-slack-signature') ?? null
  const signingSecret = (config.slackSigningSecret as string) || process.env.SLACK_SIGNING_SECRET || ''

  // Step 1: Verify signature
  const verifyErr = await verifySlackSignature(signingSecret, rawBody, timestamp, signature)
  if (verifyErr) {
    setResponseStatus(event, 401)
    return send(event, JSON.stringify({ error: verifyErr }), 'application/json')
  }

  // Step 2: Decode URL-encoded slash command payload
  const rawStr = typeof rawBody === 'string' ? rawBody : new TextDecoder().decode(rawBody)
  const params = new URLSearchParams(rawStr)

  const command = params.get('command') ?? ''
  const text = params.get('text') ?? ''
  const triggerId = params.get('trigger_id') ?? ''
  const userId = params.get('user_id') ?? ''
  const channelId = params.get('channel_id') ?? ''
  const teamId = params.get('team_id') ?? ''
  const responseUrl = params.get('response_url') ?? ''

  const route = resolveSlackCommand(command)

  // Step 3: ACK immediately with ephemeral message
  const ackText = route
    ? `Processing \`${command}${text ? ' ' + text : ''}\`… I'll let you know when it's done.`
    : `Unknown command \`${command}\`. No handler registered.`

  setResponseStatus(event, 200)
  send(
    event,
    JSON.stringify({ response_type: 'ephemeral', text: ackText }),
    'application/json',
  )

  if (!route || !triggerId) return

  // Step 4: Enqueue async
  const supabaseUrl = (config.supabaseUrl as string) || process.env.SUPABASE_URL || ''
  const supabaseKey = (config.supabaseServiceRoleKey as string) || process.env.SUPABASE_SERVICE_ROLE_KEY || ''

  enqueueSlackRun({
    ...route,
    idempotencyKey: slackCommandKey(command, triggerId),
    input: {
      command,
      text,
      trigger_id: triggerId,
      user_id: userId,
      channel_id: channelId,
      team_id: teamId,
      response_url: responseUrl,
    },
    supabaseUrl,
    supabaseServiceRoleKey: supabaseKey,
  }).catch((err: unknown) => {
    console.error('[slack-commands] enqueue error:', err instanceof Error ? err.message : String(err))
  })
})

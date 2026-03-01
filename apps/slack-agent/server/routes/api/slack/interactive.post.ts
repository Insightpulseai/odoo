// server/routes/api/slack/interactive.post.ts
// POST /api/slack/interactive — Slack Interactivity endpoint
//
// Handles: button clicks, modal submits, overflow menus, select menus.
// Slack sends application/x-www-form-urlencoded with a "payload" field.
//
// Contract:
//   1. Verify signature
//   2. Parse payload JSON from form body
//   3. ACK 200 immediately (Slack shows spinner until ACK)
//   4. Enqueue ops.run for the interaction async

import { defineEventHandler, readRawBody, getHeader, setResponseStatus, send } from 'h3'
import { useRuntimeConfig } from 'nitropack/runtime'
import { verifySlackSignature } from '../../../lib/verify'
import { slackInteractionKey } from '../../../lib/idempotency'
import { enqueueSlackRun } from '../../../lib/taskbus'

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

  // Step 2: Decode URL-encoded body → extract "payload" field
  const rawStr = typeof rawBody === 'string' ? rawBody : new TextDecoder().decode(rawBody)
  const params = new URLSearchParams(rawStr)
  const payloadStr = params.get('payload')

  if (!payloadStr) {
    setResponseStatus(event, 400)
    return send(event, JSON.stringify({ error: 'Missing payload field' }), 'application/json')
  }

  let payload: Record<string, unknown>
  try {
    payload = JSON.parse(payloadStr)
  } catch {
    setResponseStatus(event, 400)
    return send(event, JSON.stringify({ error: 'Invalid payload JSON' }), 'application/json')
  }

  const triggerId = payload.trigger_id as string | undefined
  const interactionType = payload.type as string | undefined

  // Step 3: ACK immediately
  setResponseStatus(event, 200)
  send(event, '', 'text/plain')

  // Step 4: Enqueue async
  if (!triggerId) return  // Can't build idempotency key without trigger_id

  const supabaseUrl = (config.supabaseUrl as string) || process.env.SUPABASE_URL || ''
  const supabaseKey = (config.supabaseServiceRoleKey as string) || process.env.SUPABASE_SERVICE_ROLE_KEY || ''

  enqueueSlackRun({
    jobType: `slack.interactive.${interactionType ?? 'unknown'}`,
    agent: 'slack-copilot-agent',
    idempotencyKey: slackInteractionKey(triggerId),
    input: {
      interaction_type: interactionType,
      trigger_id: triggerId,
      user: payload.user,
      actions: payload.actions,
      view: payload.view,
      callback_id: (payload.view as Record<string, unknown> | undefined)?.callback_id
        ?? (payload.actions as Array<Record<string, unknown>> | undefined)?.[0]?.action_id,
    },
    supabaseUrl,
    supabaseServiceRoleKey: supabaseKey,
  }).catch((err: unknown) => {
    console.error('[slack-interactive] enqueue error:', err instanceof Error ? err.message : String(err))
  })
})

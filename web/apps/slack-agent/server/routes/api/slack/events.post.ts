// server/routes/api/slack/events.post.ts
// POST /api/slack/events — Slack Events API endpoint
//
// Contract:
//   1. Verify X-Slack-Signature immediately (reject 401 on failure)
//   2. Handle URL verification challenge (type: "url_verification") → return {challenge}
//   3. ACK 200 instantly — never block on taskbus or DB writes
//   4. Enqueue ops.run async (non-blocking) for event processing
//
// Slack will retry on any non-2xx response or response timeout (>3s).
// The idempotency key (slack:event:{event_id}) prevents duplicate runs.

import { defineEventHandler, readRawBody, getHeader, setResponseStatus, send } from 'h3'
import { useRuntimeConfig } from 'nitropack/runtime'
import { verifySlackSignature } from '../../../lib/verify'
import { slackEventKey } from '../../../lib/idempotency'
import { enqueueSlackRun, resolveSlackAction } from '../../../lib/taskbus'

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

  // Step 2: Parse body
  let body: Record<string, unknown>
  try {
    body = JSON.parse(typeof rawBody === 'string' ? rawBody : new TextDecoder().decode(rawBody))
  } catch {
    setResponseStatus(event, 400)
    return send(event, JSON.stringify({ error: 'Invalid JSON body' }), 'application/json')
  }

  // Handle URL verification challenge (initial Slack App setup)
  if (body.type === 'url_verification') {
    return send(event, JSON.stringify({ challenge: body.challenge }), 'application/json')
  }

  // Step 3: ACK immediately — Slack requires a 200 within 3 seconds
  setResponseStatus(event, 200)
  send(event, JSON.stringify({ ok: true }), 'application/json')

  // Step 4: Enqueue run async (after ACK — Slack has already received 200)
  const innerEvent = body.event as Record<string, unknown> | undefined
  const eventType = (innerEvent?.type ?? body.type ?? 'unknown') as string
  const eventId = (body.event_id ?? innerEvent?.event_ts ?? `ts-${Date.now()}`) as string

  const route = resolveSlackAction(eventType)
  if (!route) {
    // Unhandled event type — acknowledged but not processed
    return
  }

  const supabaseUrl = (config.supabaseUrl as string) || process.env.SUPABASE_URL || ''
  const supabaseKey = (config.supabaseServiceRoleKey as string) || process.env.SUPABASE_SERVICE_ROLE_KEY || ''

  // Fire and forget — do not await (ACK already sent)
  enqueueSlackRun({
    ...route,
    idempotencyKey: slackEventKey(eventId),
    input: {
      event_type: eventType,
      event_id: eventId,
      team_id: body.team_id,
      event: innerEvent,
      api_app_id: body.api_app_id,
    },
    supabaseUrl,
    supabaseServiceRoleKey: supabaseKey,
  }).catch((err: unknown) => {
    console.error('[slack-events] enqueue error:', err instanceof Error ? err.message : String(err))
  })
})

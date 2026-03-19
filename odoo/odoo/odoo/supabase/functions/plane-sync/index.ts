/**
 * Plane Sync Edge Function
 *
 * Unified handler for:
 * 1. Platform Kit alerts → Plane issues (one-way sync for monitoring)
 * 2. Plane ↔ Odoo bidirectional sync (webhook-based)
 *
 * Endpoints:
 *   POST ?action=create         - Create single issue from Platform Kit event
 *   POST ?action=sync_failures  - Sync failed queue jobs to Plane
 *   POST ?action=sync_alerts    - Sync drift/eval alerts to Plane
 *   POST ?action=sync_all       - Sync all failures and alerts
 *   POST ?source=plane          - Handle Plane webhooks (→ Odoo)
 *   POST ?source=odoo           - Handle Odoo webhooks (→ Plane)
 *   GET  ?action=status         - Get sync status and recent activity
 *
 * Environment Variables:
 *   - SUPABASE_URL
 *   - SUPABASE_SERVICE_ROLE_KEY
 *   - PLANE_BASE_URL (e.g., https://api.plane.so/api/v1)
 *   - PLANE_API_TOKEN / PLANE_API_KEY
 *   - PLANE_WORKSPACE_SLUG (default workspace)
 *   - PLANE_PROJECT_ID (default project)
 *   - PLANE_WEBHOOK_SECRET (for verifying Plane webhooks)
 *   - ODOO_WEBHOOK_SECRET (for verifying Odoo webhooks)
 */

import { serve } from 'https://deno.land/std@0.177.0/http/server.ts'
import { createClient, SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Configuration
const PLANE_BASE_URL = Deno.env.get('PLANE_BASE_URL') || Deno.env.get('PLANE_API_URL') || 'https://api.plane.so/api/v1'
const PLANE_API_TOKEN = Deno.env.get('PLANE_API_TOKEN') || Deno.env.get('PLANE_API_KEY')
const PLANE_WORKSPACE_SLUG = Deno.env.get('PLANE_WORKSPACE_SLUG') || 'default'
const PLANE_PROJECT_ID = Deno.env.get('PLANE_PROJECT_ID')

// Entity mapping configuration for bidirectional sync
const ENTITY_MAPPINGS = {
  plane_to_odoo: {
    issue: 'project.task',
    project: 'project.project',
    cycle: 'project.milestone',
    module: 'project.project',
  },
  odoo_to_plane: {
    'project.task': 'issue',
    'project.project': 'project',
    'sale.order': 'issue',
    'account.move': 'issue',
  },
}

// Priority mappings
const PRIORITY_MAP: Record<string, number> = {
  urgent: 1,
  high: 2,
  medium: 3,
  low: 4,
  none: 0,
}

const PRIORITY_MAP_BIDIRECTIONAL = {
  plane_to_odoo: { urgent: '3', high: '2', medium: '1', low: '0', none: '0' },
  odoo_to_plane: { '3': 'urgent', '2': 'high', '1': 'medium', '0': 'low' },
}

// Types
interface PlaneIssue {
  id: string
  name: string
  description?: string
  state?: string
  priority?: number
  labels?: string[]
  assignees?: string[]
}

interface CreateIssuePayload {
  name: string
  description?: string
  priority?: number
  state?: string
  labels?: string[]
}

interface SyncRequest {
  action: 'create' | 'update' | 'sync_failures' | 'sync_alerts'
  source_type: 'eval_alert' | 'queue_failure' | 'drift_alert' | 'custom'
  source_id: string
  title?: string
  description?: string
  priority?: 'urgent' | 'high' | 'medium' | 'low' | 'none'
  labels?: string[]
  project_id?: string
  workspace_slug?: string
}

interface SyncResult {
  success: boolean
  source_id: string
  target_id?: string
  entity_type: string
  action: string
  error?: string
}

/**
 * Get required environment variable
 */
function required(name: string): string {
  const value = Deno.env.get(name)
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`)
  }
  return value
}

/**
 * Get Supabase client with service role
 */
function getSupabaseClient(): SupabaseClient {
  return createClient(required('SUPABASE_URL'), required('SUPABASE_SERVICE_ROLE_KEY'))
}

/**
 * Make authenticated request to Plane API
 */
async function planeRequest(
  method: string,
  path: string,
  body?: Record<string, unknown>
): Promise<{ ok: boolean; data?: unknown; error?: string }> {
  if (!PLANE_API_TOKEN) {
    return { ok: false, error: 'PLANE_API_TOKEN not configured' }
  }

  const url = `${PLANE_BASE_URL}${path}`

  try {
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': PLANE_API_TOKEN,
      },
      body: body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      const text = await response.text()
      return { ok: false, error: `Plane API error: ${response.status} ${text}` }
    }

    const data = await response.json()
    return { ok: true, data }
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : 'Unknown error' }
  }
}

/**
 * Create a Plane issue
 */
async function createIssue(
  workspaceSlug: string,
  projectId: string,
  payload: CreateIssuePayload
): Promise<{ ok: boolean; issue?: PlaneIssue; error?: string }> {
  const result = await planeRequest('POST', `/workspaces/${workspaceSlug}/projects/${projectId}/issues/`, payload)

  if (!result.ok) {
    return { ok: false, error: result.error }
  }

  return { ok: true, issue: result.data as PlaneIssue }
}

/**
 * Update a Plane issue
 */
async function updateIssue(
  workspaceSlug: string,
  projectId: string,
  issueId: string,
  payload: Partial<CreateIssuePayload>
): Promise<{ ok: boolean; issue?: PlaneIssue; error?: string }> {
  const result = await planeRequest(
    'PATCH',
    `/workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/`,
    payload
  )

  if (!result.ok) {
    return { ok: false, error: result.error }
  }

  return { ok: true, issue: result.data as PlaneIssue }
}

/**
 * Verify webhook signature (HMAC-SHA256)
 */
async function verifyWebhookSignature(payload: string, signature: string, secret: string): Promise<boolean> {
  try {
    const key = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    )

    const signatureBytes = hexToBytes(signature)
    const payloadBytes = new TextEncoder().encode(payload)

    return await crypto.subtle.verify('HMAC', key, signatureBytes, payloadBytes)
  } catch {
    return false
  }
}

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }
  return bytes
}

/**
 * Log sync event to ops.events
 */
async function logSyncEvent(
  supabase: SupabaseClient,
  level: 'info' | 'warning' | 'error',
  message: string,
  metadata: Record<string, unknown>
): Promise<void> {
  try {
    await supabase.rpc('ops.log_event', {
      p_level: level,
      p_message: message,
      p_system: 'supabase',
      p_category: 'plane-sync',
      p_event_type: 'webhook',
      p_component: 'plane-sync',
      p_metadata: metadata,
    })
  } catch (err) {
    console.error('Failed to log sync event:', err)
  }
}

/**
 * Get or create entity mapping for Plane issue (Platform Kit style)
 */
async function getOrCreateMapping(
  supabase: SupabaseClient,
  sourceType: string,
  sourceId: string,
  planeIssueId?: string
): Promise<{ localId: string; remoteId: string | null }> {
  // Get target ID for Plane connector
  const { data: target } = await supabase
    .from('connectors.targets')
    .select('id')
    .eq('connector_type', 'plane')
    .eq('status', 'active')
    .limit(1)
    .single()

  if (!target) {
    // Create default Plane target if not exists
    const { data: newTarget } = await supabase
      .from('connectors.targets')
      .insert({
        name: 'plane-default',
        connector_type: 'plane',
        display_name: 'Plane (Default)',
        base_url: PLANE_BASE_URL,
        status: 'active',
      })
      .select('id')
      .single()

    if (!newTarget) {
      return { localId: sourceId, remoteId: null }
    }
  }

  const targetId = target?.id

  // Check existing mapping
  const { data: existing } = await supabase
    .from('connectors.entity_mappings')
    .select('local_id, remote_id')
    .eq('target_id', targetId)
    .eq('entity_type', sourceType)
    .eq('local_id', sourceId)
    .single()

  if (existing) {
    return { localId: existing.local_id, remoteId: existing.remote_id }
  }

  // Create new mapping if we have a Plane issue ID
  if (planeIssueId && targetId) {
    await supabase.rpc('connectors.get_or_create_mapping', {
      p_target_id: targetId,
      p_entity_type: sourceType,
      p_local_id: sourceId,
      p_remote_id: planeIssueId,
    })
  }

  return { localId: sourceId, remoteId: planeIssueId || null }
}

/**
 * Record sync mapping for bidirectional sync
 */
async function recordSyncMapping(
  supabase: SupabaseClient,
  source: 'plane' | 'odoo',
  sourceId: string,
  sourceType: string,
  targetId: string,
  targetType: string
): Promise<void> {
  await supabase.from('plane.sync_mappings').upsert(
    {
      source_system: source,
      source_id: sourceId,
      source_type: sourceType,
      target_id: targetId,
      target_type: targetType,
      last_synced_at: new Date().toISOString(),
    },
    {
      onConflict: 'source_system,source_id,source_type',
    }
  )
}

/**
 * Get existing mapping for bidirectional sync
 */
async function getBidirectionalMapping(
  supabase: SupabaseClient,
  source: 'plane' | 'odoo',
  sourceId: string,
  sourceType: string
): Promise<{ target_id: string; target_type: string } | null> {
  const { data } = await supabase
    .from('plane.sync_mappings')
    .select('target_id, target_type')
    .eq('source_system', source)
    .eq('source_id', sourceId)
    .eq('source_type', sourceType)
    .single()

  return data
}

/**
 * Sync failed queue jobs to Plane issues
 */
async function syncFailedJobs(
  supabase: SupabaseClient,
  workspaceSlug: string,
  projectId: string
): Promise<{ created: number; errors: string[] }> {
  let created = 0
  const errors: string[] = []

  // Get recent failed jobs without Plane issues
  const { data: failedJobs } = await supabase
    .from('ops.queue')
    .select('id, job_type, job_name, error_message, completed_at, attempt, max_attempts')
    .eq('status', 'failed')
    .gte('completed_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
    .order('completed_at', { ascending: false })
    .limit(20)

  if (!failedJobs || failedJobs.length === 0) {
    return { created: 0, errors: [] }
  }

  for (const job of failedJobs) {
    // Check if already has a Plane issue
    const mapping = await getOrCreateMapping(supabase, 'queue_failure', job.id)
    if (mapping.remoteId) {
      continue // Already synced
    }

    // Create Plane issue
    const result = await createIssue(workspaceSlug, projectId, {
      name: `[Auto] Job Failed: ${job.job_name || job.job_type}`,
      description: `## Job Failure\n\n**Job ID:** ${job.id}\n**Type:** ${job.job_type}\n**Attempts:** ${job.attempt}/${job.max_attempts}\n**Failed At:** ${job.completed_at}\n\n### Error\n\`\`\`\n${job.error_message || 'No error message'}\n\`\`\`\n\n---\n*Auto-created by Platform Kit*`,
      priority: job.attempt >= job.max_attempts ? PRIORITY_MAP.high : PRIORITY_MAP.medium,
      labels: ['platform-kit', 'auto-created', 'job-failure'],
    })

    if (result.ok && result.issue) {
      await getOrCreateMapping(supabase, 'queue_failure', job.id, result.issue.id)
      created++
    } else {
      errors.push(`Failed to create issue for job ${job.id}: ${result.error}`)
    }
  }

  return { created, errors }
}

/**
 * Sync drift/eval alerts to Plane issues
 */
async function syncAlerts(
  supabase: SupabaseClient,
  workspaceSlug: string,
  projectId: string
): Promise<{ created: number; errors: string[] }> {
  let created = 0
  const errors: string[] = []

  // Get open alerts without Plane issues
  const { data: alerts } = await supabase
    .from('eval.drift_alerts')
    .select('id, alert_type, severity, title, description, metric_name, metric_value, created_at')
    .in('status', ['open', 'acknowledged'])
    .order('created_at', { ascending: false })
    .limit(20)

  if (!alerts || alerts.length === 0) {
    return { created: 0, errors: [] }
  }

  for (const alert of alerts) {
    // Check if already has a Plane issue
    const mapping = await getOrCreateMapping(supabase, 'drift_alert', alert.id)
    if (mapping.remoteId) {
      continue // Already synced
    }

    // Map severity to priority
    const priority =
      alert.severity === 'critical'
        ? PRIORITY_MAP.urgent
        : alert.severity === 'warning'
          ? PRIORITY_MAP.high
          : PRIORITY_MAP.medium

    // Create Plane issue
    const result = await createIssue(workspaceSlug, projectId, {
      name: `[Alert] ${alert.title}`,
      description: `## ${alert.alert_type.replace('_', ' ').toUpperCase()}\n\n${alert.description || ''}\n\n**Metric:** ${alert.metric_name || 'N/A'}\n**Value:** ${alert.metric_value || 'N/A'}\n**Detected:** ${alert.created_at}\n\n---\n*Auto-created by Platform Kit*`,
      priority,
      labels: ['platform-kit', 'auto-created', alert.alert_type, alert.severity],
    })

    if (result.ok && result.issue) {
      // Store Plane issue URL in alert
      await supabase
        .from('eval.drift_alerts')
        .update({
          related_issue_url: `${PLANE_BASE_URL.replace('/api/v1', '')}/${workspaceSlug}/projects/${projectId}/issues/${result.issue.id}`,
        })
        .eq('id', alert.id)

      await getOrCreateMapping(supabase, 'drift_alert', alert.id, result.issue.id)
      created++
    } else {
      errors.push(`Failed to create issue for alert ${alert.id}: ${result.error}`)
    }
  }

  return { created, errors }
}

/**
 * Call Odoo via odoo-proxy Edge Function
 */
async function callOdooProxy(path: string, method: string, body?: Record<string, unknown>): Promise<Response> {
  const supabaseUrl = required('SUPABASE_URL')
  const serviceKey = required('SUPABASE_SERVICE_ROLE_KEY')

  const response = await fetch(
    `${supabaseUrl}/functions/v1/odoo-proxy?path=${encodeURIComponent(path)}&skip_auth=true`,
    {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${serviceKey}`,
      },
      body: body ? JSON.stringify(body) : undefined,
    }
  )

  return response
}

/**
 * Handle Plane webhook (for bidirectional sync)
 */
async function handlePlaneWebhook(
  supabase: SupabaseClient,
  event: string,
  payload: Record<string, unknown>
): Promise<SyncResult> {
  const eventParts = event.split('.')
  const entityType = eventParts[0]
  const action = eventParts[1]

  const sourceId = String(payload.id || payload.issue_id || '')
  const odooModel = ENTITY_MAPPINGS.plane_to_odoo[entityType as keyof typeof ENTITY_MAPPINGS.plane_to_odoo]

  if (!odooModel) {
    return {
      success: false,
      source_id: sourceId,
      entity_type: entityType,
      action,
      error: `No Odoo mapping for Plane entity type: ${entityType}`,
    }
  }

  try {
    const existingMapping = await getBidirectionalMapping(supabase, 'plane', sourceId, entityType)

    if (action === 'deleted') {
      if (existingMapping) {
        await callOdooProxy('/ipai/write/', 'POST', {
          model: odooModel,
          id: existingMapping.target_id,
          values: { active: false },
        })
      }
      return {
        success: true,
        source_id: sourceId,
        target_id: existingMapping?.target_id,
        entity_type: entityType,
        action: 'archived',
      }
    }

    const odooValues = transformPlaneToOdoo(entityType, payload)
    let targetId: string

    if (existingMapping) {
      await callOdooProxy('/ipai/write/', 'POST', {
        model: odooModel,
        id: existingMapping.target_id,
        values: odooValues,
      })
      targetId = existingMapping.target_id
    } else {
      const createResponse = await callOdooProxy('/ipai/write/', 'POST', {
        model: odooModel,
        values: odooValues,
      })
      const createResult = await createResponse.json()
      targetId = String(createResult.id || createResult.result)
      await recordSyncMapping(supabase, 'plane', sourceId, entityType, targetId, odooModel)
    }

    return {
      success: true,
      source_id: sourceId,
      target_id: targetId,
      entity_type: entityType,
      action,
    }
  } catch (err) {
    return {
      success: false,
      source_id: sourceId,
      entity_type: entityType,
      action,
      error: err instanceof Error ? err.message : 'Unknown error',
    }
  }
}

/**
 * Handle Odoo webhook (for bidirectional sync)
 */
async function handleOdooWebhook(
  supabase: SupabaseClient,
  model: string,
  action: string,
  payload: Record<string, unknown>
): Promise<SyncResult> {
  const sourceId = String(payload.id || '')
  const planeType = ENTITY_MAPPINGS.odoo_to_plane[model as keyof typeof ENTITY_MAPPINGS.odoo_to_plane]

  if (!planeType) {
    return {
      success: false,
      source_id: sourceId,
      entity_type: model,
      action,
      error: `No Plane mapping for Odoo model: ${model}`,
    }
  }

  try {
    const existingMapping = await getBidirectionalMapping(supabase, 'odoo', sourceId, model)

    if (action === 'unlink') {
      if (existingMapping) {
        await planeRequest('PATCH', `/api/v1/issues/${existingMapping.target_id}/`, {
          archived_at: new Date().toISOString(),
        })
      }
      return {
        success: true,
        source_id: sourceId,
        target_id: existingMapping?.target_id,
        entity_type: model,
        action: 'archived',
      }
    }

    const planeValues = transformOdooToPlane(model, payload)
    let targetId: string

    if (existingMapping) {
      await planeRequest('PATCH', `/api/v1/issues/${existingMapping.target_id}/`, planeValues)
      targetId = existingMapping.target_id
    } else {
      const result = await planeRequest('POST', '/api/v1/issues/', planeValues)
      if (!result.ok) {
        throw new Error(result.error)
      }
      targetId = String((result.data as { id: string }).id)
      await recordSyncMapping(supabase, 'odoo', sourceId, model, targetId, planeType)
    }

    return {
      success: true,
      source_id: sourceId,
      target_id: targetId,
      entity_type: model,
      action,
    }
  } catch (err) {
    return {
      success: false,
      source_id: sourceId,
      entity_type: model,
      action,
      error: err instanceof Error ? err.message : 'Unknown error',
    }
  }
}

/**
 * Transform Plane entity to Odoo values
 */
function transformPlaneToOdoo(entityType: string, payload: Record<string, unknown>): Record<string, unknown> {
  switch (entityType) {
    case 'issue':
      return {
        name: payload.name || payload.title,
        description: payload.description || '',
        priority: PRIORITY_MAP_BIDIRECTIONAL.plane_to_odoo[(payload.priority as string) || 'none'],
        x_plane_id: payload.id,
        x_plane_url: payload.url || '',
      }
    case 'project':
      return {
        name: payload.name,
        description: payload.description || '',
        x_plane_id: payload.id,
      }
    default:
      return { name: payload.name || 'Synced from Plane' }
  }
}

/**
 * Transform Odoo entity to Plane values
 */
function transformOdooToPlane(model: string, payload: Record<string, unknown>): Record<string, unknown> {
  switch (model) {
    case 'project.task':
      return {
        name: payload.name,
        description: payload.description || '',
        priority: PRIORITY_MAP_BIDIRECTIONAL.odoo_to_plane[(payload.priority as string) || '0'],
      }
    case 'sale.order':
      return {
        name: `[Sale] ${payload.name}`,
        description: `Sale Order: ${payload.name}\nCustomer: ${payload.partner_id}\nAmount: ${payload.amount_total}`,
        priority: 'medium',
        labels: ['sales', 'odoo-sync'],
      }
    case 'account.move':
      return {
        name: `[Invoice] ${payload.name}`,
        description: `Invoice: ${payload.name}\nPartner: ${payload.partner_id}\nAmount: ${payload.amount_total}`,
        priority: 'medium',
        labels: ['finance', 'odoo-sync'],
      }
    default:
      return { name: payload.name || 'Synced from Odoo' }
  }
}

/**
 * Get sync status
 */
async function getSyncStatus(supabase: SupabaseClient): Promise<Record<string, unknown>> {
  const [mappingsResult, recentEventsResult] = await Promise.all([
    supabase.from('plane.sync_mappings').select('source_system, count').limit(100),
    supabase.from('ops.events').select('*').eq('category', 'plane-sync').order('created_at', { ascending: false }).limit(20),
  ])

  return {
    mappings: mappingsResult.data || [],
    recent_events: recentEventsResult.data || [],
    last_checked: new Date().toISOString(),
  }
}

/**
 * Main handler
 */
serve(async (req: Request): Promise<Response> => {
  const startTime = Date.now()

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Plane-Signature, X-Odoo-Signature',
      },
    })
  }

  const supabase = getSupabaseClient()
  const url = new URL(req.url)
  const source = url.searchParams.get('source') // 'plane' or 'odoo' for bidirectional sync
  const action = url.searchParams.get('action') || 'sync_all'
  const workspaceSlug = url.searchParams.get('workspace') || PLANE_WORKSPACE_SLUG
  const projectId = url.searchParams.get('project') || PLANE_PROJECT_ID

  try {
    // Handle status request
    if (req.method === 'GET' && action === 'status') {
      const status = await getSyncStatus(supabase)
      return new Response(JSON.stringify({ ok: true, ...status }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      })
    }

    // Handle bidirectional webhook sync
    if (source === 'plane' || source === 'odoo') {
      if (req.method !== 'POST') {
        return new Response(JSON.stringify({ ok: false, error: 'Method not allowed' }), {
          status: 405,
          headers: { 'Content-Type': 'application/json' },
        })
      }

      const rawBody = await req.text()
      const payload = JSON.parse(rawBody)

      let result: SyncResult

      if (source === 'plane') {
        const signature = req.headers.get('X-Plane-Signature') || ''
        const webhookSecret = Deno.env.get('PLANE_WEBHOOK_SECRET') || ''

        if (webhookSecret && signature) {
          const valid = await verifyWebhookSignature(rawBody, signature, webhookSecret)
          if (!valid) {
            await logSyncEvent(supabase, 'warning', 'Invalid Plane webhook signature', { source: 'plane' })
            return new Response(JSON.stringify({ ok: false, error: 'Invalid signature' }), {
              status: 401,
              headers: { 'Content-Type': 'application/json' },
            })
          }
        }

        const event = payload.event || payload.type || 'issue.updated'
        result = await handlePlaneWebhook(supabase, event, payload.data || payload)
      } else {
        const signature = req.headers.get('X-Odoo-Signature') || ''
        const webhookSecret = Deno.env.get('ODOO_WEBHOOK_SECRET') || ''

        if (webhookSecret && signature) {
          const valid = await verifyWebhookSignature(rawBody, signature, webhookSecret)
          if (!valid) {
            await logSyncEvent(supabase, 'warning', 'Invalid Odoo webhook signature', { source: 'odoo' })
            return new Response(JSON.stringify({ ok: false, error: 'Invalid signature' }), {
              status: 401,
              headers: { 'Content-Type': 'application/json' },
            })
          }
        }

        const model = payload.model || 'project.task'
        const odooAction = payload.action || payload.method || 'write'
        result = await handleOdooWebhook(supabase, model, odooAction, payload.data || payload)
      }

      await logSyncEvent(supabase, result.success ? 'info' : 'error', `Sync ${result.action}: ${result.entity_type} ${result.source_id}`, {
        ...result,
        source,
        duration_ms: Date.now() - startTime,
      })

      return new Response(JSON.stringify({ ok: result.success, ...result }), {
        status: result.success ? 200 : 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      })
    }

    // Handle Platform Kit sync actions
    if (!projectId) {
      throw new Error('PLANE_PROJECT_ID not configured and no project parameter provided')
    }

    let result: { created: number; errors: string[] } = { created: 0, errors: [] }

    switch (action) {
      case 'sync_failures': {
        result = await syncFailedJobs(supabase, workspaceSlug, projectId)
        break
      }

      case 'sync_alerts': {
        result = await syncAlerts(supabase, workspaceSlug, projectId)
        break
      }

      case 'sync_all': {
        const [failures, alerts] = await Promise.all([
          syncFailedJobs(supabase, workspaceSlug, projectId),
          syncAlerts(supabase, workspaceSlug, projectId),
        ])
        result = {
          created: failures.created + alerts.created,
          errors: [...failures.errors, ...alerts.errors],
        }
        break
      }

      case 'create': {
        const body = (await req.json()) as SyncRequest

        if (!body.title) {
          throw new Error('Missing required field: title')
        }

        const issueResult = await createIssue(body.workspace_slug || workspaceSlug, body.project_id || projectId, {
          name: body.title,
          description: body.description,
          priority: body.priority ? PRIORITY_MAP[body.priority] : PRIORITY_MAP.medium,
          labels: body.labels || ['platform-kit'],
        })

        if (!issueResult.ok) {
          throw new Error(issueResult.error)
        }

        if (body.source_id) {
          await getOrCreateMapping(supabase, body.source_type, body.source_id, issueResult.issue!.id)
        }

        result = { created: 1, errors: [] }
        break
      }

      default:
        throw new Error(`Unknown action: ${action}`)
    }

    await logSyncEvent(supabase, result.errors.length > 0 ? 'warning' : 'info', `Platform Kit sync: ${action}`, {
      action,
      workspace: workspaceSlug,
      project: projectId,
      created: result.created,
      errors: result.errors,
      duration_ms: Date.now() - startTime,
    })

    return new Response(
      JSON.stringify({
        success: true,
        duration_ms: Date.now() - startTime,
        issues_created: result.created,
        errors: result.errors,
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }
    )
  } catch (error) {
    console.error('Plane sync error:', error)

    await logSyncEvent(supabase, 'error', `Sync error: ${error instanceof Error ? error.message : 'Unknown error'}`, {
      action,
      source,
      error: error instanceof Error ? error.message : 'Unknown error',
      duration_ms: Date.now() - startTime,
    })

    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      }
    )
  }
})

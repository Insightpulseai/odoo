/**
 * Shared Supabase client for Edge Functions
 *
 * This module provides a configured Supabase client for use in Edge Functions.
 * It uses the service role key for administrative operations.
 */

import { createClient, SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Types for our custom schemas
export interface OpsRun {
  id: string
  system: string
  job_name: string
  job_type?: string
  run_number?: number
  status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled' | 'timeout' | 'retrying'
  started_at?: string
  ended_at?: string
  error_message?: string
  records_processed?: number
  records_failed?: number
  metadata?: Record<string, unknown>
}

export interface OpsEvent {
  id: string
  run_id?: string
  level: 'debug' | 'info' | 'warn' | 'error' | 'fatal'
  message: string
  system?: string
  category?: string
  event_type?: string
  component?: string
  duration_ms?: number
  metadata?: Record<string, unknown>
  timestamp: string
}

export interface OpsHealth {
  id: string
  system: string
  signal: string
  value: number
  component?: string
  unit?: string
  measured_at: string
}

export interface AdvisorFinding {
  id: string
  check_id: string
  category: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  status: 'open' | 'acknowledged' | 'in_progress' | 'resolved' | 'dismissed' | 'auto_resolved'
  title: string
  description?: string
  resource_type?: string
  resource_id?: string
  resource_name?: string
  evidence?: Record<string, unknown>
  first_seen_at: string
  last_seen_at: string
}

// Environment variables
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

/**
 * Create a Supabase client with service role privileges
 */
export function createServiceClient(): SupabaseClient {
  return createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  })
}

/**
 * Create a Supabase client from a request's authorization header
 */
export function createClientFromRequest(req: Request): SupabaseClient {
  const authHeader = req.headers.get('Authorization')
  const token = authHeader?.replace('Bearer ', '') ?? ''

  return createClient(SUPABASE_URL, Deno.env.get('SUPABASE_ANON_KEY')!, {
    global: {
      headers: { Authorization: `Bearer ${token}` },
    },
  })
}

/**
 * Log an ops event
 */
export async function logOpsEvent(
  client: SupabaseClient,
  event: Omit<OpsEvent, 'id' | 'timestamp'>
): Promise<void> {
  const { error } = await client.rpc('ops.log_event', {
    p_level: event.level,
    p_message: event.message,
    p_run_id: event.run_id,
    p_system: event.system,
    p_category: event.category,
    p_event_type: event.event_type,
    p_component: event.component,
    p_duration_ms: event.duration_ms,
    p_metadata: event.metadata ?? {},
  })

  if (error) {
    console.error('Failed to log ops event:', error)
  }
}

/**
 * Record a health signal
 */
export async function recordHealth(
  client: SupabaseClient,
  health: Omit<OpsHealth, 'id' | 'measured_at'>
): Promise<void> {
  const { error } = await client.rpc('ops.record_health', {
    p_system: health.system,
    p_signal: health.signal,
    p_value: health.value,
    p_component: health.component,
    p_unit: health.unit,
  })

  if (error) {
    console.error('Failed to record health:', error)
  }
}

// Default export
export default createServiceClient

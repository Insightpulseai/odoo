// ═══════════════════════════════════════════════════════════════════════════════
// Supabase Email Events - TypeScript Types
// ═══════════════════════════════════════════════════════════════════════════════
// Purpose: Type-safe interfaces for email.events schema
// Version: 1.0.0
// Date: 2026-01-28
// Generated from: db/migrations/20260128_email_events_schema.sql
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Email event types from Mailgun
 */
export type EmailEventType =
  | 'delivered'
  | 'failed'
  | 'opened'
  | 'clicked'
  | 'unsubscribed'
  | 'complained'
  | 'stored'
  | 'accepted'
  | 'rejected'
  | 'permanent_fail'
  | 'temporary_fail'
  | 'list_member_uploaded'
  | 'list_member_upload_failed'

/**
 * Email event record from email.events table
 */
export interface EmailEvent {
  // Primary key
  id: string

  // Event metadata
  event_type: EmailEventType
  event_timestamp: string

  // Message identification
  message_id: string
  recipient: string
  sender?: string
  subject?: string

  // Mailgun metadata
  mailgun_id?: string
  mailgun_timestamp?: number
  mailgun_token?: string
  mailgun_signature?: string

  // Delivery data
  delivery_status?: string
  delivery_code?: number
  delivery_description?: string
  delivery_message?: string

  // Engagement data (opens/clicks)
  client_type?: string
  client_os?: string
  client_name?: string
  device_type?: string
  user_agent?: string
  ip_address?: string
  country?: string
  region?: string
  city?: string

  // Link tracking (clicks)
  url?: string

  // Bounce/complaint data
  error_code?: string
  error_reason?: string
  severity?: string

  // Campaign/tag tracking
  tags?: string[]
  campaigns?: string[]
  user_variables?: Record<string, any>

  // Full raw payload
  raw_payload: Record<string, any>

  // Housekeeping
  created_at: string
  processed: boolean
  processed_at?: string
}

/**
 * Insert type for email.events (omits auto-generated fields)
 */
export interface EmailEventInsert {
  event_type: EmailEventType
  event_timestamp: string
  message_id: string
  recipient: string
  sender?: string
  subject?: string
  mailgun_id?: string
  mailgun_timestamp?: number
  mailgun_token?: string
  mailgun_signature?: string
  delivery_status?: string
  delivery_code?: number
  delivery_description?: string
  delivery_message?: string
  client_type?: string
  client_os?: string
  client_name?: string
  device_type?: string
  user_agent?: string
  ip_address?: string
  country?: string
  region?: string
  city?: string
  url?: string
  error_code?: string
  error_reason?: string
  severity?: string
  tags?: string[]
  campaigns?: string[]
  user_variables?: Record<string, any>
  raw_payload: Record<string, any>
  processed?: boolean
}

/**
 * Daily statistics record from email.daily_stats table
 */
export interface EmailDailyStat {
  id: string
  stat_date: string

  // Volume metrics
  total_sent: number
  total_delivered: number
  total_failed: number
  total_bounced: number
  total_complained: number

  // Engagement metrics
  total_opened: number
  total_clicked: number
  unique_opens: number
  unique_clicks: number

  // Calculated rates (%)
  delivery_rate: number
  bounce_rate: number
  open_rate: number
  click_rate: number
  complaint_rate: number

  // Optional segmentation
  sender?: string
  campaign?: string
  tags?: string[]

  // Housekeeping
  created_at: string
  updated_at: string
}

/**
 * Recipient engagement record from email.recipient_engagement table
 */
export interface RecipientEngagement {
  id: string
  recipient: string

  // Lifetime metrics
  total_received: number
  total_delivered: number
  total_bounced: number
  total_opened: number
  total_clicked: number
  total_complained: number
  total_unsubscribed: number

  // Last activity timestamps
  last_sent_at?: string
  last_delivered_at?: string
  last_opened_at?: string
  last_clicked_at?: string
  last_bounced_at?: string
  last_complained_at?: string

  // Calculated engagement score (0-100)
  engagement_score: number

  // Status flags
  is_valid: boolean
  is_suppressed: boolean
  suppression_reason?: string

  // Housekeeping
  created_at: string
  updated_at: string
}

/**
 * Supabase database schema type
 */
export interface Database {
  email: {
    Tables: {
      events: {
        Row: EmailEvent
        Insert: EmailEventInsert
        Update: Partial<EmailEventInsert>
      }
      daily_stats: {
        Row: EmailDailyStat
        Insert: Omit<EmailDailyStat, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<EmailDailyStat, 'id' | 'created_at'>>
      }
      recipient_engagement: {
        Row: RecipientEngagement
        Insert: Omit<RecipientEngagement, 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Omit<RecipientEngagement, 'id' | 'created_at'>>
      }
    }
    Functions: {
      calculate_engagement_score: {
        Args: { recipient_email: string }
        Returns: number
      }
      refresh_daily_stats: {
        Args: { target_date?: string }
        Returns: void
      }
    }
  }
}

/**
 * Helper type for Supabase client
 */
export type SupabaseClient = import('@supabase/supabase-js').SupabaseClient<Database>

/**
 * Event aggregation for BI queries
 */
export interface EventAggregation {
  period: string // e.g., "2026-01-28", "2026-01", "2026-W04"
  event_type: EmailEventType
  count: number
  unique_recipients: number
  unique_messages: number
}

/**
 * Engagement funnel metrics
 */
export interface EngagementFunnel {
  period: string
  total_sent: number
  delivered: number
  opened: number
  clicked: number
  delivery_rate: number
  open_rate: number
  click_rate: number
  click_to_open_rate: number
}

/**
 * Top performers (recipients/campaigns)
 */
export interface TopPerformer {
  identifier: string // recipient or campaign name
  metric_value: number
  rank: number
}

/**
 * Suppression list entry
 */
export interface SuppressionEntry {
  recipient: string
  reason: 'bounce' | 'complaint' | 'unsubscribe'
  suppressed_at: string
}

// ═══════════════════════════════════════════════════════════════════════════════
// Usage Examples
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Example: Query events with type safety
 *
 * ```typescript
 * import { createClient } from '@supabase/supabase-js'
 * import type { Database, EmailEvent } from './email_events'
 *
 * const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_KEY)
 *
 * const { data, error } = await supabase
 *   .from('email.events')
 *   .select('*')
 *   .eq('event_type', 'delivered')
 *   .gte('event_timestamp', '2026-01-01')
 *   .order('event_timestamp', { ascending: false })
 *
 * if (data) {
 *   const events: EmailEvent[] = data
 *   console.log(`Found ${events.length} delivered events`)
 * }
 * ```
 *
 * Example: Insert event
 *
 * ```typescript
 * const { data, error } = await supabase
 *   .from('email.events')
 *   .insert([{
 *     event_type: 'delivered',
 *     event_timestamp: new Date().toISOString(),
 *     message_id: '<msg@example.com>',
 *     recipient: 'user@example.com',
 *     raw_payload: { ... }
 *   }])
 * ```
 *
 * Example: Get daily stats
 *
 * ```typescript
 * const { data, error } = await supabase
 *   .from('email.daily_stats')
 *   .select('*')
 *   .gte('stat_date', '2026-01-01')
 *   .order('stat_date', { ascending: false })
 *
 * if (data) {
 *   data.forEach(stat => {
 *     console.log(`${stat.stat_date}: ${stat.delivery_rate}% delivered`)
 *   })
 * }
 * ```
 *
 * Example: Get recipient engagement
 *
 * ```typescript
 * const { data, error } = await supabase
 *   .from('email.recipient_engagement')
 *   .select('*')
 *   .eq('recipient', 'user@example.com')
 *   .single()
 *
 * if (data) {
 *   console.log(`Engagement score: ${data.engagement_score}`)
 *   console.log(`Last opened: ${data.last_opened_at}`)
 * }
 * ```
 *
 * Example: Call function
 *
 * ```typescript
 * const { data, error } = await supabase.rpc('refresh_daily_stats', {
 *   target_date: '2026-01-28'
 * })
 * ```
 */

// ═══════════════════════════════════════════════════════════════════════════════
// End of Types
// ═══════════════════════════════════════════════════════════════════════════════

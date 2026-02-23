// ═══════════════════════════════════════════════════════════════════════════════
// Supabase Email Events - Realtime Subscription Example
// ═══════════════════════════════════════════════════════════════════════════════
// Purpose: Real-time dashboard updates with Supabase Realtime
// Version: 1.0.0
// Date: 2026-01-28
// ═══════════════════════════════════════════════════════════════════════════════

import { createClient } from '@supabase/supabase-js'
import type { Database, EmailEvent } from '../types/email_events'

// ───────────────────────────────────────────────────────────────────────────────
// Configuration
// ───────────────────────────────────────────────────────────────────────────────

const SUPABASE_URL = process.env.SUPABASE_URL!
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY!

const supabase = createClient<Database>(SUPABASE_URL, SUPABASE_ANON_KEY)

// ───────────────────────────────────────────────────────────────────────────────
// Example 1: Subscribe to All New Events
// ───────────────────────────────────────────────────────────────────────────────

export function subscribeToAllEvents(
  onEvent: (event: EmailEvent) => void,
  onError?: (error: Error) => void
) {
  const channel = supabase
    .channel('email-events-all')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
      },
      (payload) => {
        console.log('New email event:', payload.new)
        onEvent(payload.new as EmailEvent)
      }
    )
    .subscribe((status, err) => {
      if (status === 'SUBSCRIBED') {
        console.log('✅ Subscribed to all email events')
      }
      if (err && onError) {
        onError(err)
      }
    })

  // Return unsubscribe function
  return () => {
    channel.unsubscribe()
    console.log('❌ Unsubscribed from all email events')
  }
}

// Usage:
// const unsubscribe = subscribeToAllEvents((event) => {
//   console.log('Received event:', event.event_type, event.recipient)
// })
//
// Later: unsubscribe()

// ───────────────────────────────────────────────────────────────────────────────
// Example 2: Subscribe to Specific Event Types
// ───────────────────────────────────────────────────────────────────────────────

export function subscribeToEventType(
  eventType: string,
  onEvent: (event: EmailEvent) => void,
  onError?: (error: Error) => void
) {
  const channel = supabase
    .channel(`email-events-${eventType}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
        filter: `event_type=eq.${eventType}`,
      },
      (payload) => {
        console.log(`New ${eventType} event:`, payload.new)
        onEvent(payload.new as EmailEvent)
      }
    )
    .subscribe((status, err) => {
      if (status === 'SUBSCRIBED') {
        console.log(`✅ Subscribed to ${eventType} events`)
      }
      if (err && onError) {
        onError(err)
      }
    })

  return () => channel.unsubscribe()
}

// Usage:
// const unsubscribe = subscribeToEventType('bounced', (event) => {
//   alert(`Email to ${event.recipient} bounced!`)
// })

// ───────────────────────────────────────────────────────────────────────────────
// Example 3: Subscribe to Events for Specific Recipient
// ───────────────────────────────────────────────────────────────────────────────

export function subscribeToRecipient(
  recipient: string,
  onEvent: (event: EmailEvent) => void,
  onError?: (error: Error) => void
) {
  const channel = supabase
    .channel(`email-events-${recipient}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
        filter: `recipient=eq.${recipient}`,
      },
      (payload) => {
        console.log(`New event for ${recipient}:`, payload.new)
        onEvent(payload.new as EmailEvent)
      }
    )
    .subscribe((status, err) => {
      if (status === 'SUBSCRIBED') {
        console.log(`✅ Subscribed to events for ${recipient}`)
      }
      if (err && onError) {
        onError(err)
      }
    })

  return () => channel.unsubscribe()
}

// Usage:
// const unsubscribe = subscribeToRecipient('user@example.com', (event) => {
//   console.log('Event for user:', event.event_type)
// })

// ───────────────────────────────────────────────────────────────────────────────
// Example 4: Multiple Event Types (Failures Only)
// ───────────────────────────────────────────────────────────────────────────────

export function subscribeToFailures(
  onEvent: (event: EmailEvent) => void,
  onError?: (error: Error) => void
) {
  // Note: Supabase Realtime doesn't support OR filters, so we need multiple subscriptions
  const failureTypes = ['failed', 'bounced', 'permanent_fail', 'temporary_fail', 'complained']

  const channels = failureTypes.map((eventType) =>
    supabase
      .channel(`email-failures-${eventType}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'email',
          table: 'events',
          filter: `event_type=eq.${eventType}`,
        },
        (payload) => {
          console.log(`⚠️ Failure event:`, payload.new)
          onEvent(payload.new as EmailEvent)
        }
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(`✅ Subscribed to ${eventType} events`)
        }
        if (err && onError) {
          onError(err)
        }
      })
  )

  return () => {
    channels.forEach((channel) => channel.unsubscribe())
    console.log('❌ Unsubscribed from failure events')
  }
}

// Usage:
// const unsubscribe = subscribeToFailures((event) => {
//   // Send alert to monitoring system
//   notifyOps({
//     type: event.event_type,
//     recipient: event.recipient,
//     reason: event.error_reason
//   })
// })

// ───────────────────────────────────────────────────────────────────────────────
// Example 5: Live Dashboard Stats
// ───────────────────────────────────────────────────────────────────────────────

interface LiveStats {
  total: number
  delivered: number
  failed: number
  bounced: number
  opened: number
  clicked: number
  complained: number
}

export function subscribeToDashboardStats(
  onStatsUpdate: (stats: LiveStats) => void,
  intervalMs: number = 5000
) {
  // Initialize stats
  let stats: LiveStats = {
    total: 0,
    delivered: 0,
    failed: 0,
    bounced: 0,
    opened: 0,
    clicked: 0,
    complained: 0,
  }

  // Subscribe to new events
  const channel = supabase
    .channel('email-dashboard-stats')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'email',
        table: 'events',
      },
      (payload) => {
        const event = payload.new as EmailEvent

        // Update stats based on event type
        stats.total++
        switch (event.event_type) {
          case 'delivered':
            stats.delivered++
            break
          case 'failed':
          case 'temporary_fail':
            stats.failed++
            break
          case 'bounced':
          case 'permanent_fail':
            stats.bounced++
            break
          case 'opened':
            stats.opened++
            break
          case 'clicked':
            stats.clicked++
            break
          case 'complained':
            stats.complained++
            break
        }

        // Callback with updated stats
        onStatsUpdate({ ...stats })
      }
    )
    .subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        console.log('✅ Subscribed to dashboard stats')
      }
    })

  // Also refresh from database periodically
  const refreshInterval = setInterval(async () => {
    const { data, error } = await supabase
      .from('email.events')
      .select('event_type')
      .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

    if (data && !error) {
      stats = {
        total: data.length,
        delivered: data.filter((e) => e.event_type === 'delivered').length,
        failed: data.filter((e) => ['failed', 'temporary_fail'].includes(e.event_type)).length,
        bounced: data.filter((e) => ['bounced', 'permanent_fail'].includes(e.event_type)).length,
        opened: data.filter((e) => e.event_type === 'opened').length,
        clicked: data.filter((e) => e.event_type === 'clicked').length,
        complained: data.filter((e) => e.event_type === 'complained').length,
      }
      onStatsUpdate({ ...stats })
    }
  }, intervalMs)

  // Return cleanup function
  return () => {
    channel.unsubscribe()
    clearInterval(refreshInterval)
    console.log('❌ Unsubscribed from dashboard stats')
  }
}

// Usage:
// const unsubscribe = subscribeToDashboardStats((stats) => {
//   console.log('Live stats:', stats)
//   // Update your dashboard UI with stats
//   updateDashboard(stats)
// }, 5000)

// ───────────────────────────────────────────────────────────────────────────────
// Example 6: React Hook Integration
// ───────────────────────────────────────────────────────────────────────────────

export function useRealtimeEmailEvents(
  eventType?: string,
  recipient?: string
): EmailEvent[] {
  const [events, setEvents] = React.useState<EmailEvent[]>([])

  React.useEffect(() => {
    let channelName = 'email-events'
    let filter: any = {
      event: 'INSERT',
      schema: 'email',
      table: 'events',
    }

    // Add filters if provided
    if (eventType) {
      channelName += `-${eventType}`
      filter.filter = `event_type=eq.${eventType}`
    } else if (recipient) {
      channelName += `-${recipient}`
      filter.filter = `recipient=eq.${recipient}`
    }

    const channel = supabase
      .channel(channelName)
      .on('postgres_changes', filter, (payload) => {
        setEvents((prev) => [payload.new as EmailEvent, ...prev].slice(0, 100))
      })
      .subscribe()

    return () => {
      channel.unsubscribe()
    }
  }, [eventType, recipient])

  return events
}

// Usage in React:
// function EmailDashboard() {
//   const events = useRealtimeEmailEvents()
//   const bounces = useRealtimeEmailEvents('bounced')
//
//   return (
//     <div>
//       <h2>Recent Events: {events.length}</h2>
//       <h2>Recent Bounces: {bounces.length}</h2>
//       {events.map(event => (
//         <div key={event.id}>{event.event_type} - {event.recipient}</div>
//       ))}
//     </div>
//   )
// }

// ───────────────────────────────────────────────────────────────────────────────
// Example 7: Presence - Who's Watching the Dashboard
// ───────────────────────────────────────────────────────────────────────────────

export function subscribeToDashboardPresence(
  userId: string,
  onPresenceChange: (users: string[]) => void
) {
  const channel = supabase.channel('email-dashboard-presence', {
    config: {
      presence: {
        key: userId,
      },
    },
  })

  channel
    .on('presence', { event: 'sync' }, () => {
      const state = channel.presenceState()
      const users = Object.keys(state)
      onPresenceChange(users)
    })
    .on('presence', { event: 'join' }, ({ key }) => {
      console.log('User joined:', key)
    })
    .on('presence', { event: 'leave' }, ({ key }) => {
      console.log('User left:', key)
    })
    .subscribe(async (status) => {
      if (status === 'SUBSCRIBED') {
        await channel.track({ online_at: new Date().toISOString() })
      }
    })

  return () => channel.unsubscribe()
}

// Usage:
// const unsubscribe = subscribeToDashboardPresence('user-123', (users) => {
//   console.log('Users watching dashboard:', users.length)
// })

// ═══════════════════════════════════════════════════════════════════════════════
// Complete Dashboard Example
// ═══════════════════════════════════════════════════════════════════════════════

export function startLiveEmailDashboard() {
  console.log('🚀 Starting live email dashboard...')

  // Subscribe to all events for activity feed
  const unsubscribeAll = subscribeToAllEvents((event) => {
    console.log(`📧 ${event.event_type}: ${event.recipient}`)
  })

  // Subscribe to failures for alerts
  const unsubscribeFailures = subscribeToFailures((event) => {
    console.error(`⚠️ FAILURE: ${event.event_type} - ${event.recipient}`)
    console.error(`   Reason: ${event.error_reason}`)
  })

  // Subscribe to live stats
  const unsubscribeStats = subscribeToDashboardStats((stats) => {
    console.log('📊 Live Stats (24h):', {
      ...stats,
      delivery_rate: ((stats.delivered / stats.total) * 100).toFixed(2) + '%',
      bounce_rate: ((stats.bounced / stats.total) * 100).toFixed(2) + '%',
    })
  })

  // Return cleanup function
  return () => {
    unsubscribeAll()
    unsubscribeFailures()
    unsubscribeStats()
    console.log('👋 Stopped live email dashboard')
  }
}

// Usage:
// const stop = startLiveEmailDashboard()
// Later: stop()

// ═══════════════════════════════════════════════════════════════════════════════
// End of Examples
// ═══════════════════════════════════════════════════════════════════════════════

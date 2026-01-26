// Supabase Edge Function: realtime-sync
// Handles real-time synchronization between components

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface RealtimeSyncRequest {
  channel: string
  event: string
  payload: Record<string, unknown>
  broadcast_to?: string[]
}

interface SyncStatus {
  channel: string
  subscribers: number
  last_event: string
  last_event_time: string
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Handle different HTTP methods
    if (req.method === 'GET') {
      // Get sync status
      const status = await getSyncStatus(supabase)
      return new Response(
        JSON.stringify(status),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (req.method === 'POST') {
      const body: RealtimeSyncRequest = await req.json()
      const result = await broadcastSync(supabase, body)

      return new Response(
        JSON.stringify(result),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Realtime sync error:', error)

    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Get current sync status
async function getSyncStatus(supabase: any): Promise<SyncStatus[]> {
  const channels = ['sync-events', 'schema-changes', 'kb-updates', 'control-room']
  const status: SyncStatus[] = []

  for (const channelName of channels) {
    // Get last event from sync_events
    const { data: lastEvent } = await supabase
      .from('sync_events')
      .select('event_type, timestamp')
      .eq('channel', channelName)
      .order('timestamp', { ascending: false })
      .limit(1)
      .single()

    status.push({
      channel: channelName,
      subscribers: 0, // Would need presence tracking for accurate count
      last_event: lastEvent?.event_type || 'none',
      last_event_time: lastEvent?.timestamp || 'never'
    })
  }

  return status
}

// Broadcast sync event to channels
async function broadcastSync(supabase: any, request: RealtimeSyncRequest) {
  const { channel, event, payload, broadcast_to } = request

  // Create the channel
  const realtimeChannel = supabase.channel(channel)

  // Broadcast the event
  await realtimeChannel.send({
    type: 'broadcast',
    event,
    payload: {
      ...payload,
      timestamp: new Date().toISOString(),
      source: 'realtime-sync'
    }
  })

  // Log the sync event
  await supabase.from('sync_events').insert({
    event_type: event,
    channel,
    details: payload,
    broadcast_targets: broadcast_to,
    status: 'sent',
    timestamp: new Date().toISOString()
  })

  // If specific targets, also broadcast to those channels
  if (broadcast_to && broadcast_to.length > 0) {
    for (const target of broadcast_to) {
      const targetChannel = supabase.channel(target)
      await targetChannel.send({
        type: 'broadcast',
        event: `${channel}:${event}`,
        payload
      })
    }
  }

  return {
    success: true,
    channel,
    event,
    broadcast_to: broadcast_to || [],
    timestamp: new Date().toISOString()
  }
}

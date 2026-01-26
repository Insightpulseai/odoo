// Supabase Edge Function: schema-changed
// Handles database schema change notifications and updates metadata

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface SchemaChangeRequest {
  action: 'refresh_metadata' | 'invalidate_cache' | 'notify_subscribers'
  tables?: string[]
  migration_file?: string
  changes?: SchemaChange[]
}

interface SchemaChange {
  type: 'create' | 'alter' | 'drop'
  object_type: 'table' | 'column' | 'index' | 'constraint'
  object_name: string
  details?: Record<string, unknown>
}

interface SchemaMetadata {
  table_name: string
  column_count: number
  row_estimate: number
  last_modified: string
  indexes: string[]
  constraints: string[]
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

    const body: SchemaChangeRequest = await req.json()
    const { action, tables, migration_file, changes } = body

    let result: Record<string, unknown>

    switch (action) {
      case 'refresh_metadata':
        result = await refreshSchemaMetadata(supabase, tables)
        break

      case 'invalidate_cache':
        result = await invalidateSchemaCache(supabase, tables)
        break

      case 'notify_subscribers':
        result = await notifySchemaSubscribers(supabase, changes || [])
        break

      default:
        throw new Error(`Unknown action: ${action}`)
    }

    // Log schema change event
    await supabase.from('sync_events').insert({
      event_type: 'schema_change',
      action,
      details: {
        tables,
        migration_file,
        changes,
        result
      },
      status: 'completed',
      timestamp: new Date().toISOString()
    })

    return new Response(
      JSON.stringify({ success: true, ...result }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    console.error('Schema change error:', error)

    return new Response(
      JSON.stringify({
        success: false,
        error: error.message
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})

// Refresh schema metadata for specified tables
async function refreshSchemaMetadata(supabase: any, tables?: string[]): Promise<Record<string, unknown>> {
  // Query pg_catalog for table metadata
  const { data: tableInfo, error } = await supabase.rpc('get_table_metadata', {
    table_names: tables || null
  })

  if (error) {
    // If RPC doesn't exist, use direct query
    console.log('Using fallback metadata query')
    return await refreshMetadataFallback(supabase, tables)
  }

  // Update data_assets with fresh metadata
  const updates: SchemaMetadata[] = []

  for (const table of tableInfo || []) {
    const metadata: SchemaMetadata = {
      table_name: table.table_name,
      column_count: table.column_count,
      row_estimate: table.row_estimate,
      last_modified: new Date().toISOString(),
      indexes: table.indexes || [],
      constraints: table.constraints || []
    }

    await supabase
      .from('data_assets')
      .upsert({
        table_name: metadata.table_name,
        schema_name: 'public',
        column_count: metadata.column_count,
        row_estimate: metadata.row_estimate,
        indexes: metadata.indexes,
        constraints: metadata.constraints,
        updated_at: metadata.last_modified
      }, {
        onConflict: 'table_name,schema_name'
      })

    updates.push(metadata)
  }

  return {
    action: 'refresh_metadata',
    tables_updated: updates.length,
    metadata: updates
  }
}

// Fallback metadata refresh using information_schema
async function refreshMetadataFallback(supabase: any, tables?: string[]): Promise<Record<string, unknown>> {
  // This is a simplified fallback - in production, use proper RPC
  const updated: string[] = []

  if (tables) {
    for (const table of tables) {
      await supabase
        .from('data_assets')
        .upsert({
          table_name: table,
          schema_name: 'public',
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'table_name,schema_name'
        })

      updated.push(table)
    }
  }

  return {
    action: 'refresh_metadata_fallback',
    tables_updated: updated.length,
    tables: updated
  }
}

// Invalidate schema-related caches
async function invalidateSchemaCache(supabase: any, tables?: string[]): Promise<Record<string, unknown>> {
  // Broadcast cache invalidation to all connected clients
  const channel = supabase.channel('schema-changes')

  await channel.send({
    type: 'broadcast',
    event: 'cache_invalidate',
    payload: {
      tables: tables || ['*'],
      timestamp: new Date().toISOString()
    }
  })

  // Update cache version in metadata
  await supabase
    .from('system_metadata')
    .upsert({
      key: 'schema_cache_version',
      value: Date.now().toString(),
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'key'
    })

  return {
    action: 'invalidate_cache',
    tables_affected: tables?.length || 'all',
    new_version: Date.now()
  }
}

// Notify subscribers about schema changes
async function notifySchemaSubscribers(supabase: any, changes: SchemaChange[]): Promise<Record<string, unknown>> {
  if (changes.length === 0) {
    return { action: 'notify_subscribers', notifications_sent: 0 }
  }

  // Group changes by type for summary
  const summary = {
    creates: changes.filter(c => c.type === 'create').length,
    alters: changes.filter(c => c.type === 'alter').length,
    drops: changes.filter(c => c.type === 'drop').length
  }

  // Broadcast to realtime channel
  const channel = supabase.channel('schema-changes')

  await channel.send({
    type: 'broadcast',
    event: 'schema_updated',
    payload: {
      changes,
      summary,
      timestamp: new Date().toISOString()
    }
  })

  // Insert notification records for UI
  await supabase.from('notifications').insert({
    type: 'schema_change',
    title: `Schema updated: ${changes.length} changes`,
    body: `Creates: ${summary.creates}, Alters: ${summary.alters}, Drops: ${summary.drops}`,
    data: { changes, summary },
    created_at: new Date().toISOString()
  })

  return {
    action: 'notify_subscribers',
    notifications_sent: 1,
    changes_count: changes.length,
    summary
  }
}

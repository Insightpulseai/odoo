// Supabase Edge Function: sync-kb-to-schema
// Syncs KB artifacts to schema metadata and refreshes caches

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface SyncRequest {
  action: 'refresh_all' | 'refresh_table' | 'sync_artifact'
  table_name?: string
  artifact_id?: string
  source?: string
}

interface SyncResult {
  success: boolean
  action: string
  affected: number
  details?: Record<string, unknown>
  error?: string
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

    const body: SyncRequest = await req.json()
    const { action, table_name, artifact_id, source } = body

    let result: SyncResult

    switch (action) {
      case 'refresh_all':
        result = await refreshAllMetadata(supabase)
        break

      case 'refresh_table':
        if (!table_name) {
          throw new Error('table_name required for refresh_table action')
        }
        result = await refreshTableMetadata(supabase, table_name)
        break

      case 'sync_artifact':
        if (!artifact_id) {
          throw new Error('artifact_id required for sync_artifact action')
        }
        result = await syncArtifactToSchema(supabase, artifact_id)
        break

      default:
        throw new Error(`Unknown action: ${action}`)
    }

    // Log sync event
    await supabase.from('sync_events').insert({
      event_type: 'kb_schema_sync',
      action,
      source: source || 'edge_function',
      status: result.success ? 'completed' : 'failed',
      details: result,
      timestamp: new Date().toISOString()
    })

    // Broadcast realtime update
    await supabase.channel('sync-events').send({
      type: 'broadcast',
      event: 'kb_sync_complete',
      payload: result
    })

    return new Response(
      JSON.stringify(result),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: result.success ? 200 : 500
      }
    )

  } catch (error) {
    console.error('Sync error:', error)

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

// Refresh all metadata tables
async function refreshAllMetadata(supabase: any): Promise<SyncResult> {
  // Get all KB artifacts that are data dictionaries or schema docs
  const { data: artifacts, error } = await supabase
    .from('kb_artifacts')
    .select('*')
    .in('kind', ['data_dictionary', 'api_reference', 'prd'])

  if (error) throw error

  let affected = 0

  for (const artifact of artifacts || []) {
    // Extract table references from content
    const tables = extractTableReferences(artifact.content)

    for (const table of tables) {
      // Update or create data_assets entry
      await supabase
        .from('data_assets')
        .upsert({
          table_name: table.name,
          schema_name: table.schema || 'public',
          description: table.description,
          kb_artifact_id: artifact.id,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'table_name,schema_name'
        })

      affected++
    }
  }

  // Update materialized views if any
  await supabase.rpc('refresh_metadata_views')

  return {
    success: true,
    action: 'refresh_all',
    affected,
    details: {
      artifacts_processed: artifacts?.length || 0
    }
  }
}

// Refresh single table metadata
async function refreshTableMetadata(supabase: any, tableName: string): Promise<SyncResult> {
  // Find KB artifact that documents this table
  const { data: artifacts } = await supabase
    .from('kb_artifacts')
    .select('*')
    .or(`content.ilike.%${tableName}%,title.ilike.%${tableName}%`)
    .limit(5)

  if (!artifacts || artifacts.length === 0) {
    return {
      success: true,
      action: 'refresh_table',
      affected: 0,
      details: { message: 'No matching KB artifacts found' }
    }
  }

  // Update data_assets with aggregated info
  const descriptions = artifacts
    .map((a: any) => extractTableDescription(a.content, tableName))
    .filter(Boolean)

  await supabase
    .from('data_assets')
    .upsert({
      table_name: tableName,
      schema_name: 'public',
      description: descriptions[0] || null,
      kb_artifact_ids: artifacts.map((a: any) => a.id),
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'table_name,schema_name'
    })

  return {
    success: true,
    action: 'refresh_table',
    affected: 1,
    details: {
      table: tableName,
      artifacts_found: artifacts.length
    }
  }
}

// Sync single artifact to schema
async function syncArtifactToSchema(supabase: any, artifactId: string): Promise<SyncResult> {
  const { data: artifact, error } = await supabase
    .from('kb_artifacts')
    .select('*')
    .eq('id', artifactId)
    .single()

  if (error) throw error
  if (!artifact) throw new Error('Artifact not found')

  const tables = extractTableReferences(artifact.content)
  let affected = 0

  for (const table of tables) {
    await supabase
      .from('data_assets')
      .upsert({
        table_name: table.name,
        schema_name: table.schema || 'public',
        description: table.description,
        kb_artifact_id: artifact.id,
        updated_at: new Date().toISOString()
      }, {
        onConflict: 'table_name,schema_name'
      })

    affected++
  }

  return {
    success: true,
    action: 'sync_artifact',
    affected,
    details: {
      artifact_id: artifactId,
      artifact_title: artifact.title
    }
  }
}

// Extract table references from markdown content
function extractTableReferences(content: string): Array<{name: string, schema?: string, description?: string}> {
  const tables: Array<{name: string, schema?: string, description?: string}> = []

  // Match ### table_name patterns
  const headerRegex = /###\s+(\w+)\n\n>?\s*(.+)?/g
  let match

  while ((match = headerRegex.exec(content)) !== null) {
    tables.push({
      name: match[1],
      description: match[2]?.trim()
    })
  }

  // Match CREATE TABLE patterns
  const createRegex = /CREATE TABLE (?:IF NOT EXISTS )?(?:(\w+)\.)?(\w+)/gi
  while ((match = createRegex.exec(content)) !== null) {
    if (!tables.find(t => t.name === match[2])) {
      tables.push({
        schema: match[1],
        name: match[2]
      })
    }
  }

  return tables
}

// Extract description for specific table
function extractTableDescription(content: string, tableName: string): string | null {
  // Look for description after table header
  const regex = new RegExp(`###\\s+${tableName}\\n\\n>?\\s*(.+)`, 'i')
  const match = content.match(regex)
  return match ? match[1].trim() : null
}

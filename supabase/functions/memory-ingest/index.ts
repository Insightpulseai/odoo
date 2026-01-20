/**
 * Memory Ingestion Edge Function
 *
 * Purpose: Centralized endpoint for ingesting infrastructure discovery data
 * into Supabase knowledge graph (infra.nodes + infra.edges)
 *
 * Accepts JSON payload with:
 * - source: discovery source ID (vercel, supabase, odoo, digitalocean, docker)
 * - nodes: array of node objects
 * - edges: array of edge objects
 * - caller: optional caller annotation for provenance tracking
 *
 * Security: Service role only (protected endpoint)
 *
 * Usage:
 * POST /functions/v1/memory-ingest
 * Headers: Authorization: Bearer <SERVICE_ROLE_KEY>
 * Body: { source, nodes, edges, caller }
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Environment variables
const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

interface Node {
  id: string
  source: string
  kind: string
  key: string
  name: string
  props: Record<string, any>
}

interface Edge {
  id: string
  source: string
  from_id: string
  to_id: string
  type: string
  props: Record<string, any>
}

interface IngestPayload {
  source: string
  nodes: Node[]
  edges: Edge[]
  caller?: string
  metadata?: Record<string, any>
}

interface IngestResult {
  success: boolean
  source: string
  nodes_upserted: number
  edges_upserted: number
  caller?: string
  timestamp: string
  errors?: string[]
}

serve(async (req) => {
  try {
    // Only allow POST
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        { status: 405, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Parse request body
    const payload: IngestPayload = await req.json()
    const { source, nodes, edges, caller, metadata } = payload

    // Validate required fields
    if (!source) {
      return new Response(
        JSON.stringify({ error: 'Missing required field: source' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    if (!Array.isArray(nodes) || !Array.isArray(edges)) {
      return new Response(
        JSON.stringify({ error: 'nodes and edges must be arrays' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      )
    }

    // Create Supabase service role client
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    const errors: string[] = []
    let nodesUpserted = 0
    let edgesUpserted = 0

    // Update source last_discovered_at and increment discovery_count
    const { error: sourceError } = await supabase
      .from('sources')
      .update({
        last_discovered_at: new Date().toISOString(),
        discovery_count: supabase.sql`discovery_count + 1`,
        metadata: metadata || {}
      })
      .eq('id', source)

    if (sourceError) {
      errors.push(`Source update error: ${sourceError.message}`)
    }

    // Upsert nodes in batches (Supabase has 1000 row limit per request)
    const BATCH_SIZE = 500
    for (let i = 0; i < nodes.length; i += BATCH_SIZE) {
      const batch = nodes.slice(i, i + BATCH_SIZE)

      // Enrich nodes with caller annotation if provided
      const enrichedNodes = batch.map(node => ({
        ...node,
        props: {
          ...node.props,
          ...(caller ? { _caller: caller } : {})
        },
        discovered_at: new Date().toISOString()
      }))

      const { error: nodeError } = await supabase
        .from('nodes')
        .upsert(enrichedNodes, {
          onConflict: 'id',
          ignoreDuplicates: false
        })

      if (nodeError) {
        errors.push(`Nodes batch ${i}-${i + BATCH_SIZE} error: ${nodeError.message}`)
      } else {
        nodesUpserted += batch.length
      }
    }

    // Upsert edges in batches
    for (let i = 0; i < edges.length; i += BATCH_SIZE) {
      const batch = edges.slice(i, i + BATCH_SIZE)

      // Enrich edges with caller annotation if provided
      const enrichedEdges = batch.map(edge => ({
        ...edge,
        props: {
          ...edge.props,
          ...(caller ? { _caller: caller } : {})
        },
        discovered_at: new Date().toISOString()
      }))

      const { error: edgeError } = await supabase
        .from('edges')
        .upsert(enrichedEdges, {
          onConflict: 'id',
          ignoreDuplicates: false
        })

      if (edgeError) {
        errors.push(`Edges batch ${i}-${i + BATCH_SIZE} error: ${edgeError.message}`)
      } else {
        edgesUpserted += batch.length
      }
    }

    // Create snapshot record
    const { error: snapshotError } = await supabase
      .from('snapshots')
      .insert({
        sources: [source],
        node_count: nodesUpserted,
        edge_count: edgesUpserted,
        graph_data: {
          source,
          nodes: nodes.slice(0, 100), // Store sample for reference
          edges: edges.slice(0, 100),
          caller,
          metadata
        },
        metadata: {
          caller,
          total_nodes: nodes.length,
          total_edges: edges.length,
          has_errors: errors.length > 0
        }
      })

    if (snapshotError) {
      errors.push(`Snapshot creation error: ${snapshotError.message}`)
    }

    // Build result
    const result: IngestResult = {
      success: errors.length === 0,
      source,
      nodes_upserted: nodesUpserted,
      edges_upserted: edgesUpserted,
      caller,
      timestamp: new Date().toISOString(),
      ...(errors.length > 0 ? { errors } : {})
    }

    return new Response(
      JSON.stringify(result),
      {
        status: errors.length === 0 ? 200 : 207, // 207 Multi-Status for partial success
        headers: { 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Memory ingest error:', error)
    return new Response(
      JSON.stringify({
        success: false,
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      }),
      {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
})

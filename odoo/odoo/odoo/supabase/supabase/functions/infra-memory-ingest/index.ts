// =============================================================================
// INFRA-MEMORY-INGEST - Infrastructure Discovery Memory Ingestion
// =============================================================================
// POST: Accepts infrastructure discovery results and stores in Knowledge Graph
// Supports: vercel, supabase, digitalocean, docker, odoo, github sources
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface IngestRequest {
  tenant_id?: string;
  source_type: "vercel" | "supabase" | "digitalocean" | "docker" | "odoo" | "github" | "all";
  nodes: NodePayload[];
  edges: EdgePayload[];
  metadata?: Record<string, unknown>;
}

interface NodePayload {
  kind: string;
  key: string;
  label: string;
  attrs?: Record<string, unknown>;
}

interface EdgePayload {
  src_key: string;
  predicate: string;
  dst_key: string;
  weight?: number;
  source_type?: string;
  source_ref?: string;
}

interface IngestResult {
  ok: boolean;
  run_id?: string;
  nodes_processed: number;
  edges_processed: number;
  errors: string[];
}

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SYSTEM_TENANT_ID = "00000000-0000-0000-0000-000000000001";

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
    status,
  });
}

function errorResponse(message: string, status = 400): Response {
  return jsonResponse({ ok: false, error: message }, status);
}

// -----------------------------------------------------------------------------
// Node/Edge Processing
// -----------------------------------------------------------------------------

async function upsertNode(
  supabase: SupabaseClient,
  tenantId: string,
  node: NodePayload
): Promise<{ node_id: string | null; error: string | null }> {
  try {
    const { data, error } = await supabase.rpc("kg.upsert_node", {
      p_tenant: tenantId,
      p_kind: node.kind,
      p_key: node.key,
      p_label: node.label,
      p_attrs: node.attrs || {},
    });

    if (error) {
      return { node_id: null, error: error.message };
    }

    return { node_id: data, error: null };
  } catch (e) {
    return { node_id: null, error: (e as Error).message };
  }
}

async function getNodeId(
  supabase: SupabaseClient,
  tenantId: string,
  key: string
): Promise<string | null> {
  const { data, error } = await supabase
    .from("kg.nodes")
    .select("node_id")
    .eq("tenant_id", tenantId)
    .eq("key", key)
    .single();

  if (error || !data) return null;
  return data.node_id;
}

async function upsertEdge(
  supabase: SupabaseClient,
  tenantId: string,
  edge: EdgePayload,
  nodeKeyToId: Map<string, string>
): Promise<{ edge_id: string | null; error: string | null }> {
  try {
    // Resolve node IDs
    let srcNodeId = nodeKeyToId.get(edge.src_key);
    let dstNodeId = nodeKeyToId.get(edge.dst_key);

    // If not in map, try to find in DB
    if (!srcNodeId) {
      srcNodeId = await getNodeId(supabase, tenantId, edge.src_key) || undefined;
    }
    if (!dstNodeId) {
      dstNodeId = await getNodeId(supabase, tenantId, edge.dst_key) || undefined;
    }

    if (!srcNodeId || !dstNodeId) {
      return {
        edge_id: null,
        error: `Could not resolve node IDs for edge: ${edge.src_key} -> ${edge.dst_key}`,
      };
    }

    const { data, error } = await supabase.rpc("kg.upsert_edge", {
      p_tenant: tenantId,
      p_src_node_id: srcNodeId,
      p_predicate: edge.predicate,
      p_dst_node_id: dstNodeId,
      p_weight: edge.weight || 1.0,
      p_source_type: edge.source_type || null,
      p_source_ref: edge.source_ref || null,
    });

    if (error) {
      return { edge_id: null, error: error.message };
    }

    return { edge_id: data, error: null };
  } catch (e) {
    return { edge_id: null, error: (e as Error).message };
  }
}

// -----------------------------------------------------------------------------
// Main Ingestion Logic
// -----------------------------------------------------------------------------

async function ingestDiscoveryResults(
  supabase: SupabaseClient,
  request: IngestRequest
): Promise<IngestResult> {
  const tenantId = request.tenant_id || SYSTEM_TENANT_ID;
  const errors: string[] = [];
  let nodesProcessed = 0;
  let edgesProcessed = 0;

  // Start discovery run
  const { data: runId, error: runError } = await supabase.rpc("kg.start_discovery_run", {
    p_tenant: tenantId,
    p_discovery_type: request.source_type,
    p_metadata: request.metadata || {},
  });

  if (runError) {
    return {
      ok: false,
      nodes_processed: 0,
      edges_processed: 0,
      errors: [`Failed to start discovery run: ${runError.message}`],
    };
  }

  // Build node key to ID map as we process
  const nodeKeyToId = new Map<string, string>();

  // Process nodes
  for (const node of request.nodes) {
    const { node_id, error } = await upsertNode(supabase, tenantId, node);
    if (error) {
      errors.push(`Node ${node.key}: ${error}`);
    } else if (node_id) {
      nodeKeyToId.set(node.key, node_id);
      nodesProcessed++;
    }
  }

  // Process edges
  for (const edge of request.edges) {
    const { edge_id, error } = await upsertEdge(supabase, tenantId, edge, nodeKeyToId);
    if (error) {
      errors.push(`Edge ${edge.src_key}->${edge.dst_key}: ${error}`);
    } else if (edge_id) {
      edgesProcessed++;
    }
  }

  // Complete discovery run
  await supabase.rpc("kg.complete_discovery_run", {
    p_run_id: runId,
    p_nodes_discovered: nodesProcessed,
    p_edges_discovered: edgesProcessed,
    p_error_message: errors.length > 0 ? errors.slice(0, 5).join("; ") : null,
  });

  return {
    ok: errors.length === 0,
    run_id: runId,
    nodes_processed: nodesProcessed,
    edges_processed: edgesProcessed,
    errors,
  };
}

// -----------------------------------------------------------------------------
// Request Validation
// -----------------------------------------------------------------------------

function validateRequest(request: IngestRequest): string | null {
  if (!request.source_type) {
    return "source_type is required";
  }

  const validSources = ["vercel", "supabase", "digitalocean", "docker", "odoo", "github", "all"];
  if (!validSources.includes(request.source_type)) {
    return `Invalid source_type. Must be one of: ${validSources.join(", ")}`;
  }

  if (!Array.isArray(request.nodes)) {
    return "nodes must be an array";
  }

  if (!Array.isArray(request.edges)) {
    return "edges must be an array";
  }

  // Validate node structure
  for (const node of request.nodes) {
    if (!node.kind || !node.key || !node.label) {
      return `Invalid node: ${JSON.stringify(node)}. Required fields: kind, key, label`;
    }
  }

  // Validate edge structure
  for (const edge of request.edges) {
    if (!edge.src_key || !edge.predicate || !edge.dst_key) {
      return `Invalid edge: ${JSON.stringify(edge)}. Required fields: src_key, predicate, dst_key`;
    }
  }

  return null;
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  // Only accept POST
  if (req.method !== "POST") {
    return errorResponse("Method not allowed", 405);
  }

  try {
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
      {
        global: {
          headers: { Authorization: req.headers.get("Authorization") || "" },
        },
      }
    );

    // Parse request
    const request: IngestRequest = await req.json();

    // Validate
    const validationError = validateRequest(request);
    if (validationError) {
      return errorResponse(validationError);
    }

    // Log incoming request summary
    console.log(
      `Ingesting ${request.nodes.length} nodes and ${request.edges.length} edges from ${request.source_type}`
    );

    // Process ingestion
    const result = await ingestDiscoveryResults(supabase, request);

    // Log result
    console.log(
      `Ingestion complete: ${result.nodes_processed} nodes, ${result.edges_processed} edges, ${result.errors.length} errors`
    );

    // Return result
    const status = result.ok ? 200 : result.errors.length > 0 ? 207 : 500;
    return jsonResponse(result, status);
  } catch (error) {
    console.error("Ingestion error:", error);
    return errorResponse((error as Error).message || "Internal server error", 500);
  }
});

// =============================================================================
// CATALOG-SYNC - Unity Catalog Asset Synchronization
// =============================================================================
// Purpose: Sync assets between Odoo, Supabase, and external catalogs
// Endpoints:
//   POST /catalog-sync { action: "sync_odoo_models", ... }
//   POST /catalog-sync { action: "sync_scout_views", ... }
//   POST /catalog-sync { action: "register_asset", ... }
//   POST /catalog-sync { action: "search_assets", ... }
//   POST /catalog-sync { action: "get_tools", ... }
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface OdooModelInfo {
  model: string;
  name: string;
  description?: string;
  fields: Array<{
    name: string;
    type: string;
    string: string;
    required: boolean;
    readonly: boolean;
  }>;
}

interface AssetInput {
  fqdn: string;
  asset_type: string;
  system: string;
  title: string;
  description?: string;
  owner?: string;
  tags?: string[];
  uri?: string;
  metadata?: Record<string, unknown>;
  company_id?: number;
}

interface ToolDefinition {
  tool_key: string;
  tool_type: string;
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  returns?: Record<string, unknown>;
  requires_confirmation: boolean;
  allowed_roles: string[];
  tags: string[];
}

interface SearchRequest {
  query?: string;
  asset_type?: string;
  system?: string;
  tags?: string[];
  limit?: number;
}

interface SyncOdooRequest {
  odoo_url: string;
  odoo_db: string;
  models?: string[];
  session_id?: string;
}

interface SyncScoutRequest {
  schema_name?: string;
  include_views?: boolean;
}

interface CatalogRequest {
  action: string;
  data?: unknown;
}

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function buildFqdn(system: string, ...parts: string[]): string {
  return [system, ...parts].join(".");
}

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
// Actions
// -----------------------------------------------------------------------------

/**
 * Register or update a single asset in the catalog
 */
async function registerAsset(
  supabase: SupabaseClient,
  asset: AssetInput
): Promise<{ ok: boolean; asset_id?: string; error?: string }> {
  const { data, error } = await supabase
    .from("catalog.assets")
    .upsert(
      {
        fqdn: asset.fqdn,
        asset_type: asset.asset_type,
        system: asset.system,
        title: asset.title,
        description: asset.description,
        owner: asset.owner,
        tags: asset.tags || [],
        uri: asset.uri,
        metadata: asset.metadata || {},
        company_id: asset.company_id,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "fqdn" }
    )
    .select("id")
    .single();

  if (error) {
    return { ok: false, error: error.message };
  }

  return { ok: true, asset_id: data.id };
}

/**
 * Search assets in the catalog
 */
async function searchAssets(
  supabase: SupabaseClient,
  request: SearchRequest
): Promise<{ ok: boolean; assets?: unknown[]; error?: string }> {
  let query = supabase
    .from("catalog.assets")
    .select("id, fqdn, asset_type, system, title, description, owner, tags, uri, metadata, created_at")
    .eq("status", "active");

  if (request.asset_type) {
    query = query.eq("asset_type", request.asset_type);
  }

  if (request.system) {
    query = query.eq("system", request.system);
  }

  if (request.tags && request.tags.length > 0) {
    query = query.overlaps("tags", request.tags);
  }

  if (request.query) {
    // Use full-text search
    query = query.textSearch("search_vector", request.query, { type: "websearch" });
  }

  query = query.limit(request.limit || 20).order("updated_at", { ascending: false });

  const { data, error } = await query;

  if (error) {
    return { ok: false, error: error.message };
  }

  return { ok: true, assets: data };
}

/**
 * Get tool definitions for copilot
 */
async function getTools(
  supabase: SupabaseClient,
  tags?: string[]
): Promise<{ ok: boolean; tools?: ToolDefinition[]; error?: string }> {
  let query = supabase
    .from("catalog.tools")
    .select("tool_key, tool_type, name, description, parameters, returns, requires_confirmation, allowed_roles, tags")
    .eq("active", true);

  if (tags && tags.length > 0) {
    query = query.overlaps("tags", tags);
  }

  const { data, error } = await query.order("tool_key");

  if (error) {
    return { ok: false, error: error.message };
  }

  return { ok: true, tools: data as ToolDefinition[] };
}

/**
 * Get tool binding for execution
 */
async function getToolBinding(
  supabase: SupabaseClient,
  toolKey: string
): Promise<{ ok: boolean; binding?: Record<string, unknown>; error?: string }> {
  const { data: tool, error: toolError } = await supabase
    .from("catalog.tools")
    .select("id, tool_key, tool_type, requires_confirmation, allowed_roles")
    .eq("tool_key", toolKey)
    .eq("active", true)
    .single();

  if (toolError || !tool) {
    return { ok: false, error: `Tool not found: ${toolKey}` };
  }

  const { data: binding, error: bindingError } = await supabase
    .from("catalog.tool_bindings")
    .select("target_type, target_config, conditions")
    .eq("tool_id", tool.id)
    .eq("active", true)
    .order("priority", { ascending: false })
    .limit(1)
    .single();

  if (bindingError) {
    return { ok: false, error: `No binding found for tool: ${toolKey}` };
  }

  return {
    ok: true,
    binding: {
      tool_key: tool.tool_key,
      tool_type: tool.tool_type,
      requires_confirmation: tool.requires_confirmation,
      allowed_roles: tool.allowed_roles,
      target_type: binding.target_type,
      target_config: binding.target_config,
      conditions: binding.conditions,
    },
  };
}

/**
 * Sync Odoo models to catalog (called from Odoo bridge module)
 */
async function syncOdooModels(
  supabase: SupabaseClient,
  request: SyncOdooRequest,
  models: OdooModelInfo[]
): Promise<{ ok: boolean; synced: number; errors: string[] }> {
  const errors: string[] = [];
  let synced = 0;

  for (const model of models) {
    const fqdn = buildFqdn("odoo", request.odoo_db, model.model);

    const asset: AssetInput = {
      fqdn,
      asset_type: "odoo_model",
      system: "odoo",
      title: model.name,
      description: model.description || `Odoo model: ${model.model}`,
      tags: ["odoo", "model"],
      uri: `${request.odoo_url}/web#model=${model.model}&view_type=list`,
      metadata: {
        model: model.model,
        fields: model.fields,
        odoo_db: request.odoo_db,
      },
    };

    const result = await registerAsset(supabase, asset);
    if (result.ok) {
      synced++;
    } else {
      errors.push(`${model.model}: ${result.error}`);
    }
  }

  return { ok: errors.length === 0, synced, errors };
}

/**
 * Sync Scout views to catalog
 */
async function syncScoutViews(
  supabase: SupabaseClient,
  request: SyncScoutRequest
): Promise<{ ok: boolean; synced: number; errors: string[] }> {
  const schemaName = request.schema_name || "scout_gold";
  const errors: string[] = [];
  let synced = 0;

  // Get list of views/tables in the schema
  const { data: objects, error } = await supabase.rpc("pg_catalog_objects", {
    p_schema: schemaName,
  });

  if (error) {
    // Fallback: just register known gold views
    const knownViews = [
      { name: "sales_by_store", description: "Store performance summary" },
      { name: "sales_by_product", description: "Product performance with ranking" },
      { name: "customer_360", description: "Customer lifetime value and behavior" },
    ];

    for (const view of knownViews) {
      const fqdn = buildFqdn("supabase", "ipai", schemaName, view.name);

      const result = await registerAsset(supabase, {
        fqdn,
        asset_type: "view",
        system: "scout",
        title: view.name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        description: view.description,
        tags: ["scout", "gold", "analytics"],
        metadata: { schema: schemaName, object_name: view.name },
      });

      if (result.ok) synced++;
      else errors.push(`${view.name}: ${result.error}`);
    }

    return { ok: true, synced, errors };
  }

  // Register each object
  for (const obj of objects || []) {
    const fqdn = buildFqdn("supabase", "ipai", schemaName, obj.object_name);
    const assetType = obj.object_type === "VIEW" ? "view" : "table";

    const result = await registerAsset(supabase, {
      fqdn,
      asset_type: assetType,
      system: "scout",
      title: obj.object_name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
      description: obj.description || `Scout ${assetType}: ${obj.object_name}`,
      tags: ["scout", schemaName.replace("scout_", ""), "analytics"],
      metadata: {
        schema: schemaName,
        object_name: obj.object_name,
        object_type: obj.object_type,
        columns: obj.columns,
      },
    });

    if (result.ok) synced++;
    else errors.push(`${obj.object_name}: ${result.error}`);
  }

  return { ok: errors.length === 0, synced, errors };
}

/**
 * Get lineage for an asset
 */
async function getLineage(
  supabase: SupabaseClient,
  assetFqdn: string,
  direction: "upstream" | "downstream" = "upstream",
  depth = 3
): Promise<{ ok: boolean; lineage?: unknown[]; error?: string }> {
  // Get asset ID
  const { data: asset, error: assetError } = await supabase
    .from("catalog.assets")
    .select("id")
    .eq("fqdn", assetFqdn)
    .single();

  if (assetError || !asset) {
    return { ok: false, error: `Asset not found: ${assetFqdn}` };
  }

  // Call the appropriate lineage function
  const funcName = direction === "upstream" ? "get_upstream_lineage" : "get_downstream_lineage";

  const { data, error } = await supabase.rpc(funcName, {
    p_asset_id: asset.id,
    p_depth: depth,
  });

  if (error) {
    return { ok: false, error: error.message };
  }

  return { ok: true, lineage: data };
}

/**
 * Check permission for a principal on an asset
 */
async function checkPermission(
  supabase: SupabaseClient,
  assetFqdn: string,
  principalKey: string,
  permission: string
): Promise<{ ok: boolean; allowed: boolean; error?: string }> {
  const { data, error } = await supabase.rpc("catalog.check_permission", {
    p_asset_fqdn: assetFqdn,
    p_principal_key: principalKey,
    p_permission: permission,
  });

  if (error) {
    return { ok: false, allowed: false, error: error.message };
  }

  return { ok: true, allowed: data };
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  // Handle CORS preflight
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
    const body: CatalogRequest = await req.json();
    const { action, data } = body;

    // Route to action handler
    switch (action) {
      case "register_asset": {
        const assetData = data as AssetInput;
        if (!assetData.fqdn || !assetData.asset_type || !assetData.system || !assetData.title) {
          return errorResponse("Missing required fields: fqdn, asset_type, system, title");
        }
        const result = await registerAsset(supabase, assetData);
        return jsonResponse(result);
      }

      case "search_assets": {
        const searchData = data as SearchRequest;
        const result = await searchAssets(supabase, searchData);
        return jsonResponse(result);
      }

      case "get_tools": {
        const tags = (data as { tags?: string[] })?.tags;
        const result = await getTools(supabase, tags);
        return jsonResponse(result);
      }

      case "get_tool_binding": {
        const toolKey = (data as { tool_key: string })?.tool_key;
        if (!toolKey) {
          return errorResponse("Missing tool_key");
        }
        const result = await getToolBinding(supabase, toolKey);
        return jsonResponse(result);
      }

      case "sync_odoo_models": {
        const syncData = data as { request: SyncOdooRequest; models: OdooModelInfo[] };
        if (!syncData.request || !syncData.models) {
          return errorResponse("Missing request or models");
        }
        const result = await syncOdooModels(supabase, syncData.request, syncData.models);
        return jsonResponse(result);
      }

      case "sync_scout_views": {
        const syncData = (data as SyncScoutRequest) || {};
        const result = await syncScoutViews(supabase, syncData);
        return jsonResponse(result);
      }

      case "get_lineage": {
        const lineageData = data as {
          fqdn: string;
          direction?: "upstream" | "downstream";
          depth?: number;
        };
        if (!lineageData.fqdn) {
          return errorResponse("Missing fqdn");
        }
        const result = await getLineage(
          supabase,
          lineageData.fqdn,
          lineageData.direction,
          lineageData.depth
        );
        return jsonResponse(result);
      }

      case "check_permission": {
        const permData = data as {
          fqdn: string;
          principal_key: string;
          permission: string;
        };
        if (!permData.fqdn || !permData.principal_key || !permData.permission) {
          return errorResponse("Missing fqdn, principal_key, or permission");
        }
        const result = await checkPermission(
          supabase,
          permData.fqdn,
          permData.principal_key,
          permData.permission
        );
        return jsonResponse(result);
      }

      default:
        return errorResponse(`Unknown action: ${action}`);
    }
  } catch (error) {
    console.error("Catalog sync error:", error);
    return errorResponse(error.message || "Internal server error", 500);
  }
});

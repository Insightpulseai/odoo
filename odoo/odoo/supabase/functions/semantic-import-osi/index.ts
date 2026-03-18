// =============================================================================
// SEMANTIC-IMPORT-OSI - Import Open Semantics Interface payload
// =============================================================================
// POST: Upsert asset + semantic model + dimensions + metrics
// Optionally stores YAML snapshot in semantic_exports
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface DimensionInput {
  name: string;
  label?: string;
  description?: string;
  expr: string;
  data_type?: string;
  is_time_dimension?: boolean;
  time_grain?: string;
  hierarchy_level?: number;
  parent_dimension?: string;
  tags?: string[];
  is_hidden?: boolean;
}

interface MetricInput {
  name: string;
  label?: string;
  description?: string;
  metric_type?: string;
  aggregation?: string;
  expr: string;
  depends_on?: string[];
  formula?: string;
  format_string?: string;
  unit?: string;
  filters?: unknown[];
  time_grains?: string[];
  tags?: string[];
  is_hidden?: boolean;
}

interface RelationshipInput {
  name: string;
  description?: string;
  to_model: string;
  join_type?: string;
  on_clause: string;
  from_cardinality?: string;
  to_cardinality?: string;
}

interface ModelInput {
  name: string;
  label?: string;
  description?: string;
  source_type?: string;
  source_ref: string;
  primary_key?: string[];
  time_dimension?: string;
  default_time_grain?: string;
  default_filters?: unknown[];
}

interface OSIPayload {
  asset_fqdn: string;
  asset_title?: string;
  asset_description?: string;
  asset_tags?: string[];
  model: ModelInput;
  dimensions: DimensionInput[];
  metrics: MetricInput[];
  relationships?: RelationshipInput[];
  store_export?: boolean;
  export_format?: string;
}

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

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
// Import Logic
// -----------------------------------------------------------------------------

async function importOSI(
  supabase: SupabaseClient,
  payload: OSIPayload
): Promise<{ ok: boolean; model_id?: string; stats?: Record<string, number>; error?: string }> {
  const stats = { dimensions: 0, metrics: 0, relationships: 0 };

  try {
    // 1. Upsert asset
    const { data: asset, error: assetError } = await supabase
      .from("catalog.assets")
      .upsert(
        {
          fqdn: payload.asset_fqdn,
          asset_type: "table",
          system: payload.asset_fqdn.startsWith("odoo") ? "odoo" : "scout",
          title: payload.asset_title || payload.model.name,
          description: payload.asset_description || payload.model.description,
          tags: payload.asset_tags || ["semantic"],
          status: "active",
        },
        { onConflict: "fqdn" }
      )
      .select("id")
      .single();

    if (assetError) {
      return { ok: false, error: `Asset upsert failed: ${assetError.message}` };
    }

    // 2. Upsert semantic model
    const { data: model, error: modelError } = await supabase
      .from("catalog.semantic_models")
      .upsert(
        {
          asset_id: asset.id,
          name: payload.model.name,
          label: payload.model.label,
          description: payload.model.description,
          source_type: payload.model.source_type || "table",
          source_ref: payload.model.source_ref,
          primary_key: payload.model.primary_key,
          time_dimension: payload.model.time_dimension,
          default_time_grain: payload.model.default_time_grain,
          default_filters: payload.model.default_filters || [],
          status: "active",
        },
        { onConflict: "asset_id,name" }
      )
      .select("id")
      .single();

    if (modelError) {
      return { ok: false, error: `Model upsert failed: ${modelError.message}` };
    }

    // 3. Upsert dimensions
    for (const dim of payload.dimensions) {
      const { error: dimError } = await supabase.from("catalog.semantic_dimensions").upsert(
        {
          model_id: model.id,
          name: dim.name,
          label: dim.label,
          description: dim.description,
          expr: dim.expr,
          data_type: dim.data_type || "string",
          is_time_dimension: dim.is_time_dimension || false,
          time_grain: dim.time_grain,
          hierarchy_level: dim.hierarchy_level,
          tags: dim.tags || [],
          is_hidden: dim.is_hidden || false,
        },
        { onConflict: "model_id,name" }
      );

      if (!dimError) stats.dimensions++;
    }

    // 4. Upsert metrics
    for (const met of payload.metrics) {
      const { error: metError } = await supabase.from("catalog.semantic_metrics").upsert(
        {
          model_id: model.id,
          name: met.name,
          label: met.label,
          description: met.description,
          metric_type: met.metric_type || "simple",
          aggregation: met.aggregation,
          expr: met.expr,
          depends_on: met.depends_on,
          formula: met.formula,
          format_string: met.format_string,
          unit: met.unit,
          filters: met.filters || [],
          time_grains: met.time_grains,
          tags: met.tags || [],
          is_hidden: met.is_hidden || false,
        },
        { onConflict: "model_id,name" }
      );

      if (!metError) stats.metrics++;
    }

    // 5. Upsert relationships (if any)
    if (payload.relationships) {
      for (const rel of payload.relationships) {
        // Find target model
        const { data: toModel } = await supabase
          .from("catalog.semantic_models")
          .select("id")
          .eq("name", rel.to_model)
          .single();

        if (toModel) {
          const { error: relError } = await supabase.from("catalog.semantic_relationships").upsert(
            {
              from_model_id: model.id,
              to_model_id: toModel.id,
              name: rel.name,
              description: rel.description,
              join_type: rel.join_type || "left",
              on_clause: rel.on_clause,
              from_cardinality: rel.from_cardinality || "many",
              to_cardinality: rel.to_cardinality || "one",
              active: true,
            },
            { onConflict: "from_model_id,to_model_id,name" }
          );

          if (!relError) stats.relationships++;
        }
      }
    }

    // 6. Create lineage edge
    await supabase.rpc("catalog.create_semantic_lineage", {
      p_asset_fqdn: payload.asset_fqdn,
      p_model_name: payload.model.name,
    });

    // 7. Store export snapshot (optional)
    if (payload.store_export) {
      const format = payload.export_format || "json";
      const content =
        format === "yaml"
          ? (
              await supabase.rpc("catalog.export_semantic_yaml", {
                p_asset_fqdn: payload.asset_fqdn,
                p_model_name: payload.model.name,
              })
            ).data
          : JSON.stringify(payload, null, 2);

      await supabase.from("catalog.semantic_exports").insert({
        asset_id: asset.id,
        model_name: payload.model.name,
        format: format,
        version: new Date().toISOString().split("T")[0],
        content: content,
        exported_by: "semantic-import-osi",
        export_reason: "auto-snapshot on import",
      });
    }

    return { ok: true, model_id: model.id, stats };
  } catch (error) {
    return { ok: false, error: error.message || "Import failed" };
  }
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return errorResponse("Method not allowed", 405);
  }

  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
      {
        global: {
          headers: { Authorization: req.headers.get("Authorization") || "" },
        },
      }
    );

    const payload: OSIPayload = await req.json();

    // Validate required fields
    if (!payload.asset_fqdn) {
      return errorResponse("Missing asset_fqdn");
    }
    if (!payload.model || !payload.model.name || !payload.model.source_ref) {
      return errorResponse("Missing model.name or model.source_ref");
    }
    if (!payload.dimensions || payload.dimensions.length === 0) {
      return errorResponse("At least one dimension is required");
    }
    if (!payload.metrics || payload.metrics.length === 0) {
      return errorResponse("At least one metric is required");
    }

    const result = await importOSI(supabase, payload);
    return jsonResponse(result);
  } catch (error) {
    console.error("Semantic import error:", error);
    return errorResponse(error.message || "Internal server error", 500);
  }
});

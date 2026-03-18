// =============================================================================
// SEMANTIC-EXPORT-OSI - Export semantic model to JSON/YAML
// =============================================================================
// GET: Export semantic model in specified format
// Query params: asset_fqdn, model_name, format (json|yaml|both)
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

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

function yamlResponse(content: string): Response {
  return new Response(content, {
    headers: { ...corsHeaders, "Content-Type": "text/yaml" },
    status: 200,
  });
}

function errorResponse(message: string, status = 400): Response {
  return jsonResponse({ ok: false, error: message }, status);
}

// -----------------------------------------------------------------------------
// YAML Generator (Simple)
// -----------------------------------------------------------------------------

function toYaml(model: Record<string, unknown>): string {
  const m = model.model as Record<string, unknown>;
  const dims = model.dimensions as Record<string, unknown>[];
  const mets = model.metrics as Record<string, unknown>[];
  const rels = model.relationships as Record<string, unknown>[];

  let yaml = `# Open Semantics Interface (OSI) Export
# Model: ${m.name}
# Generated: ${new Date().toISOString()}

version: "1.0"

model:
  name: ${m.name}
  label: ${m.label || m.name}
  description: "${m.description || ""}"
  source:
    type: ${m.source_type || "table"}
    ref: ${m.source_ref}
`;

  if (m.primary_key) {
    yaml += `  primary_key: [${(m.primary_key as string[]).join(", ")}]\n`;
  }

  if (m.time_dimension) {
    yaml += `  time_dimension: ${m.time_dimension}\n`;
    yaml += `  default_time_grain: ${m.default_time_grain || "day"}\n`;
  }

  // Dimensions
  yaml += `\ndimensions:\n`;
  for (const d of dims) {
    yaml += `  - name: ${d.name}\n`;
    if (d.label) yaml += `    label: "${d.label}"\n`;
    if (d.description) yaml += `    description: "${d.description}"\n`;
    yaml += `    expr: "${d.expr}"\n`;
    yaml += `    type: ${d.data_type || "string"}\n`;
    if (d.is_time_dimension) {
      yaml += `    is_time_dimension: true\n`;
      if (d.time_grain) yaml += `    time_grain: ${d.time_grain}\n`;
    }
    if (d.tags && (d.tags as string[]).length > 0) {
      yaml += `    tags: [${(d.tags as string[]).join(", ")}]\n`;
    }
  }

  // Metrics
  yaml += `\nmetrics:\n`;
  for (const met of mets) {
    yaml += `  - name: ${met.name}\n`;
    if (met.label) yaml += `    label: "${met.label}"\n`;
    if (met.description) yaml += `    description: "${met.description}"\n`;
    yaml += `    type: ${met.metric_type || "simple"}\n`;
    if (met.aggregation) yaml += `    aggregation: ${met.aggregation}\n`;
    yaml += `    expr: "${met.expr}"\n`;
    if (met.formula) yaml += `    formula: "${met.formula}"\n`;
    if (met.format_string) yaml += `    format: "${met.format_string}"\n`;
    if (met.unit) yaml += `    unit: "${met.unit}"\n`;
    if (met.tags && (met.tags as string[]).length > 0) {
      yaml += `    tags: [${(met.tags as string[]).join(", ")}]\n`;
    }
  }

  // Relationships
  if (rels && rels.length > 0) {
    yaml += `\nrelationships:\n`;
    for (const r of rels) {
      yaml += `  - name: ${r.name}\n`;
      yaml += `    to_model: ${r.to_model}\n`;
      yaml += `    join_type: ${r.join_type || "left"}\n`;
      yaml += `    on: "${r.on_clause}"\n`;
      yaml += `    cardinality: ${r.cardinality || "many-to-one"}\n`;
    }
  }

  return yaml;
}

// -----------------------------------------------------------------------------
// Export Logic
// -----------------------------------------------------------------------------

async function exportOSI(
  supabase: SupabaseClient,
  assetFqdn: string,
  modelName: string,
  format: string
): Promise<{ ok: boolean; json?: unknown; yaml?: string; error?: string }> {
  // Get semantic model using the helper function
  const { data: modelData, error } = await supabase.rpc("catalog.get_semantic_model", {
    p_asset_fqdn: assetFqdn,
    p_model_name: modelName,
  });

  if (error) {
    return { ok: false, error: error.message };
  }

  if (!modelData || Object.keys(modelData).length === 0) {
    return { ok: false, error: "Semantic model not found" };
  }

  const result: { ok: boolean; json?: unknown; yaml?: string } = { ok: true };

  if (format === "json" || format === "both") {
    result.json = {
      version: "1.0",
      asset_fqdn: assetFqdn,
      exported_at: new Date().toISOString(),
      ...modelData,
    };
  }

  if (format === "yaml" || format === "both") {
    result.yaml = toYaml(modelData);
  }

  return result;
}

// -----------------------------------------------------------------------------
// Main Handler
// -----------------------------------------------------------------------------

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  if (req.method !== "GET" && req.method !== "POST") {
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

    // Parse params from URL or body
    let assetFqdn: string;
    let modelName: string;
    let format: string;

    if (req.method === "GET") {
      const url = new URL(req.url);
      assetFqdn = url.searchParams.get("asset_fqdn") || "";
      modelName = url.searchParams.get("model_name") || "";
      format = url.searchParams.get("format") || "json";
    } else {
      const body = await req.json();
      assetFqdn = body.asset_fqdn || "";
      modelName = body.model_name || "";
      format = body.format || "json";
    }

    // Validate
    if (!assetFqdn || !modelName) {
      return errorResponse("Missing asset_fqdn or model_name");
    }

    if (!["json", "yaml", "both"].includes(format)) {
      return errorResponse("Invalid format. Use: json, yaml, or both");
    }

    const result = await exportOSI(supabase, assetFqdn, modelName, format);

    if (!result.ok) {
      return errorResponse(result.error || "Export failed");
    }

    // Return based on format
    if (format === "yaml" && result.yaml) {
      return yamlResponse(result.yaml);
    }

    return jsonResponse(result);
  } catch (error) {
    console.error("Semantic export error:", error);
    return errorResponse(error.message || "Internal server error", 500);
  }
});

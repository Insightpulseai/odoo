// =============================================================================
// SEMANTIC-QUERY - Validate and resolve semantic queries
// =============================================================================
// POST: Validates dimensions/metrics and returns resolved query plan
// Executor intentionally NOT implemented - use BI tool connector
// =============================================================================

import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient, SupabaseClient } from "https://esm.sh/@supabase/supabase-js@2";

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface SemanticQueryRequest {
  asset_fqdn: string;
  model_name: string;
  dimensions: string[];
  metrics: string[];
  filters?: FilterCondition[];
  time_grain?: string;
  time_range?: {
    start: string;
    end: string;
  };
  order_by?: OrderBy[];
  limit?: number;
}

interface FilterCondition {
  dimension: string;
  operator: string; // eq, ne, gt, gte, lt, lte, in, not_in, like, between
  value: unknown;
}

interface OrderBy {
  field: string;
  direction: "asc" | "desc";
}

interface QueryPlan {
  model: string;
  asset_fqdn: string;
  select: SelectItem[];
  from: string;
  joins: JoinClause[];
  where: string[];
  group_by: string[];
  order_by: string[];
  limit: number;
  sql_preview: string;
}

interface SelectItem {
  name: string;
  expr: string;
  type: "dimension" | "metric";
}

interface JoinClause {
  table: string;
  type: string;
  on: string;
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

function buildFilterSql(filter: FilterCondition, dimExpr: string): string {
  const ops: Record<string, string> = {
    eq: "=",
    ne: "!=",
    gt: ">",
    gte: ">=",
    lt: "<",
    lte: "<=",
    like: "LIKE",
  };

  const op = ops[filter.operator] || "=";

  if (filter.operator === "in") {
    const values = Array.isArray(filter.value) ? filter.value : [filter.value];
    return `${dimExpr} IN (${values.map((v) => (typeof v === "string" ? `'${v}'` : v)).join(", ")})`;
  }

  if (filter.operator === "not_in") {
    const values = Array.isArray(filter.value) ? filter.value : [filter.value];
    return `${dimExpr} NOT IN (${values.map((v) => (typeof v === "string" ? `'${v}'` : v)).join(", ")})`;
  }

  if (filter.operator === "between" && Array.isArray(filter.value) && filter.value.length === 2) {
    return `${dimExpr} BETWEEN '${filter.value[0]}' AND '${filter.value[1]}'`;
  }

  const val = typeof filter.value === "string" ? `'${filter.value}'` : filter.value;
  return `${dimExpr} ${op} ${val}`;
}

// -----------------------------------------------------------------------------
// Query Resolution
// -----------------------------------------------------------------------------

async function resolveQuery(
  supabase: SupabaseClient,
  request: SemanticQueryRequest
): Promise<{ ok: boolean; plan?: QueryPlan; validation?: Record<string, unknown>; error?: string }> {
  // 1. Get semantic model
  const { data: modelData, error: modelError } = await supabase.rpc("catalog.get_semantic_model", {
    p_asset_fqdn: request.asset_fqdn,
    p_model_name: request.model_name,
  });

  if (modelError || !modelData || Object.keys(modelData).length === 0) {
    return { ok: false, error: modelError?.message || "Semantic model not found" };
  }

  const model = modelData.model;
  const allDimensions = modelData.dimensions as Record<string, unknown>[];
  const allMetrics = modelData.metrics as Record<string, unknown>[];
  const relationships = modelData.relationships as Record<string, unknown>[];

  // 2. Validate requested dimensions
  const dimMap = new Map(allDimensions.map((d) => [d.name as string, d]));
  const invalidDims = request.dimensions.filter((d) => !dimMap.has(d));

  if (invalidDims.length > 0) {
    return {
      ok: false,
      error: `Invalid dimensions: ${invalidDims.join(", ")}`,
      validation: {
        requested: request.dimensions,
        available: allDimensions.map((d) => d.name),
      },
    };
  }

  // 3. Validate requested metrics
  const metMap = new Map(allMetrics.map((m) => [m.name as string, m]));
  const invalidMets = request.metrics.filter((m) => !metMap.has(m));

  if (invalidMets.length > 0) {
    return {
      ok: false,
      error: `Invalid metrics: ${invalidMets.join(", ")}`,
      validation: {
        requested: request.metrics,
        available: allMetrics.map((m) => m.name),
      },
    };
  }

  // 4. Build query plan
  const selectItems: SelectItem[] = [];
  const groupByExprs: string[] = [];
  const whereConditions: string[] = [];
  const orderByExprs: string[] = [];

  // Add dimensions
  for (const dimName of request.dimensions) {
    const dim = dimMap.get(dimName);
    if (dim) {
      selectItems.push({
        name: dimName,
        expr: dim.expr as string,
        type: "dimension",
      });
      groupByExprs.push(dim.expr as string);
    }
  }

  // Add metrics
  for (const metName of request.metrics) {
    const met = metMap.get(metName);
    if (met) {
      let expr = met.expr as string;
      const metricType = met.metric_type as string;
      const aggregation = met.aggregation as string;

      if (metricType === "simple" && aggregation) {
        expr = `${aggregation.toUpperCase()}(${expr})`;
      } else if (metricType === "derived" && met.formula) {
        expr = met.formula as string;
      }

      selectItems.push({
        name: metName,
        expr: expr,
        type: "metric",
      });
    }
  }

  // Add filters
  if (request.filters) {
    for (const filter of request.filters) {
      const dim = dimMap.get(filter.dimension);
      if (dim) {
        whereConditions.push(buildFilterSql(filter, dim.expr as string));
      }
    }
  }

  // Add time range filter
  if (request.time_range && model.time_dimension) {
    const timeDim = dimMap.get(model.time_dimension);
    if (timeDim) {
      whereConditions.push(
        `${timeDim.expr} >= '${request.time_range.start}' AND ${timeDim.expr} <= '${request.time_range.end}'`
      );
    }
  }

  // Add order by
  if (request.order_by) {
    for (const ob of request.order_by) {
      const dim = dimMap.get(ob.field);
      const met = metMap.get(ob.field);
      if (dim) {
        orderByExprs.push(`${dim.expr} ${ob.direction.toUpperCase()}`);
      } else if (met) {
        orderByExprs.push(`${ob.field} ${ob.direction.toUpperCase()}`);
      }
    }
  }

  // Build SQL preview
  const selectClause = selectItems.map((s) => `${s.expr} AS ${s.name}`).join(",\n    ");
  const fromClause = model.source_ref;
  const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join("\n  AND ")}` : "";
  const groupByClause = groupByExprs.length > 0 ? `GROUP BY ${groupByExprs.join(", ")}` : "";
  const orderByClause = orderByExprs.length > 0 ? `ORDER BY ${orderByExprs.join(", ")}` : "";
  const limitClause = `LIMIT ${request.limit || 1000}`;

  const sqlPreview = `SELECT
    ${selectClause}
FROM ${fromClause}
${whereClause}
${groupByClause}
${orderByClause}
${limitClause}`.trim();

  const plan: QueryPlan = {
    model: model.name,
    asset_fqdn: request.asset_fqdn,
    select: selectItems,
    from: model.source_ref,
    joins: [], // Would be populated from relationships if cross-model query
    where: whereConditions,
    group_by: groupByExprs,
    order_by: orderByExprs,
    limit: request.limit || 1000,
    sql_preview: sqlPreview,
  };

  return {
    ok: true,
    plan,
    validation: {
      dimensions_valid: true,
      metrics_valid: true,
      note: "Query execution intentionally not implemented. Use the sql_preview with your BI tool or query engine.",
    },
  };
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

    const request: SemanticQueryRequest = await req.json();

    // Validate required fields
    if (!request.asset_fqdn || !request.model_name) {
      return errorResponse("Missing asset_fqdn or model_name");
    }

    if (!request.dimensions || request.dimensions.length === 0) {
      return errorResponse("At least one dimension is required");
    }

    if (!request.metrics || request.metrics.length === 0) {
      return errorResponse("At least one metric is required");
    }

    const result = await resolveQuery(supabase, request);

    if (!result.ok) {
      return jsonResponse(result, result.validation ? 400 : 404);
    }

    return jsonResponse(result);
  } catch (error) {
    console.error("Semantic query error:", error);
    return errorResponse(error.message || "Internal server error", 500);
  }
});

/**
 * Odoo Template Export Edge Function
 *
 * Generates clean CSV/JSON import templates from the odoo_dict.fields data dictionary.
 *
 * Endpoints:
 * - GET /odoo-template-export?model=project.task&format=csv
 * - GET /odoo-template-export?template=finance-ppm-tasks&format=csv
 * - GET /odoo-template-export?model=project.task&format=json (returns field metadata)
 *
 * Query params:
 * - model: Odoo model name (e.g., 'project.task')
 * - template: Predefined template slug (e.g., 'finance-ppm-tasks')
 * - format: 'csv' | 'json' (default: 'csv')
 * - include_examples: 'true' to include example row (csv only)
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface DictField {
  id: number;
  model_name: string;
  field_name: string;
  label: string;
  field_type: string;
  required: boolean;
  is_key: boolean;
  relation_model: string | null;
  import_column: string;
  description: string | null;
  example_value: string | null;
  default_value: string | null;
  domain: string;
  sequence: number;
}

interface Template {
  slug: string;
  name: string;
  description: string | null;
  model_name: string;
  field_names: string[];
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const modelName = url.searchParams.get("model");
    const templateSlug = url.searchParams.get("template");
    const format = url.searchParams.get("format") || "csv";
    const includeExamples = url.searchParams.get("include_examples") === "true";

    if (!modelName && !templateSlug) {
      return new Response(
        JSON.stringify({
          error: "Missing required parameter: 'model' or 'template'",
          usage: {
            by_model: "?model=project.task&format=csv",
            by_template: "?template=finance-ppm-tasks&format=csv",
          },
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Initialize Supabase client
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    let fields: DictField[] = [];
    let templateInfo: Template | null = null;

    if (templateSlug) {
      // Fetch template first
      const { data: template, error: tplError } = await supabase
        .from("odoo_dict.templates")
        .select("*")
        .eq("slug", templateSlug)
        .eq("is_active", true)
        .single();

      if (tplError || !template) {
        return new Response(
          JSON.stringify({
            error: `Template not found: ${templateSlug}`,
            available: await getAvailableTemplates(supabase),
          }),
          {
            status: 404,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      }

      templateInfo = template as Template;

      // Fetch fields in template order
      const { data: fieldData, error: fieldError } = await supabase
        .from("odoo_dict.fields")
        .select("*")
        .eq("model_name", template.model_name)
        .in("field_name", template.field_names)
        .eq("is_active", true);

      if (fieldError) {
        throw fieldError;
      }

      // Reorder fields according to template.field_names
      const fieldMap = new Map(
        (fieldData as DictField[]).map((f) => [f.field_name, f])
      );
      fields = template.field_names
        .map((name: string) => fieldMap.get(name))
        .filter(Boolean) as DictField[];
    } else if (modelName) {
      // Fetch all active fields for model
      const { data, error } = await supabase
        .from("odoo_dict.fields")
        .select("*")
        .eq("model_name", modelName)
        .eq("is_active", true)
        .order("sequence", { ascending: true })
        .order("id", { ascending: true });

      if (error) {
        throw error;
      }

      if (!data || data.length === 0) {
        return new Response(
          JSON.stringify({
            error: `No fields found for model: ${modelName}`,
            available: await getAvailableModels(supabase),
          }),
          {
            status: 404,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      }

      fields = data as DictField[];
    }

    // Generate output based on format
    if (format === "json") {
      return new Response(
        JSON.stringify(
          {
            model: modelName || templateInfo?.model_name,
            template: templateSlug || null,
            fields: fields.map((f) => ({
              field_name: f.field_name,
              import_column: f.import_column,
              label: f.label,
              field_type: f.field_type,
              required: f.required,
              is_key: f.is_key,
              relation_model: f.relation_model,
              description: f.description,
              example_value: f.example_value,
              default_value: f.default_value,
            })),
          },
          null,
          2
        ),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // CSV format
    const headers = fields.map((f) => f.import_column);
    const csvRows: string[] = [headers.map(escapeCSV).join(",")];

    if (includeExamples) {
      const exampleRow = fields.map((f) => f.example_value || "");
      csvRows.push(exampleRow.map(escapeCSV).join(","));
    }

    const csvContent = csvRows.join("\n");
    const filename =
      templateSlug ||
      modelName?.replace(/\./g, "_") ||
      "odoo_import_template";

    return new Response(csvContent, {
      headers: {
        ...corsHeaders,
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": `attachment; filename="${filename}.csv"`,
      },
    });
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        details: error instanceof Error ? error.message : String(error),
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

function escapeCSV(value: string): string {
  if (!value) return "";
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

async function getAvailableModels(
  supabase: ReturnType<typeof createClient>
): Promise<string[]> {
  const { data } = await supabase
    .from("odoo_dict.fields")
    .select("model_name")
    .eq("is_active", true);

  if (!data) return [];
  return [...new Set(data.map((r) => r.model_name))].sort();
}

async function getAvailableTemplates(
  supabase: ReturnType<typeof createClient>
): Promise<string[]> {
  const { data } = await supabase
    .from("odoo_dict.templates")
    .select("slug")
    .eq("is_active", true);

  if (!data) return [];
  return data.map((r) => r.slug).sort();
}

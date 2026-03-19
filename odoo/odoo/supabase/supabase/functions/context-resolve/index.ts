/**
 * Context Resolution Edge Function
 *
 * Resolves platform context (tenant/account/project) to Odoo entity IDs.
 * Used by AI agents and React apps to get Odoo coordinates for the current user context.
 *
 * Returns:
 * - odoo_db: Which Odoo database to connect to
 * - odoo_company_id: res.company.id (if multi-company mode)
 * - odoo_partner_id: res.partner.id (customer/vendor org)
 * - odoo_project_id: project.project.id (delivery scope)
 * - odoo_analytic_account_id: account.analytic.account.id (cost spine)
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface ContextRequest {
  tenant_id: string;
  account_id?: string;
  project_id?: string;
  environment_id?: string;
}

interface OdooContext {
  ok: boolean;
  tenancy_mode?: "multi_db" | "multi_company";
  odoo_db?: string;
  odoo_company_id?: number;
  odoo_partner_id?: number;
  odoo_project_id?: number;
  odoo_analytic_account_id?: number;
  sync_enabled?: boolean;
  error?: string;
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // GET: Resolve from query params
    // POST: Resolve from body
    let contextReq: ContextRequest;

    if (req.method === "GET") {
      const url = new URL(req.url);
      contextReq = {
        tenant_id: url.searchParams.get("tenant_id") || "",
        account_id: url.searchParams.get("account_id") || undefined,
        project_id: url.searchParams.get("project_id") || undefined,
        environment_id: url.searchParams.get("environment_id") || undefined,
      };
    } else if (req.method === "POST") {
      contextReq = await req.json();
    } else {
      return new Response(
        JSON.stringify({ ok: false, error: "Method not allowed" }),
        {
          status: 405,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Validate required fields
    if (!contextReq.tenant_id) {
      return new Response(
        JSON.stringify({ ok: false, error: "tenant_id is required" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Call the resolve function
    const { data, error } = await supabase.rpc("resolve_odoo_context", {
      p_tenant_id: contextReq.tenant_id,
      p_account_id: contextReq.account_id || null,
      p_project_id: contextReq.project_id || null,
      p_environment_id: contextReq.environment_id || null,
    });

    if (error) {
      console.error("Context resolution error:", error);
      return new Response(
        JSON.stringify({ ok: false, error: error.message }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const context = data as OdooContext;

    // If resolution succeeded, also fetch analytic account details if available
    if (context.ok && context.odoo_analytic_account_id) {
      const { data: analyticData } = await supabase
        .from("analytic_account_cache")
        .select("name, code, balance, plan_name")
        .eq("tenant_id", contextReq.tenant_id)
        .eq("odoo_analytic_id", context.odoo_analytic_account_id)
        .single();

      if (analyticData) {
        (context as any).analytic_account = analyticData;
      }
    }

    return new Response(JSON.stringify(context), {
      status: context.ok ? 200 : 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("Unexpected error:", err);
    return new Response(
      JSON.stringify({ ok: false, error: "Internal server error" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

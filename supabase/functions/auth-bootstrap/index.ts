// ============================================================================
// Auth Bootstrap: Tenant + Owner Creation
// ============================================================================
// Purpose: Create new tenant with first owner user
//
// POST /auth-bootstrap
// Body: {
//   tenant: { slug, name, settings? },
//   owner: { email, password, display_name? }
// }
//
// Response: {
//   tenant: { id, slug, name },
//   user: { id, email, role },
//   access_token, refresh_token
// }
// ============================================================================

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface BootstrapRequest {
  tenant: {
    slug: string;
    name: string;
    settings?: Record<string, any>;
  };
  owner: {
    email: string;
    password: string;
    display_name?: string;
  };
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client with service role
    const supabaseAdmin = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false,
        },
      }
    );

    // Parse request body
    const body: BootstrapRequest = await req.json();

    // Validate input
    if (!body.tenant?.slug || !body.tenant?.name) {
      return new Response(
        JSON.stringify({ error: "Missing tenant slug or name" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    if (!body.owner?.email || !body.owner?.password) {
      return new Response(
        JSON.stringify({ error: "Missing owner email or password" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Validate tenant slug format
    if (!/^[a-z0-9-]+$/.test(body.tenant.slug)) {
      return new Response(
        JSON.stringify({
          error: "Tenant slug must contain only lowercase letters, numbers, and hyphens",
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Check if tenant slug already exists
    const { data: existingTenant } = await supabaseAdmin
      .from("tenants")
      .select("id")
      .eq("slug", body.tenant.slug)
      .single();

    if (existingTenant) {
      return new Response(
        JSON.stringify({ error: "Tenant slug already exists" }),
        {
          status: 409,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // 1. Create tenant
    const { data: tenant, error: tenantError } = await supabaseAdmin
      .from("tenants")
      .insert({
        slug: body.tenant.slug,
        name: body.tenant.name,
        settings: body.tenant.settings || {},
      })
      .select()
      .single();

    if (tenantError) {
      console.error("Tenant creation error:", tenantError);
      return new Response(
        JSON.stringify({ error: "Failed to create tenant", details: tenantError }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // 2. Create auth user
    const { data: authData, error: authError } =
      await supabaseAdmin.auth.admin.createUser({
        email: body.owner.email,
        password: body.owner.password,
        email_confirm: true, // Auto-confirm for bootstrap
        user_metadata: {
          display_name: body.owner.display_name || body.owner.email.split("@")[0],
        },
      });

    if (authError || !authData.user) {
      console.error("Auth user creation error:", authError);

      // Rollback tenant creation
      await supabaseAdmin.from("tenants").delete().eq("id", tenant.id);

      return new Response(
        JSON.stringify({
          error: "Failed to create user",
          details: authError,
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // 3. Create profile with owner role
    const { error: profileError } = await supabaseAdmin.from("profiles").insert({
      user_id: authData.user.id,
      tenant_id: tenant.id,
      role: "owner",
      display_name: body.owner.display_name || body.owner.email.split("@")[0],
    });

    if (profileError) {
      console.error("Profile creation error:", profileError);

      // Rollback user and tenant
      await supabaseAdmin.auth.admin.deleteUser(authData.user.id);
      await supabaseAdmin.from("tenants").delete().eq("id", tenant.id);

      return new Response(
        JSON.stringify({
          error: "Failed to create profile",
          details: profileError,
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // 4. Generate session tokens for immediate login
    const { data: sessionData, error: sessionError } =
      await supabaseAdmin.auth.admin.generateLink({
        type: "magiclink",
        email: body.owner.email,
      });

    // Log audit event
    await supabaseAdmin.from("audit_log").insert({
      tenant_id: tenant.id,
      user_id: authData.user.id,
      action: "tenant.bootstrapped",
      resource_type: "tenant",
      resource_id: tenant.id,
      metadata: {
        tenant_slug: tenant.slug,
        owner_email: body.owner.email,
      },
    });

    // Return success with session tokens
    return new Response(
      JSON.stringify({
        success: true,
        tenant: {
          id: tenant.id,
          slug: tenant.slug,
          name: tenant.name,
        },
        user: {
          id: authData.user.id,
          email: authData.user.email,
          role: "owner",
        },
        session: sessionData,
      }),
      {
        status: 201,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Bootstrap error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error", details: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

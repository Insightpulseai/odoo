// ============================================================================
// Tenant Invite: Add Users to Existing Tenant
// ============================================================================
// Purpose: Invite new users to existing tenant with specified role
//
// POST /tenant-invite
// Headers: Authorization: Bearer <user_jwt>
// Body: {
//   email: string,
//   role: 'admin' | 'finance' | 'ops' | 'viewer',
//   display_name?: string,
//   send_email?: boolean
// }
//
// Response: {
//   user: { id, email, role },
//   invitation_sent: boolean
// }
//
// Authorization: Only admin/owner can invite users
// ============================================================================

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

interface InviteRequest {
  email: string;
  role: "admin" | "finance" | "ops" | "viewer";
  display_name?: string;
  send_email?: boolean;
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    // Get JWT from Authorization header
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) {
      return new Response(JSON.stringify({ error: "Missing authorization" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Initialize Supabase client with user JWT
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? "",
      {
        global: {
          headers: { Authorization: authHeader },
        },
      }
    );

    // Get current user from JWT
    const {
      data: { user },
      error: userError,
    } = await supabaseClient.auth.getUser();

    if (userError || !user) {
      return new Response(JSON.stringify({ error: "Unauthorized" }), {
        status: 401,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Get current user's profile
    const { data: inviterProfile, error: profileError } = await supabaseClient
      .from("profiles")
      .select("tenant_id, role")
      .eq("user_id", user.id)
      .single();

    if (profileError || !inviterProfile) {
      return new Response(JSON.stringify({ error: "Profile not found" }), {
        status: 404,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Check authorization (only admin/owner can invite)
    if (!["owner", "admin"].includes(inviterProfile.role)) {
      return new Response(
        JSON.stringify({ error: "Insufficient permissions to invite users" }),
        {
          status: 403,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Parse request body
    const body: InviteRequest = await req.json();

    // Validate input
    if (!body.email || !body.role) {
      return new Response(
        JSON.stringify({ error: "Missing email or role" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Validate role
    const validRoles = ["admin", "finance", "ops", "viewer"];
    if (!validRoles.includes(body.role)) {
      return new Response(
        JSON.stringify({
          error: `Invalid role. Must be one of: ${validRoles.join(", ")}`,
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Only owners can invite other owners
    if (body.role === "owner" && inviterProfile.role !== "owner") {
      return new Response(
        JSON.stringify({ error: "Only owners can invite other owners" }),
        {
          status: 403,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Initialize admin client for user creation
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

    // Check if user already exists
    const { data: existingUser } = await supabaseAdmin.auth.admin.listUsers();
    const userExists = existingUser?.users.some((u) => u.email === body.email);

    if (userExists) {
      // Check if user already has profile in this tenant
      const { data: existingProfile } = await supabaseAdmin
        .from("profiles")
        .select("user_id, role")
        .eq("tenant_id", inviterProfile.tenant_id)
        .eq("user_id", (
          existingUser?.users.find((u) => u.email === body.email)
        )?.id || "")
        .single();

      if (existingProfile) {
        return new Response(
          JSON.stringify({
            error: "User already exists in this tenant",
            existing_role: existingProfile.role,
          }),
          {
            status: 409,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      }
    }

    // Create auth user (or get existing)
    let newUserId: string;

    if (userExists) {
      newUserId = existingUser?.users.find((u) => u.email === body.email)?.id || "";
    } else {
      // Generate temporary password (user will set via password reset)
      const tempPassword = crypto.randomUUID();

      const { data: authData, error: authError } =
        await supabaseAdmin.auth.admin.createUser({
          email: body.email,
          password: tempPassword,
          email_confirm: false, // Require email confirmation for invitations
          user_metadata: {
            display_name: body.display_name || body.email.split("@")[0],
            invited_by: user.id,
            invited_at: new Date().toISOString(),
          },
        });

      if (authError || !authData.user) {
        console.error("User creation error:", authError);
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

      newUserId = authData.user.id;
    }

    // Create profile in tenant
    const { error: profileInsertError } = await supabaseAdmin
      .from("profiles")
      .insert({
        user_id: newUserId,
        tenant_id: inviterProfile.tenant_id,
        role: body.role,
        display_name: body.display_name || body.email.split("@")[0],
      });

    if (profileInsertError) {
      console.error("Profile creation error:", profileInsertError);

      // Rollback user creation if new user
      if (!userExists) {
        await supabaseAdmin.auth.admin.deleteUser(newUserId);
      }

      return new Response(
        JSON.stringify({
          error: "Failed to create profile",
          details: profileInsertError,
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Send invitation email (if requested)
    let invitationSent = false;
    if (body.send_email !== false) {
      try {
        const { error: inviteError } =
          await supabaseAdmin.auth.admin.inviteUserByEmail(body.email);

        if (!inviteError) {
          invitationSent = true;
        } else {
          console.error("Invitation email error:", inviteError);
        }
      } catch (emailError) {
        console.error("Email sending failed:", emailError);
      }
    }

    // Log audit event
    await supabaseAdmin.from("audit_log").insert({
      tenant_id: inviterProfile.tenant_id,
      user_id: user.id,
      action: "user.invited",
      resource_type: "profile",
      resource_id: newUserId,
      metadata: {
        invitee_email: body.email,
        role: body.role,
        invitation_sent: invitationSent,
      },
    });

    // Return success
    return new Response(
      JSON.stringify({
        success: true,
        user: {
          id: newUserId,
          email: body.email,
          role: body.role,
        },
        invitation_sent: invitationSent,
      }),
      {
        status: 201,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Invitation error:", error);
    return new Response(
      JSON.stringify({ error: "Internal server error", details: error.message }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});

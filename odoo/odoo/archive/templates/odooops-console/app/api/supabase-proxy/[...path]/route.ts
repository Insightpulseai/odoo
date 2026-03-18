import { createSupabaseServerClient } from "@/lib/supabase/server";
import { NextRequest, NextResponse } from "next/server";

export const runtime = "edge";

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return handleRequest(req, resolvedParams, "GET");
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return handleRequest(req, resolvedParams, "POST");
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return handleRequest(req, resolvedParams, "PATCH");
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return handleRequest(req, resolvedParams, "DELETE");
}

async function handleRequest(
  req: NextRequest,
  params: { path: string[] },
  method: string
) {
  // Step 1: Verify authentication
  const supabase = await createSupabaseServerClient();
  const { data: { user }, error: authError } = await supabase.auth.getUser();

  if (authError || !user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Step 2: Extract supabase project ref from path
  // Expected format: /api/supabase-proxy/{projectRef}/...
  const [projectRef, ...apiPath] = params.path;

  if (!projectRef) {
    return NextResponse.json({ error: "Missing project reference" }, { status: 400 });
  }

  // Step 3: Find OdooOps project_id for this Supabase ref
  const { data: project, error: projectError } = await supabase
    .from("projects")
    .select("project_id")
    .eq("supabase_project_ref", projectRef)
    .single();

  if (projectError || !project) {
    return NextResponse.json({ error: "Project not found" }, { status: 404 });
  }

  // Step 4: Validate user is project member via ops.user_has_permission()
  const { data: hasPermission, error: permError } = await supabase.rpc(
    "user_has_permission",
    {
      p_user_id: user.id,
      p_project_id: project.project_id,
      p_permission: "read", // Minimum permission level
    }
  );

  if (permError || !hasPermission) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  // Step 5: Forward request to Supabase Management API
  const managementApiUrl = `https://api.supabase.com/v1/projects/${projectRef}/${apiPath.join("/")}`;
  const token = process.env.SUPABASE_MANAGEMENT_API_TOKEN;

  if (!token) {
    console.error("SUPABASE_MANAGEMENT_API_TOKEN not configured");
    return NextResponse.json({ error: "Server configuration error" }, { status: 500 });
  }

  const headers: HeadersInit = {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json",
  };

  const options: RequestInit = {
    method,
    headers,
  };

  if (method !== "GET" && method !== "DELETE") {
    const body = await req.json();
    options.body = JSON.stringify(body);
  }

  const response = await fetch(managementApiUrl, options);
  const data = await response.json();

  // Step 6: Audit operation to ops.run_events
  await supabase.from("run_events").insert({
    run_id: `audit-${Date.now()}`,
    level: "info",
    message: `Supabase Management API: ${method} ${apiPath.join("/")}`,
    payload: {
      user_id: user.id,
      project_id: project.project_id,
      supabase_ref: projectRef,
      method,
      path: apiPath.join("/"),
      status: response.status,
    },
  });

  // Step 7: Return response (never expose management token)
  return NextResponse.json(data, { status: response.status });
}

// src/app/api/audit/route.ts
import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { createSupabaseServiceClient } from "@/lib/supabase/service";

function safeJsonParse(input: string | null): any {
  if (!input) return {};
  try {
    return JSON.parse(input);
  } catch {
    return { _parse_error: true, raw: input };
  }
}

export async function POST(req: Request) {
  // 1) Validate user session via SSR client (cookie auth)
  const supabase = createSupabaseServerClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }

  // 2) Read form or JSON payload
  const contentType = req.headers.get("content-type") || "";
  let action = "";
  let org_id: string | null = null;
  let metadata: any = {};
  let target: any = {};

  if (contentType.includes("application/json")) {
    const body = await req.json();
    action = String(body.action || "");
    org_id = body.org_id ? String(body.org_id) : null;
    metadata = body.metadata ?? {};
    target = body.target ?? {};
  } else {
    const form = await req.formData();
    action = String(form.get("action") || "");
    org_id = form.get("org_id") ? String(form.get("org_id")) : null;
    metadata = safeJsonParse(form.get("metadata_json")?.toString() ?? null);
    target = safeJsonParse(form.get("target_json")?.toString() ?? null);
  }

  if (!action) {
    return NextResponse.json({ ok: false, error: "missing action" }, { status: 400 });
  }

  // 3) Optional: verify user is member of org_id if provided
  if (org_id) {
    const { data: member, error: memberErr } = await supabase
      .from("registry.org_members")
      .select("role")
      .eq("org_id", org_id)
      .eq("user_id", user.id)
      .maybeSingle();

    if (memberErr || !member) {
      return NextResponse.json({ ok: false, error: "forbidden (not org member)" }, { status: 403 });
    }
  }

  // 4) Write audit event with service role (server-only)
  const svc = createSupabaseServiceClient();
  const { error: insErr } = await svc.from("audit.events").insert({
    org_id,
    actor_user_id: user.id,
    action,
    target,
    metadata,
  });

  if (insErr) {
    return NextResponse.json({ ok: false, error: insErr.message }, { status: 500 });
  }

  // Redirect back if browser form POST, else JSON response
  if (!contentType.includes("application/json")) {
    return NextResponse.redirect(new URL("/app", req.url), { status: 303 });
  }

  return NextResponse.json({ ok: true });
}

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export const dynamic = "force-dynamic";

function checkInternalToken(req: NextRequest): boolean {
  const expected = process.env.OPS_INTERNAL_TOKEN;
  if (!expected) return false; // Env not configured — deny
  const provided = req.headers.get("x-ops-internal-token");
  return provided === expected;
}

export async function GET(req: NextRequest) {
  if (!checkInternalToken(req)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!supabaseUrl || !serviceKey) {
    return NextResponse.json({ error: "Supabase env not configured" }, { status: 500 });
  }

  const supabase = createClient(supabaseUrl, serviceKey, {
    auth: { persistSession: false },
  });

  const { data, error } = await supabase
    .schema("ops")
    .from("ppm_initiatives")
    .select(
      "initiative_id, name, owner, status, spec_slug, github_label, start_date, target_date, updated_at"
    )
    .order("status", { ascending: true })
    .order("initiative_id", { ascending: true });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ data });
}

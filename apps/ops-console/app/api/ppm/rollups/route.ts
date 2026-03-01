import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export const dynamic = "force-dynamic";

function checkInternalToken(req: NextRequest): boolean {
  const expected = process.env.OPS_INTERNAL_TOKEN;
  if (!expected) return false;
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
    .from("ppm_status_rollups")
    .select(
      "initiative_id, blocking_findings, merged_prs_30d, last_run_at, last_run_status, computed_at"
    )
    .order("computed_at", { ascending: false })
    .limit(500);

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ data });
}

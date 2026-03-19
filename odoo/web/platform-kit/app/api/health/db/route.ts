import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

export const runtime = "nodejs";

export async function GET() {
  const url = process.env.SUPABASE_URL;
  const service = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !service) {
    return NextResponse.json(
      { status: "fail", reason: "missing env" },
      { status: 500 }
    );
  }

  const sb = createClient(url, service, { auth: { persistSession: false } });

  // Lightweight connectivity check - just verify we can reach the database
  const { error } = await sb.from("_health_check_noop").select("1").limit(0);

  // Ignore "relation does not exist" errors - we just want to verify connectivity
  if (error && !error.message.includes("does not exist")) {
    return NextResponse.json(
      { status: "fail", error: String(error.message) },
      { status: 500 }
    );
  }

  return NextResponse.json({ status: "ok", ts: new Date().toISOString() });
}

// app/api/supabase/health/route.ts
// Server-only — SUPABASE_SERVICE_ROLE_KEY never reaches the client.
import { NextRequest, NextResponse } from "next/server"

const SUPABASE_URL =
  process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""

function headers() {
  return {
    apikey:        SERVICE_KEY,
    Authorization: `Bearer ${SERVICE_KEY}`,
    "Content-Type": "application/json",
  }
}

export async function GET(_req: NextRequest) {
  if (!SUPABASE_URL || !SERVICE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  try {
    // 1. Recent function runs (from ops.runs if it exists)
    const [secretsRes, artifactsRes] = await Promise.all([
      // Missing secrets from ops.secret_inventory
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.secret_inventory?status=eq.missing&select=name,severity,last_checked&order=severity.asc&limit=20`,
        { headers: headers(), next: { revalidate: 120 } }
      ),
      // Recent artifact/run entries as proxy for deployed functions
      fetch(
        `${SUPABASE_URL}/rest/v1/ops.runs?select=function_name,status,started_at&order=started_at.desc&limit=20`,
        { headers: headers(), next: { revalidate: 120 } }
      ),
    ])

    const missingSecrets = secretsRes.ok ? await secretsRes.json() : []
    const recentRuns = artifactsRes.ok ? await artifactsRes.json() : []

    return NextResponse.json({
      missingSecrets: Array.isArray(missingSecrets) ? missingSecrets : [],
      recentRuns:     Array.isArray(recentRuns) ? recentRuns : [],
      projectRef:     "spdtwktxdalcfigzeqrz",
      supabaseUrl:    SUPABASE_URL,
    })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}

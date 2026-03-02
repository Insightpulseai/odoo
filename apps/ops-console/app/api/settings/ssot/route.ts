import { NextRequest, NextResponse } from "next/server"

const SUPABASE_URL = process.env.SUPABASE_URL ?? process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ""

function supabaseHeaders(schema = "ops") {
  return {
    apikey: SUPABASE_SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    "Accept-Profile": schema,
  }
}

/**
 * GET /api/settings/ssot
 *
 * Returns the latest settings_snapshot artifact from ops.artifacts.
 * The snapshot is produced by scripts/ci/generate_settings_snapshot.py
 * and inserted by .github/workflows/settings-snapshot.yml on every push to main
 * or change to ssot/**.
 *
 * Shape of snapshot.metadata: SettingsSnapshot (see scripts/ci/generate_settings_snapshot.py)
 */
export async function GET(_req: NextRequest) {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
    return NextResponse.json({ error: "Supabase not configured" }, { status: 503 })
  }

  try {
    const params = new URLSearchParams({
      kind: "eq.settings_snapshot",
      order: "created_at.desc",
      limit: "1",
      select: "id,kind,sha,branch,created_at,metadata",
    })

    const res = await fetch(
      `${SUPABASE_URL}/rest/v1/artifacts?${params}`,
      { headers: supabaseHeaders("ops"), next: { revalidate: 120 } }
    )

    if (!res.ok) {
      const body = await res.text()
      return NextResponse.json({ error: body }, { status: res.status })
    }

    const rows = await res.json()
    if (!rows.length) {
      return NextResponse.json({ snapshot: null, message: "No settings snapshot found. Run CI workflow: settings-snapshot.yml" })
    }

    const row = rows[0]
    return NextResponse.json({
      snapshot: {
        id: row.id,
        sha: row.sha,
        branch: row.branch,
        created_at: row.created_at,
        ...(row.metadata ?? {}),
      },
    })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}

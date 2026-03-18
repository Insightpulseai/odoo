// app/api/vercel/deployments/route.ts
// Server-only — VERCEL_API_TOKEN never reaches the client.
import { NextRequest, NextResponse } from "next/server"

const VERCEL_API_TOKEN = process.env.VERCEL_API_TOKEN ?? ""
const VERCEL_TEAM_SLUG = process.env.VERCEL_TEAM_SLUG ?? "tbwa"
const VERCEL_PROJECT = process.env.VERCEL_PROJECT_NAME ?? "odooops-console"

export async function GET(req: NextRequest) {
  if (!VERCEL_API_TOKEN || VERCEL_API_TOKEN === "YOUR_VERCEL_TOKEN_HERE") {
    return NextResponse.json({ error: "VERCEL_API_TOKEN not configured" }, { status: 503 })
  }

  const { searchParams } = req.nextUrl
  const limit = searchParams.get("limit") ?? "10"

  try {
    const params = new URLSearchParams({
      projectId: VERCEL_PROJECT,
      teamId:    VERCEL_TEAM_SLUG,
      limit,
    })

    const res = await fetch(
      `https://api.vercel.com/v6/deployments?${params.toString()}`,
      {
        headers: { Authorization: `Bearer ${VERCEL_API_TOKEN}` },
        next: { revalidate: 60 },
      }
    )

    if (!res.ok) {
      const text = await res.text()
      return NextResponse.json(
        { error: `Vercel API ${res.status}: ${text.slice(0, 200)}` },
        { status: res.status }
      )
    }

    const data = await res.json()
    // Shape: { deployments: [{ uid, url, state, createdAt, meta: { githubCommitSha, githubCommitMessage } }] }
    const deployments = (data.deployments ?? []).map((d: Record<string, unknown>) => ({
      id:        d.uid,
      url:       d.url,
      state:     d.state,           // READY | ERROR | BUILDING | CANCELED
      createdAt: d.createdAt,
      sha:       (d.meta as Record<string, unknown>)?.githubCommitSha,
      message:   (d.meta as Record<string, unknown>)?.githubCommitMessage,
      errorMessage: (d.errorMessage as string | undefined) ?? null,
    }))

    return NextResponse.json({ deployments })
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 })
  }
}

/**
 * GET /api/auth/vercel
 * Initiates Sign in with Vercel OAuth 2.0 flow.
 * Redirects to Vercel authorization endpoint.
 *
 * Required env vars:
 *   VERCEL_OAUTH_CLIENT_ID — OAuth app client ID
 *   NEXT_PUBLIC_APP_URL    — canonical base URL (e.g. https://ops.insightpulseai.com)
 */

import { NextResponse } from "next/server"

export const runtime = "edge"

export function GET() {
  const clientId = process.env.VERCEL_OAUTH_CLIENT_ID
  const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? ""

  if (!clientId) {
    return new NextResponse("VERCEL_OAUTH_CLIENT_ID not configured", { status: 503 })
  }
  if (!appUrl) {
    return new NextResponse("NEXT_PUBLIC_APP_URL not configured", { status: 503 })
  }

  const redirectUri = `${appUrl}/api/auth/vercel/callback`

  const params = new URLSearchParams({
    client_id:     clientId,
    redirect_uri:  redirectUri,
    scope:         "openid email profile",
    response_type: "code",
  })

  return NextResponse.redirect(
    `https://vercel.com/oauth/authorization?${params.toString()}`
  )
}

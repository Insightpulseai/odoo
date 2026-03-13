/**
 * GET /api/auth/vercel/callback
 * Handles Vercel OAuth 2.0 callback.
 *
 * Flow:
 *   1. Exchange authorization code for access token
 *   2. Fetch user info from Vercel API
 *   3. Create HMAC-signed session cookie
 *   4. Redirect to / (ops console home)
 *
 * Required env vars:
 *   VERCEL_OAUTH_CLIENT_ID     — OAuth app client ID
 *   VERCEL_OAUTH_CLIENT_SECRET — OAuth app client secret
 *   NEXT_PUBLIC_APP_URL        — canonical base URL
 *   SESSION_SECRET             — ≥32-char secret for HMAC signing
 */

import { type NextRequest, NextResponse } from "next/server"
import { createSession, SESSION_COOKIE } from "@/lib/session"

export const runtime = "nodejs"

interface VercelTokenResponse {
  access_token: string
  token_type:   string
  error?:       string
}

interface VercelUser {
  user: {
    id:       string
    name:     string
    email:    string
    avatar?:  string
    username: string
  }
}

export async function GET(req: NextRequest) {
  const { searchParams } = req.nextUrl
  const code  = searchParams.get("code")
  const error = searchParams.get("error")

  const appUrl      = process.env.NEXT_PUBLIC_APP_URL ?? ""
  const clientId    = process.env.VERCEL_OAUTH_CLIENT_ID ?? ""
  const clientSecret = process.env.VERCEL_OAUTH_CLIENT_SECRET ?? ""

  const loginUrl = `${appUrl}/login`

  if (error || !code) {
    return NextResponse.redirect(`${loginUrl}?error=${encodeURIComponent(error ?? "no_code")}`)
  }

  if (!clientId || !clientSecret || !appUrl) {
    return NextResponse.redirect(`${loginUrl}?error=misconfigured`)
  }

  // ── Step 1: Exchange code for access token ──────────────────────────────
  let accessToken: string
  try {
    const tokenRes = await fetch("https://vercel.com/oauth/access_token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code,
        client_id:     clientId,
        client_secret: clientSecret,
        redirect_uri:  `${appUrl}/api/auth/vercel/callback`,
      }),
    })
    const tokenData = (await tokenRes.json()) as VercelTokenResponse
    if (!tokenRes.ok || tokenData.error || !tokenData.access_token) {
      console.error("[auth/vercel/callback] token exchange failed", tokenData)
      return NextResponse.redirect(`${loginUrl}?error=token_exchange`)
    }
    accessToken = tokenData.access_token
  } catch (err) {
    console.error("[auth/vercel/callback] token fetch error", err)
    return NextResponse.redirect(`${loginUrl}?error=token_fetch`)
  }

  // ── Step 2: Fetch user info ─────────────────────────────────────────────
  let vercelUser: VercelUser["user"]
  try {
    const userRes = await fetch("https://api.vercel.com/v2/user", {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    if (!userRes.ok) {
      return NextResponse.redirect(`${loginUrl}?error=user_fetch`)
    }
    const userData = (await userRes.json()) as VercelUser
    vercelUser = userData.user
  } catch (err) {
    console.error("[auth/vercel/callback] user fetch error", err)
    return NextResponse.redirect(`${loginUrl}?error=user_fetch`)
  }

  // ── Step 3: Create session cookie ──────────────────────────────────────
  const sessionToken = createSession({
    sub:     vercelUser.id,
    name:    vercelUser.name || vercelUser.username,
    email:   vercelUser.email,
    picture: vercelUser.avatar,
  })

  const res = NextResponse.redirect(`${appUrl}/`)
  res.cookies.set(SESSION_COOKIE, sessionToken, {
    httpOnly: true,
    secure:   process.env.NODE_ENV === "production",
    sameSite: "lax",
    path:     "/",
    // No explicit maxAge — session expires when browser closes (exp enforced in verifySession)
  })

  return res
}

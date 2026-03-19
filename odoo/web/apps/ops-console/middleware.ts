/**
 * middleware.ts — route protection for ops-console
 *
 * Runs on Edge Runtime. Verifies the HMAC-signed session cookie using
 * Web Crypto API (crypto.subtle). Redirects to /login if missing / invalid.
 *
 * Public paths (no auth required):
 *   /login           — sign-in page
 *   /api/auth/**     — OAuth flow endpoints
 *   /_next/**        — Next.js internals
 *   /favicon.ico
 */

import { type NextRequest, NextResponse } from "next/server"

const SESSION_COOKIE = "ops-session"

function hexToBytes(hex: string): Uint8Array {
  const arr = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    arr[i / 2] = parseInt(hex.slice(i, i + 2), 16)
  }
  return arr
}

function decodeBase64url(str: string): string {
  // base64url → standard base64 → atob
  const b64 = str.replace(/-/g, "+").replace(/_/g, "/")
  const padded = b64 + "=".repeat((4 - (b64.length % 4)) % 4)
  return atob(padded)
}

async function isValidToken(token: string, secret: string): Promise<boolean> {
  const dot = token.lastIndexOf(".")
  if (dot < 0) return false
  const payload = token.slice(0, dot)
  const sig = token.slice(dot + 1)
  try {
    const enc = new TextEncoder()
    const key = await crypto.subtle.importKey(
      "raw",
      enc.encode(secret),
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["verify"],
    )
    const valid = await crypto.subtle.verify("HMAC", key, hexToBytes(sig), enc.encode(payload))
    if (!valid) return false
    const data = JSON.parse(decodeBase64url(payload)) as { exp?: number }
    return typeof data.exp === "number" && data.exp > Math.floor(Date.now() / 1000)
  } catch {
    return false
  }
}

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Always allow auth flow, Next.js internals, and static assets
  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/api/auth/") ||
    pathname.startsWith("/_next/") ||
    pathname === "/favicon.ico"
  ) {
    return NextResponse.next()
  }

  const secret = process.env.SESSION_SECRET ?? ""
  const token = req.cookies.get(SESSION_COOKIE)?.value

  if (!secret || secret.length < 32 || !token) {
    return NextResponse.redirect(new URL("/login", req.url))
  }

  const valid = await isValidToken(token, secret)
  if (!valid) {
    const res = NextResponse.redirect(new URL("/login", req.url))
    res.cookies.delete(SESSION_COOKIE)
    return res
  }

  return NextResponse.next()
}

export const config = {
  // Run on all paths except static file extensions
  matcher: ["/((?!_next/static|_next/image|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff2?|ttf)).*)"],
}

/**
 * POST /api/auth/logout
 * Clears the session cookie and redirects to /login.
 */

import { NextResponse } from "next/server"
import { SESSION_COOKIE } from "@/lib/session"

export const runtime = "edge"

export function POST() {
  const res = NextResponse.redirect(
    new URL("/login", process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000")
  )
  res.cookies.delete(SESSION_COOKIE)
  return res
}

// Allow GET too (for simple href="/api/auth/logout" links)
export function GET() {
  return POST()
}

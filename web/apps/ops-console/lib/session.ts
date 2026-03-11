/**
 * session.ts — lightweight HMAC-signed cookie session
 *
 * No external deps; uses Node.js built-in crypto.
 * Format:  <base64url(payload)>.<hex(hmac-sha256)>
 * Payload: { sub, name, picture, email, exp }
 */

import { createHmac, timingSafeEqual } from "crypto"
import { cookies } from "next/headers"

export const SESSION_COOKIE = "ops-session"
const TTL_SECONDS = 60 * 60 * 8 // 8 hours

export interface SessionUser {
  sub: string
  name: string
  email: string
  picture?: string
  exp: number
}

function secret(): string {
  const s = process.env.SESSION_SECRET
  if (!s || s.length < 32) throw new Error("SESSION_SECRET must be ≥32 chars")
  return s
}

function sign(payload: string): string {
  return createHmac("sha256", secret()).update(payload).digest("hex")
}

export function createSession(user: Omit<SessionUser, "exp">): string {
  const payload = Buffer.from(
    JSON.stringify({ ...user, exp: Math.floor(Date.now() / 1000) + TTL_SECONDS })
  ).toString("base64url")
  return `${payload}.${sign(payload)}`
}

export function verifySession(token: string): SessionUser | null {
  const dot = token.lastIndexOf(".")
  if (dot < 0) return null
  const payload = token.slice(0, dot)
  const sig = token.slice(dot + 1)
  const expected = sign(payload)
  try {
    if (!timingSafeEqual(Buffer.from(sig, "hex"), Buffer.from(expected, "hex"))) return null
  } catch {
    return null
  }
  const user: SessionUser = JSON.parse(Buffer.from(payload, "base64url").toString())
  if (user.exp < Math.floor(Date.now() / 1000)) return null
  return user
}

/** Call from server components / route handlers — reads the current session. */
export async function getSession(): Promise<SessionUser | null> {
  const jar = await cookies()
  const raw = jar.get(SESSION_COOKIE)?.value
  if (!raw) return null
  return verifySession(raw)
}

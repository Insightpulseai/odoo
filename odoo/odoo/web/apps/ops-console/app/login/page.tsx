/**
 * /login — Sign in with Vercel
 *
 * Full-page overlay (fixed, z-50) so it covers the main layout's
 * sidebar and header without needing a separate root layout.
 */

import Link from "next/link"

export const metadata = {
  title: "Sign In | OdooOps",
}

export default function LoginPage({
  searchParams,
}: {
  searchParams: Record<string, string | undefined>
}) {
  const error = searchParams.error

  const ERROR_MESSAGES: Record<string, string> = {
    no_code:        "Authorization was cancelled.",
    token_exchange: "Failed to exchange authorization code. Please try again.",
    token_fetch:    "Could not reach Vercel. Check your network and try again.",
    user_fetch:     "Could not load your Vercel profile. Please try again.",
    misconfigured:  "Auth is not configured. Contact your administrator.",
  }
  const errorMessage = error ? (ERROR_MESSAGES[error] ?? "An unexpected error occurred.") : null

  return (
    /* Full-page overlay over the main layout */
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
      {/* Subtle background grid */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.4) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
      />

      <div className="relative z-10 w-full max-w-sm px-4">
        {/* Card */}
        <div className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-8 shadow-2xl">
          {/* Logo / brand */}
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl border border-white/20 bg-white/10">
              {/* Simple ops icon */}
              <svg
                className="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6.75 7.5l3 2.25-3 2.25m4.5 0h3m-9 8.25h13.5A2.25 2.25 0 0021 18V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v12a2.25 2.25 0 002.25 2.25z"
                />
              </svg>
            </div>
            <h1 className="text-lg font-semibold text-foreground">OdooOps Console</h1>
            <p className="mt-1 text-xs text-muted-foreground">
              Sign in with your Vercel account to continue
            </p>
          </div>

          {/* Error banner */}
          {errorMessage && (
            <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-xs text-red-400">
              {errorMessage}
            </div>
          )}

          {/* Sign in button */}
          <Link
            href="/api/auth/vercel"
            className="flex w-full items-center justify-center gap-2.5 rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-black shadow-sm transition-opacity hover:opacity-90 active:opacity-80"
          >
            {/* Vercel triangle */}
            <svg
              className="h-4 w-4"
              viewBox="0 0 76 65"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M37.5274 0L75.0548 65H0L37.5274 0Z" />
            </svg>
            Continue with Vercel
          </Link>

          <p className="mt-6 text-center text-[11px] text-muted-foreground/60">
            Access is restricted to Insightpulse AI team members.
          </p>
        </div>
      </div>
    </div>
  )
}

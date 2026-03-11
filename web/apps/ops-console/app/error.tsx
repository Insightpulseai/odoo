'use client'

import { useEffect } from 'react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log to an error reporting service if available
    console.error('[ops-console] Unhandled error:', error.digest ?? error.message)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-8 text-center">
      <h2 className="text-xl font-semibold text-destructive">Something went wrong</h2>
      <p className="text-sm text-muted-foreground max-w-md">
        {error.digest ? `Error ID: ${error.digest}` : error.message}
      </p>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        Try again
      </button>
    </div>
  )
}

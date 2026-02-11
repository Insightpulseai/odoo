'use client'

import { useEffect } from 'react'

/**
 * Ensures SSR markup stays stable.
 * Any client-derived flags (localStorage, browser env, or external scripts)
 * are applied AFTER hydration to prevent mismatches.
 */
export default function ClientBodyDataset() {
  useEffect(() => {
    // This runs only after hydration is complete
    // Any body dataset manipulations from external sources (like Supabase Manager iframe)
    // won't cause hydration errors because we're not setting them during render

    // If you need to set specific flags from localStorage, do it here:
    // const body = document.body
    // const debugMode = localStorage.getItem('default_debug_mode') ?? 'disabled'
    // body.dataset.defaultDebugMode = debugMode

  }, [])

  return null
}

// Edge Function Health Check for Secrets
// Verifies presence (not values) of required Edge Secrets

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  // Check required Edge Secrets are present
  const requiredSecrets = [
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'OCR_BASE_URL',
    'OCR_API_KEY',
    'N8N_BASE_URL',
    'SUPERSET_BASE_URL',
    'MCP_BASE_URL',
  ]

  const missing: string[] = []
  const present: string[] = []

  for (const secret of requiredSecrets) {
    if (Deno.env.get(secret)) {
      present.push(secret)
    } else {
      missing.push(secret)
    }
  }

  const ok = missing.length === 0

  return new Response(
    JSON.stringify({
      ok,
      present: present.length,
      missing: missing.length,
      missingSecrets: missing,
      timestamp: new Date().toISOString(),
    }),
    {
      status: ok ? 200 : 500,
      headers: { 'Content-Type': 'application/json' },
    }
  )
})

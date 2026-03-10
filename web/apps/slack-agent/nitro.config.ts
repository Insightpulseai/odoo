// apps/slack-agent/nitro.config.ts
// Nitro server configuration for the IPAI Slack Agent.
//
// Deployment: Vercel (preset: "vercel")
// Port (local dev): 3300
// Endpoints:
//   POST /api/slack/events      — Slack Events API (signature-verified)
//   POST /api/slack/interactive — Slack Interactivity (buttons, modals)
//   POST /api/slack/commands    — Slash commands
//
// Required env vars (registered in ssot/secrets/registry.yaml):
//   SLACK_SIGNING_SECRET  — HMAC verification of every inbound Slack request
//   SLACK_BOT_TOKEN       — xoxb- token for posting messages back to Slack
//   SUPABASE_URL          — Supabase project URL
//   SUPABASE_SERVICE_ROLE_KEY — Service-role key for ops.* writes

import { defineNitroConfig } from 'nitropack/config'

export default defineNitroConfig({
  preset: process.env.NITRO_PRESET ?? 'node-server',

  routeRules: {
    '/api/slack/**': {
      // Slack sends raw application/x-www-form-urlencoded or application/json;
      // disable automatic body parsing so we can read rawBody for HMAC verification.
    },
  },

  runtimeConfig: {
    slackSigningSecret: '',       // injected from NITRO_SLACK_SIGNING_SECRET or env
    slackBotToken: '',            // injected from NITRO_SLACK_BOT_TOKEN or env
    supabaseUrl: '',              // injected from NITRO_SUPABASE_URL or env
    supabaseServiceRoleKey: '',   // injected from NITRO_SUPABASE_SERVICE_ROLE_KEY or env
  },
})

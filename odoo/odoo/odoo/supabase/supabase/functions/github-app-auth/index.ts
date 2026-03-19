// Supabase Edge Function: GitHub App Authentication
// Handles OAuth flow and installation token management for pulser-hub GitHub App

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { SignJWT, importPKCS8 } from 'https://deno.land/x/jose@v4.14.4/index.ts'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// GitHub App configuration
const GITHUB_APP_ID = Deno.env.get('GITHUB_APP_ID') || '2191216'
const GITHUB_CLIENT_ID = Deno.env.get('GITHUB_CLIENT_ID') || 'Iv23liwGL7fnYySPPAjS'
const GITHUB_CLIENT_SECRET = Deno.env.get('GITHUB_CLIENT_SECRET')!
const GITHUB_PRIVATE_KEY = Deno.env.get('GITHUB_PRIVATE_KEY')!
const CALLBACK_URL = Deno.env.get('GITHUB_CALLBACK_URL') || 'https://mcp.insightpulseai.com/callback'

interface InstallationToken {
  token: string
  expires_at: string
  permissions: Record<string, string>
  repository_selection: string
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const url = new URL(req.url)
  const path = url.pathname.split('/').pop()

  try {
    switch (path) {
      case 'authorize':
        return handleAuthorize()

      case 'callback':
        return await handleCallback(req)

      case 'webhook':
        return await handleWebhook(req)

      case 'installation-token':
        return await handleInstallationToken(req)

      case 'jwt':
        return await generateAppJWT()

      case 'repos':
        return await listInstallationRepos(req)

      default:
        return new Response(
          JSON.stringify({ error: 'Unknown endpoint' }),
          { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
    }
  } catch (error) {
    console.error('GitHub App error:', error)
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Step 1: Start OAuth authorization
function handleAuthorize() {
  const state = crypto.randomUUID()
  const authUrl = `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(CALLBACK_URL)}&state=${state}&scope=repo,workflow`

  return new Response(
    JSON.stringify({ auth_url: authUrl, state }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Step 2: Handle OAuth callback
async function handleCallback(req: Request) {
  const url = new URL(req.url)
  const code = url.searchParams.get('code')
  const state = url.searchParams.get('state')

  if (!code) {
    return new Response(
      JSON.stringify({ error: 'Missing authorization code' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  // Exchange code for access token
  const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: CALLBACK_URL
    })
  })

  const tokenData = await tokenResponse.json()

  if (tokenData.error) {
    return new Response(
      JSON.stringify({ error: tokenData.error_description }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  // Get user info
  const userResponse = await fetch('https://api.github.com/user', {
    headers: {
      'Authorization': `Bearer ${tokenData.access_token}`,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  })

  const userData = await userResponse.json()

  // Store in Supabase
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const supabase = createClient(supabaseUrl, supabaseKey)

  await supabase.from('github_oauth_tokens').upsert({
    github_user_id: userData.id.toString(),
    github_username: userData.login,
    access_token: tokenData.access_token, // Should encrypt via Vault!
    token_type: tokenData.token_type,
    scope: tokenData.scope,
    updated_at: new Date().toISOString()
  })

  return new Response(
    JSON.stringify({
      success: true,
      user: {
        id: userData.id,
        login: userData.login,
        name: userData.name,
        avatar_url: userData.avatar_url
      }
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Handle GitHub App webhook events
async function handleWebhook(req: Request) {
  const signature = req.headers.get('x-hub-signature-256')
  const event = req.headers.get('x-github-event')
  const delivery = req.headers.get('x-github-delivery')

  const payload = await req.json()

  // Log webhook event
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const supabase = createClient(supabaseUrl, supabaseKey)

  await supabase.from('github_webhook_events').insert({
    delivery_id: delivery,
    event_type: event,
    action: payload.action,
    repository: payload.repository?.full_name,
    sender: payload.sender?.login,
    payload: payload,
    received_at: new Date().toISOString()
  })

  // Route events to n8n workflows
  const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL') || 'https://n8n.insightpulseai.com'

  switch (event) {
    case 'push':
      await fetch(`${n8nUrl}/webhook/github-push`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      break

    case 'pull_request':
      await fetch(`${n8nUrl}/webhook/github-pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      break

    case 'installation':
    case 'installation_repositories':
      // Handle app installation changes
      await handleInstallationEvent(supabase, payload)
      break
  }

  return new Response(
    JSON.stringify({ success: true, event, delivery }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Generate JWT for GitHub App authentication
async function generateAppJWT(): Promise<Response> {
  const privateKey = await importPKCS8(GITHUB_PRIVATE_KEY, 'RS256')

  const now = Math.floor(Date.now() / 1000)
  const jwt = await new SignJWT({})
    .setProtectedHeader({ alg: 'RS256' })
    .setIssuedAt(now - 60) // 60 seconds in the past for clock drift
    .setExpirationTime(now + 600) // 10 minutes max
    .setIssuer(GITHUB_APP_ID)
    .sign(privateKey)

  return new Response(
    JSON.stringify({ jwt, expires_at: new Date((now + 600) * 1000).toISOString() }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Get installation access token for API calls
async function handleInstallationToken(req: Request): Promise<Response> {
  const body = await req.json()
  const installationId = body.installation_id

  if (!installationId) {
    return new Response(
      JSON.stringify({ error: 'Missing installation_id' }),
      { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  // Generate JWT first
  const privateKey = await importPKCS8(GITHUB_PRIVATE_KEY, 'RS256')
  const now = Math.floor(Date.now() / 1000)
  const jwt = await new SignJWT({})
    .setProtectedHeader({ alg: 'RS256' })
    .setIssuedAt(now - 60)
    .setExpirationTime(now + 600)
    .setIssuer(GITHUB_APP_ID)
    .sign(privateKey)

  // Get installation token
  const response = await fetch(
    `https://api.github.com/app/installations/${installationId}/access_tokens`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      }
    }
  )

  if (!response.ok) {
    const error = await response.json()
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: response.status, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  const tokenData: InstallationToken = await response.json()

  // Cache in Supabase for reuse
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const supabase = createClient(supabaseUrl, supabaseKey)

  await supabase.from('github_installation_tokens').upsert({
    installation_id: installationId.toString(),
    token: tokenData.token, // Should encrypt via Vault!
    expires_at: tokenData.expires_at,
    permissions: tokenData.permissions,
    repository_selection: tokenData.repository_selection,
    updated_at: new Date().toISOString()
  })

  return new Response(
    JSON.stringify({
      success: true,
      token: tokenData.token,
      expires_at: tokenData.expires_at,
      permissions: tokenData.permissions
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// List repositories the app is installed on
async function listInstallationRepos(req: Request): Promise<Response> {
  const body = await req.json()
  const installationId = body.installation_id

  // Get cached token or generate new one
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const supabase = createClient(supabaseUrl, supabaseKey)

  const { data: cached } = await supabase
    .from('github_installation_tokens')
    .select('token, expires_at')
    .eq('installation_id', installationId)
    .single()

  let token: string

  if (cached && new Date(cached.expires_at) > new Date()) {
    token = cached.token
  } else {
    // Generate new token
    const tokenResponse = await handleInstallationToken(req)
    const tokenData = await tokenResponse.json()
    token = tokenData.token
  }

  // List repos
  const response = await fetch(
    'https://api.github.com/installation/repositories',
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
      }
    }
  )

  const data = await response.json()

  return new Response(
    JSON.stringify({
      success: true,
      total_count: data.total_count,
      repositories: data.repositories?.map((r: any) => ({
        id: r.id,
        name: r.name,
        full_name: r.full_name,
        private: r.private,
        default_branch: r.default_branch,
        url: r.html_url
      }))
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Handle installation events
async function handleInstallationEvent(supabase: any, payload: any) {
  const installation = payload.installation

  if (payload.action === 'created' || payload.action === 'new_permissions_accepted') {
    await supabase.from('github_installations').upsert({
      installation_id: installation.id.toString(),
      account_login: installation.account.login,
      account_type: installation.account.type,
      target_type: installation.target_type,
      repository_selection: installation.repository_selection,
      permissions: installation.permissions,
      events: installation.events,
      created_at: installation.created_at,
      updated_at: new Date().toISOString()
    })
  } else if (payload.action === 'deleted') {
    await supabase
      .from('github_installations')
      .delete()
      .eq('installation_id', installation.id.toString())
  }
}

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface RunContext {
  run_id: string
  project_id: string
  env_id: string
  git_sha: string
  git_ref: string
  metadata: Record<string, any>
}

interface BuildPhase {
  name: string
  execute: (ctx: RunContext) => Promise<void>
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Get worker ID from environment or generate
    const workerId = Deno.env.get('WORKER_ID') || `worker-${crypto.randomUUID()}`

    console.log(`[${workerId}] Starting ops-runner...`)

    // Claim next queued run
    const { data: run, error: claimError } = await supabase.rpc('claim_next_run', {
      p_worker_id: workerId
    }).single()

    if (claimError) {
      console.error('Error claiming run:', claimError)
      return new Response(
        JSON.stringify({ error: 'Failed to claim run', details: claimError }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (!run) {
      console.log('No runs available in queue')
      return new Response(
        JSON.stringify({ message: 'No runs in queue' }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`[${workerId}] Claimed run: ${run.run_id}`)

    const runContext: RunContext = {
      run_id: run.run_id,
      project_id: run.project_id,
      env_id: run.env_id,
      git_sha: run.git_sha,
      git_ref: run.git_ref,
      metadata: run.metadata || {}
    }

    // Execute build phases
    const phases: BuildPhase[] = [
      {
        name: 'build_image',
        execute: buildImagePhase
      },
      {
        name: 'deploy_runtime',
        execute: deployRuntimePhase
      },
      {
        name: 'smoke_tests',
        execute: smokeTestsPhase
      },
      {
        name: 'capture_artifacts',
        execute: captureArtifactsPhase
      }
    ]

    let success = true

    for (const phase of phases) {
      try {
        await appendEvent(supabase, runContext.run_id, 'info', `Starting phase: ${phase.name}`)
        await phase.execute(runContext)
        await appendEvent(supabase, runContext.run_id, 'info', `Completed phase: ${phase.name}`)
      } catch (error) {
        success = false
        await appendEvent(
          supabase,
          runContext.run_id,
          'error',
          `Phase ${phase.name} failed: ${error.message}`,
          { error: error.toString(), phase: phase.name }
        )
        console.error(`Phase ${phase.name} failed:`, error)
        break
      }
    }

    // Finish run with final status
    const finalStatus = success ? 'success' : 'failed'
    await supabase.rpc('finish_run', {
      p_run_id: runContext.run_id,
      p_status: finalStatus,
      p_metadata: {
        worker_id: workerId,
        completed_at: new Date().toISOString(),
        phases_completed: phases.filter((_, i) => i < phases.length || success).map(p => p.name)
      }
    })

    console.log(`[${workerId}] Run ${runContext.run_id} finished: ${finalStatus}`)

    return new Response(
      JSON.stringify({
        run_id: runContext.run_id,
        status: finalStatus,
        worker_id: workerId
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Runner error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error', details: error.toString() }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

// Helper function to append events
async function appendEvent(
  supabase: any,
  run_id: string,
  level: string,
  message: string,
  payload: Record<string, any> = {}
) {
  await supabase.rpc('append_event', {
    p_run_id: run_id,
    p_level: level,
    p_message: message,
    p_payload: payload
  })
  console.log(`[${run_id}] ${level.toUpperCase()}: ${message}`)
}

// Build image phase: Create GHCR container image
async function buildImagePhase(ctx: RunContext) {
  console.log(`Building image for ${ctx.git_sha}...`)

  // Simulate image build (in reality, would call GitHub Actions or Docker build)
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Mock image digest
  const imageDigest = `sha256:${crypto.randomUUID().replaceAll('-', '')}`

  ctx.metadata.image_digest = imageDigest
  ctx.metadata.image_tag = `ghcr.io/insightpulseai/odoo:${ctx.git_sha.substring(0, 7)}`

  console.log(`Image built: ${ctx.metadata.image_tag}@${imageDigest}`)
}

// Deploy runtime phase: Deploy container to target environment
async function deployRuntimePhase(ctx: RunContext) {
  console.log(`Deploying to environment ${ctx.env_id}...`)

  // Simulate deployment (in reality, would call DigitalOcean API or Kubernetes)
  await new Promise(resolve => setTimeout(resolve, 3000))

  ctx.metadata.deployment_url = `https://${ctx.env_id}.insightpulseai.com`

  console.log(`Deployed to: ${ctx.metadata.deployment_url}`)
}

// Smoke tests phase: Basic health checks
async function smokeTestsPhase(ctx: RunContext) {
  console.log(`Running smoke tests for ${ctx.metadata.deployment_url}...`)

  // Simulate smoke tests (in reality, would make HTTP requests)
  await new Promise(resolve => setTimeout(resolve, 1000))

  const tests = [
    { name: 'health_check', status: 'pass', duration_ms: 234 },
    { name: 'database_connection', status: 'pass', duration_ms: 156 },
    { name: 'odoo_modules_loaded', status: 'pass', duration_ms: 892 }
  ]

  ctx.metadata.smoke_tests = tests

  console.log(`Smoke tests passed: ${tests.length}/${tests.length}`)
}

// Capture artifacts phase: Store build artifacts
async function captureArtifactsPhase(ctx: RunContext) {
  console.log(`Capturing artifacts for run ${ctx.run_id}...`)

  // In reality, would upload to storage and create artifact records
  const artifacts = [
    {
      artifact_type: 'image',
      storage_path: ctx.metadata.image_tag,
      digest: ctx.metadata.image_digest,
      size_bytes: 1024 * 1024 * 450, // 450 MB
      metadata: { git_sha: ctx.git_sha, git_ref: ctx.git_ref }
    },
    {
      artifact_type: 'logs',
      storage_path: `s3://builds/${ctx.run_id}/build.log`,
      size_bytes: 1024 * 128, // 128 KB
      metadata: { phases: ['build', 'deploy', 'test'] }
    },
    {
      artifact_type: 'evidence',
      storage_path: `s3://builds/${ctx.run_id}/evidence/`,
      size_bytes: 1024 * 64, // 64 KB
      metadata: { smoke_tests: ctx.metadata.smoke_tests }
    }
  ]

  ctx.metadata.artifacts = artifacts

  console.log(`Captured ${artifacts.length} artifacts`)
}

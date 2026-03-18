// Supabase Edge Function: Cron Processor
// Replaces n8n cron triggers with Supabase pg_cron for reliability

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CronJob {
  id: string
  name: string
  schedule: string
  workflow_id: string
  payload: Record<string, unknown>
  enabled: boolean
  last_run: string | null
  next_run: string | null
}

interface JobExecution {
  job_id: string
  status: 'running' | 'success' | 'failed'
  started_at: string
  completed_at?: string
  duration_ms?: number
  error?: string
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const supabaseUrl = Deno.env.get('SUPABASE_URL')!
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  const supabase = createClient(supabaseUrl, supabaseKey)
  const n8nUrl = Deno.env.get('N8N_WEBHOOK_URL') || 'https://n8n.insightpulseai.com'

  try {
    const url = new URL(req.url)
    const path = url.pathname.split('/').pop()

    // Handle different endpoints
    switch (req.method) {
      case 'GET':
        if (path === 'jobs') {
          return await listJobs(supabase)
        }
        if (path === 'status') {
          return await getStatus(supabase)
        }
        break

      case 'POST':
        if (path === 'trigger') {
          // Manual trigger or pg_cron callback
          const body = await req.json()
          return await executeCronJob(supabase, n8nUrl, body.job_name)
        }
        if (path === 'register') {
          const body = await req.json()
          return await registerJob(supabase, body)
        }
        break

      case 'DELETE':
        if (path === 'job') {
          const body = await req.json()
          return await deleteJob(supabase, body.job_id)
        }
        break
    }

    // Default: Run all due jobs (called by pg_cron every minute)
    return await runDueJobs(supabase, n8nUrl)

  } catch (error) {
    console.error('Cron processor error:', error)
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

async function runDueJobs(supabase: any, n8nUrl: string) {
  const now = new Date()

  // Fetch all enabled jobs that are due
  const { data: dueJobs, error } = await supabase
    .from('cron_jobs')
    .select('*')
    .eq('enabled', true)
    .lte('next_run', now.toISOString())
    .order('next_run', { ascending: true })

  if (error) throw error

  const results = []

  for (const job of dueJobs || []) {
    const result = await executeJob(supabase, n8nUrl, job)
    results.push(result)
  }

  return new Response(
    JSON.stringify({
      success: true,
      executed: results.length,
      jobs: results,
      timestamp: now.toISOString()
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function executeJob(supabase: any, n8nUrl: string, job: CronJob) {
  const startTime = Date.now()
  const executionId = crypto.randomUUID()

  // Log execution start
  await supabase.from('cron_executions').insert({
    id: executionId,
    job_id: job.id,
    job_name: job.name,
    status: 'running',
    started_at: new Date().toISOString()
  })

  try {
    // Trigger n8n workflow
    const response = await fetch(`${n8nUrl}/webhook/${job.workflow_id}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Cron-Job': job.name,
        'X-Execution-ID': executionId
      },
      body: JSON.stringify({
        ...job.payload,
        _cron: {
          job_id: job.id,
          job_name: job.name,
          scheduled_time: job.next_run,
          execution_id: executionId
        }
      })
    })

    const duration = Date.now() - startTime

    // Update execution log
    await supabase.from('cron_executions').update({
      status: response.ok ? 'success' : 'failed',
      completed_at: new Date().toISOString(),
      duration_ms: duration,
      response_code: response.status
    }).eq('id', executionId)

    // Calculate next run
    const nextRun = calculateNextRun(job.schedule)

    // Update job with next run time
    await supabase.from('cron_jobs').update({
      last_run: new Date().toISOString(),
      next_run: nextRun.toISOString(),
      last_status: response.ok ? 'success' : 'failed'
    }).eq('id', job.id)

    return {
      job_id: job.id,
      job_name: job.name,
      status: response.ok ? 'success' : 'failed',
      duration_ms: duration,
      next_run: nextRun.toISOString()
    }

  } catch (error) {
    const duration = Date.now() - startTime

    await supabase.from('cron_executions').update({
      status: 'failed',
      completed_at: new Date().toISOString(),
      duration_ms: duration,
      error: error.message
    }).eq('id', executionId)

    return {
      job_id: job.id,
      job_name: job.name,
      status: 'failed',
      error: error.message,
      duration_ms: duration
    }
  }
}

async function executeCronJob(supabase: any, n8nUrl: string, jobName: string) {
  const { data: job, error } = await supabase
    .from('cron_jobs')
    .select('*')
    .eq('name', jobName)
    .single()

  if (error || !job) {
    return new Response(
      JSON.stringify({ success: false, error: 'Job not found' }),
      { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }

  const result = await executeJob(supabase, n8nUrl, job)

  return new Response(
    JSON.stringify({ success: true, ...result }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function registerJob(supabase: any, jobConfig: Partial<CronJob>) {
  const nextRun = calculateNextRun(jobConfig.schedule || '0 8 * * *')

  const { data, error } = await supabase.from('cron_jobs').upsert({
    id: jobConfig.id || crypto.randomUUID(),
    name: jobConfig.name,
    schedule: jobConfig.schedule,
    workflow_id: jobConfig.workflow_id,
    payload: jobConfig.payload || {},
    enabled: jobConfig.enabled ?? true,
    next_run: nextRun.toISOString(),
    created_at: new Date().toISOString()
  }).select().single()

  if (error) throw error

  return new Response(
    JSON.stringify({ success: true, job: data }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function deleteJob(supabase: any, jobId: string) {
  const { error } = await supabase
    .from('cron_jobs')
    .delete()
    .eq('id', jobId)

  if (error) throw error

  return new Response(
    JSON.stringify({ success: true, deleted: jobId }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function listJobs(supabase: any) {
  const { data, error } = await supabase
    .from('cron_jobs')
    .select('*')
    .order('name')

  if (error) throw error

  return new Response(
    JSON.stringify({ success: true, jobs: data }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

async function getStatus(supabase: any) {
  // Get recent executions
  const { data: recentExecutions } = await supabase
    .from('cron_executions')
    .select('*')
    .order('started_at', { ascending: false })
    .limit(20)

  // Get job stats
  const { data: jobStats } = await supabase
    .from('cron_jobs')
    .select('id, name, enabled, last_run, last_status, next_run')

  // Calculate health metrics
  const successCount = recentExecutions?.filter((e: JobExecution) => e.status === 'success').length || 0
  const failedCount = recentExecutions?.filter((e: JobExecution) => e.status === 'failed').length || 0
  const successRate = recentExecutions?.length ? (successCount / recentExecutions.length * 100).toFixed(1) : '0'

  return new Response(
    JSON.stringify({
      success: true,
      health: {
        success_rate: `${successRate}%`,
        recent_success: successCount,
        recent_failed: failedCount,
        total_jobs: jobStats?.length || 0,
        enabled_jobs: jobStats?.filter((j: CronJob) => j.enabled).length || 0
      },
      jobs: jobStats,
      recent_executions: recentExecutions
    }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
  )
}

// Simple cron expression parser (supports standard 5-field cron)
function calculateNextRun(cronExpression: string): Date {
  const [minute, hour, dayOfMonth, month, dayOfWeek] = cronExpression.split(' ')
  const now = new Date()
  const next = new Date(now)

  // Simple implementation: assume daily at specified hour:minute
  const targetHour = hour === '*' ? now.getHours() : parseInt(hour)
  const targetMinute = minute === '*' ? 0 : parseInt(minute)

  next.setHours(targetHour, targetMinute, 0, 0)

  // If the time has passed today, schedule for tomorrow
  if (next <= now) {
    next.setDate(next.getDate() + 1)
  }

  return next
}

#!/usr/bin/env tsx
/**
 * Vercel Environment Variable Sync Script
 * 
 * Syncs environment variables to a Vercel project via REST API.
 * Reads from process.env or a local .env file (not committed).
 * 
 * Usage:
 *   pnpm tsx scripts/vercel/env_sync.ts --project ai-control-plane --env production
 *   pnpm tsx scripts/vercel/env_sync.ts --project ai-control-plane --dry-run
 */

import * as fs from 'fs';
import * as path from 'path';

interface VercelEnvVar {
  key: string;
  value: string;
  type: 'plain' | 'secret' | 'system';
  target: ('production' | 'preview' | 'development')[];
}

const VERCEL_API = 'https://api.vercel.com';
const VERCEL_TOKEN = process.env.VERCEL_TOKEN;

if (!VERCEL_TOKEN) {
  console.error('❌ VERCEL_TOKEN environment variable required');
  process.exit(1);
}

// Required env vars per docs/architecture/VERCEL_CONTROL_PLANE_DEPLOYMENT.md
// and ssot/secrets/registry.yaml
const ENV_VAR_SPEC: Record<string, { type: 'plain' | 'secret'; target: VercelEnvVar['target'] }> = {
  'NEXT_PUBLIC_SUPABASE_URL': { type: 'plain', target: ['production', 'preview', 'development'] },
  'NEXT_PUBLIC_SUPABASE_ANON_KEY': { type: 'plain', target: ['production', 'preview', 'development'] },
  'SUPABASE_SERVICE_ROLE_KEY': { type: 'secret', target: ['production', 'preview'] },
  'SUPABASE_MANAGEMENT_API_TOKEN': { type: 'secret', target: ['production', 'preview'] },
  'GITHUB_TOKEN': { type: 'secret', target: ['production', 'preview'] },
  'ALLOWED_PROJECT_REFS': { type: 'plain', target: ['production', 'preview'] },
  'N8N_WEBHOOK_BACKUP_URL': { type: 'plain', target: ['production', 'preview'] },
  'OPENAI_API_KEY': { type: 'secret', target: ['production', 'preview'] },
  // CRON_SECRET: Vercel injects this as Bearer token on scheduled cron invocations.
  // Required by: apps/ops-console/app/api/cron/tick/route.ts
  //              apps/ops-console/app/api/cron/advisor-nightly/route.ts
  // SSOT: ssot/secrets/registry.yaml → cron_secret
  'CRON_SECRET': { type: 'secret', target: ['production', 'preview'] },
};

async function getVercelProjectId(projectName: string): Promise<string> {
  const response = await fetch(`${VERCEL_API}/v9/projects/${projectName}`, {
    headers: {
      'Authorization': `Bearer ${VERCEL_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch project ${projectName}: ${response.statusText}`);
  }

  const data = await response.json();
  return data.id;
}

async function listVercelEnvVars(projectId: string): Promise<any[]> {
  const response = await fetch(`${VERCEL_API}/v9/projects/${projectId}/env`, {
    headers: {
      'Authorization': `Bearer ${VERCEL_TOKEN}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to list env vars: ${response.statusText}`);
  }

  const data = await response.json();
  return data.envs || [];
}

async function upsertVercelEnvVar(
  projectId: string,
  envVar: VercelEnvVar
): Promise<void> {
  const response = await fetch(`${VERCEL_API}/v10/projects/${projectId}/env`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${VERCEL_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(envVar)
  });

  if (!response.ok) {
    throw new Error(`Failed to upsert ${envVar.key}: ${response.statusText}`);
  }
}

function loadEnvFromProcess(): Record<string, string> {
  const env: Record<string, string> = {};

  for (const key of Object.keys(ENV_VAR_SPEC)) {
    if (process.env[key]) {
      env[key] = process.env[key]!;
    }
  }

  return env;
}

async function syncEnvVars(options: {
  projectName: string;
  environment: 'production' | 'preview' | 'all';
  dryRun: boolean;
}) {
  console.log(`🔄 Syncing environment variables to Vercel project: ${options.projectName}`);
  console.log(`   Environment: ${options.environment}`);
  console.log(`   Dry run: ${options.dryRun}`);

  const projectId = await getVercelProjectId(options.projectName);
  console.log(`✅ Project ID: ${projectId}`);

  const existingVars = await listVercelEnvVars(projectId);
  const existingKeys = new Set(existingVars.map(v => v.key));

  const localEnv = loadEnvFromProcess();
  const missingKeys = Object.keys(ENV_VAR_SPEC).filter(k => !localEnv[k]);

  if (missingKeys.length > 0) {
    console.warn(`⚠️  Missing local env vars: ${missingKeys.join(', ')}`);
  }

  for (const [key, value] of Object.entries(localEnv)) {
    const spec = ENV_VAR_SPEC[key];
    if (!spec) continue;

    const target = options.environment === 'all' 
      ? spec.target 
      : spec.target.filter(t => t === options.environment);

    if (target.length === 0) continue;

    const envVar: VercelEnvVar = {
      key,
      value,
      type: spec.type,
      target
    };

    const action = existingKeys.has(key) ? 'UPDATE' : 'CREATE';

    if (options.dryRun) {
      console.log(`   [DRY RUN] ${action} ${key} (${spec.type}, ${target.join('/')})`);
    } else {
      await upsertVercelEnvVar(projectId, envVar);
      console.log(`   ✅ ${action} ${key}`);
    }
  }

  console.log(`✅ Sync complete`);
}

// CLI parsing
const args = process.argv.slice(2);
const projectIndex = args.indexOf('--project');
const envIndex = args.indexOf('--env');
const dryRunIndex = args.indexOf('--dry-run');

if (projectIndex === -1) {
  console.error('Usage: pnpm tsx scripts/vercel/env_sync.ts --project <name> [--env production|preview|all] [--dry-run]');
  process.exit(1);
}

const projectName = args[projectIndex + 1];
const environment = (envIndex !== -1 ? args[envIndex + 1] : 'production') as 'production' | 'preview' | 'all';
const dryRun = dryRunIndex !== -1;

syncEnvVars({ projectName, environment, dryRun }).catch(err => {
  console.error('❌ Sync failed:', err.message);
  process.exit(1);
});

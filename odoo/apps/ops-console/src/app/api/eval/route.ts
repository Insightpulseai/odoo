import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import path from 'path'

const EVAL_PATH = path.join(process.cwd(), '..', '..', 'artifacts', 'evals', 'odoo_copilot_capability_eval.json')

// Fallback data matching the real eval output
const FALLBACK = {
  overall_score: 0.4174,
  maturity_band: 'scaffolded',
  release_blocked: true,
  domain_scores: {
    tool_execution: 0.75,
    production_readiness: 0.625,
    auth_identity: 0.625,
    knowledge_retrieval: 0.5,
    workflow_orchestration: 0.375,
    context_management: 0.375,
    observability: 0.375,
    error_recovery: 0.25,
    agents: 0.125,
    multi_turn: 0.125,
  },
  blockers: [
    'agent_resolution: current=2 (needs >=3, domain=agents)',
    'multi_turn_success: current=1 (needs >=3, domain=multi_turn)',
    'error_recovery_rate: current=1 (needs >=2, domain=error_recovery)',
  ],
}

export async function GET() {
  try {
    const raw = await readFile(EVAL_PATH, 'utf-8')
    const data = JSON.parse(raw)
    return NextResponse.json({ ...data, source: 'artifact', readAt: new Date().toISOString() })
  } catch {
    return NextResponse.json({ ...FALLBACK, source: 'fallback', readAt: new Date().toISOString() })
  }
}

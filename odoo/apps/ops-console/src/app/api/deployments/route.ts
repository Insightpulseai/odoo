import { NextResponse } from 'next/server'
import { loadModelAliases, loadPolicyCards } from '@/lib/view-models/services'
import { loadAgentCards } from '@/lib/view-models/agents'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const agents = loadAgentCards()
    const modelAliases = loadModelAliases()
    const policies = loadPolicyCards()

    // Build a deployment/promotion view from agent manifests
    const deployments = agents.map(agent => ({
      id: `agent-${agent.id}`,
      name: agent.name,
      version: agent.version,
      environment: agent.promotionState,
      status: agent.promotionState === 'prod' ? 'success' : agent.promotionState === 'staging' ? 'in_progress' : 'pending',
      modelAlias: agent.modelAlias,
      owner: agent.owner,
      sourceFile: agent.sourceFile,
    }))

    return NextResponse.json({
      deployments,
      modelAliases: modelAliases.map(m => ({
        alias: m.alias,
        currentModel: m.currentModel,
        fallback: m.fallback,
        costTier: m.costTier,
        useCases: m.useCases,
      })),
      policies: policies.map(p => ({
        name: p.name,
        kind: p.kind,
        version: p.version,
        sourceFile: p.sourceFile,
      })),
      source: 'registry',
      fetchedAt: new Date().toISOString(),
    })
  } catch (err) {
    console.error('[api/deployments] Registry load failed:', err)
    return NextResponse.json({
      deployments: [],
      modelAliases: [],
      policies: [],
      source: 'error',
      error: String(err),
      fetchedAt: new Date().toISOString(),
    }, { status: 500 })
  }
}

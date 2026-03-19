import { NextResponse } from 'next/server'
import { loadAgentCards, loadToolCards } from '@/lib/view-models/agents'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const agents = loadAgentCards()
    const tools = loadToolCards()

    // Map agents to the format expected by the existing UI
    const toolList = [
      // Include tools from agent manifests (tool bindings)
      ...agents.flatMap(agent =>
        agent.tools.map(toolName => ({
          name: toolName,
          category: categorizeToolName(toolName),
          status: 'operational' as const,
          agentBinding: agent.name,
        }))
      ),
      // Include standalone tool definitions
      ...tools.map(tool => ({
        name: tool.name,
        category: categorizeToolName(tool.name),
        status: 'operational' as const,
        provider: tool.provider,
      })),
    ]

    // Deduplicate by tool name
    const seen = new Set<string>()
    const uniqueTools = toolList.filter(t => {
      if (seen.has(t.name)) return false
      seen.add(t.name)
      return true
    })

    return NextResponse.json({
      agents: agents.map(a => ({
        name: a.name,
        version: a.version,
        owner: a.owner,
        runtime: a.runtime,
        modelAlias: a.modelAlias,
        tools: a.tools,
        promotionState: a.promotionState,
        description: a.description,
        sourceFile: a.sourceFile,
      })),
      tools: uniqueTools,
      source: 'registry',
      fetchedAt: new Date().toISOString(),
    })
  } catch (err) {
    console.error('[api/agents] Registry load failed:', err)
    return NextResponse.json({
      agents: [],
      tools: [],
      source: 'error',
      error: String(err),
      fetchedAt: new Date().toISOString(),
    }, { status: 500 })
  }
}

function categorizeToolName(name: string): string {
  if (name.includes('search') || name.includes('get') || name.includes('read')) return 'read'
  if (name.includes('create') || name.includes('update') || name.includes('write')) return 'write'
  if (name.includes('document') || name.includes('extract') || name.includes('intelligence')) return 'document'
  if (name.includes('slack') || name.includes('email') || name.includes('notify')) return 'notification'
  if (name.includes('odoo')) return 'odoo'
  return 'other'
}

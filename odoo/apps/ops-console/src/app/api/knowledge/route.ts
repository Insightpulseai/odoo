import { NextResponse } from 'next/server'
import { loadOdooBoundaryCards } from '@/lib/view-models/odoo'
import { loadPolicyCards } from '@/lib/view-models/services'

export const dynamic = 'force-dynamic'

const SEARCH_ENDPOINT = process.env.AZURE_SEARCH_ENDPOINT
const SEARCH_KEY = process.env.AZURE_SEARCH_KEY

interface KBStatus {
  name: string
  index: string
  status: 'operational' | 'scaffolded' | 'error'
  chunks: number
  lastRefresh: string | null
}

const KB_INDEXES = [
  { name: 'odoo19-docs', index: 'odoo19-docs' },
  { name: 'azure-platform-docs', index: 'azure-platform-docs' },
  { name: 'databricks-docs', index: 'databricks-docs' },
  { name: 'org-docs', index: 'org-docs' },
]

async function checkIndex(kb: typeof KB_INDEXES[0]): Promise<KBStatus> {
  if (!SEARCH_ENDPOINT || !SEARCH_KEY) {
    return { name: kb.name, index: kb.index, status: 'scaffolded', chunks: 0, lastRefresh: null }
  }

  try {
    const res = await fetch(
      `${SEARCH_ENDPOINT}/indexes/${kb.index}/docs/$count?api-version=2024-07-01`,
      { headers: { 'api-key': SEARCH_KEY }, cache: 'no-store' }
    )
    if (!res.ok) {
      return { name: kb.name, index: kb.index, status: res.status === 404 ? 'scaffolded' : 'error', chunks: 0, lastRefresh: null }
    }
    const count = parseInt(await res.text(), 10)
    return {
      name: kb.name,
      index: kb.index,
      status: count > 0 ? 'operational' : 'scaffolded',
      chunks: count,
      lastRefresh: new Date().toISOString().split('T')[0],
    }
  } catch {
    return { name: kb.name, index: kb.index, status: 'error', chunks: 0, lastRefresh: null }
  }
}

export async function GET() {
  try {
    const [kbResults, boundaryContracts, policies] = await Promise.all([
      Promise.all(KB_INDEXES.map(checkIndex)),
      Promise.resolve(loadOdooBoundaryCards()),
      Promise.resolve(loadPolicyCards()),
    ])

    return NextResponse.json({
      knowledgeBases: kbResults,
      boundaryContracts: boundaryContracts.map(c => ({
        name: c.name,
        kind: c.kind,
        odooModel: c.odooModel,
        description: c.description,
        readOps: c.readOperations.length,
        writeOps: c.writeOperations.length,
        prohibited: c.prohibited.length,
        sourceFile: c.sourceFile,
      })),
      policies: policies.slice(0, 10).map(p => ({
        name: p.name,
        kind: p.kind,
        version: p.version,
        sourceFile: p.sourceFile,
      })),
      source: SEARCH_ENDPOINT ? 'azure-search+registry' : 'registry',
      fetchedAt: new Date().toISOString(),
    })
  } catch (err) {
    console.error('[api/knowledge] Load failed:', err)
    return NextResponse.json({
      knowledgeBases: [],
      boundaryContracts: [],
      policies: [],
      source: 'error',
      error: String(err),
      fetchedAt: new Date().toISOString(),
    }, { status: 500 })
  }
}

import { NextResponse } from 'next/server'

const ODOO_URL = process.env.ODOO_URL || 'https://erp.insightpulseai.com'
const ODOO_API_KEY = process.env.ODOO_API_KEY
const FOUNDRY_ENDPOINT = process.env.AZURE_FOUNDRY_ENDPOINT
const FOUNDRY_KEY = process.env.AZURE_FOUNDRY_API_KEY

// Platform context for local fallback responses
const PLATFORM_CONTEXT: Record<string, string> = {
  status: 'Platform: 6 Azure Container Apps in cae-ipai-dev (southeastasia). Odoo CE 19 on ipai-odoo-dev-web. Agent readiness: 49/100 (scaffolded). 3 release blockers active.',
  blockers: 'Release blockers:\\n1. Auth flow incomplete — Keycloak token exchange not wired\\n2. No structured error recovery — raw tracebacks on tool failure\\n3. KB coverage below 50% — 6/12 Foundry buckets unindexed',
  agents: '14 tools in CopilotToolExecutor: 4 core (read_record, search_records, search_docs, get_report), 3 finance (read_finance_close, view_campaign_perf, view_dashboard), 7 knowledge (search_*_docs, search_org_docs, search_spec_bundles, search_architecture_docs). All read-only Stage 1.',
  services: 'Services behind Azure Front Door (ipai-fd-dev):\\n- Odoo ERP (erp.insightpulseai.com) — Live\\n- Keycloak SSO (auth.insightpulseai.com) — Live\\n- n8n (n8n.insightpulseai.com) — Live\\n- Superset (superset.insightpulseai.com) — Live\\n- MCP (mcp.insightpulseai.com) — Live\\n- OCR (ocr.insightpulseai.com) — Live',
  foundry: 'Foundry SDK: PARTIAL. Done: DefaultAzureCredential, Azure Search SDK, 3 KB tools, API 2025-03-01-preview. Not done: AIProjectClient adoption, live endpoint validation.',
  knowledge: 'KB coverage: 6/12 Foundry buckets. Covered: Agent Runtime, Responses API, Tool Use, Prompt Engineering, SDK, Deployment. Missing: Guardrails, Responsible AI, Security, Observability, Operations, Fine-tuning. Org docs: 8,254 files inventoried.',
  deploy: 'Azure Container Apps: cae-ipai-dev (southeastasia). Front Door: ipai-fd-dev. Supabase: Azure VM vm-ipai-supabase-dev. PostgreSQL: Azure Flexible Server. CI: 355 GitHub Actions workflows.',
}

function localFallback(message: string): string {
  const lower = message.toLowerCase()
  if (lower.includes('status') || lower.includes('overview') || lower.includes('health')) return PLATFORM_CONTEXT.status
  if (lower.includes('blocker') || lower.includes('block') || lower.includes('issue')) return PLATFORM_CONTEXT.blockers
  if (lower.includes('agent') || lower.includes('tool') || lower.includes('copilot')) return PLATFORM_CONTEXT.agents
  if (lower.includes('service') || lower.includes('container')) return PLATFORM_CONTEXT.services
  if (lower.includes('foundry') || lower.includes('sdk')) return PLATFORM_CONTEXT.foundry
  if (lower.includes('knowledge') || lower.includes('kb') || lower.includes('doc')) return PLATFORM_CONTEXT.knowledge
  if (lower.includes('deploy') || lower.includes('ci') || lower.includes('pipeline')) return PLATFORM_CONTEXT.deploy
  return 'I can answer questions about: platform status, release blockers, agent tools, services, Foundry SDK, knowledge bases, and deployments. What would you like to know?'
}

export async function POST(request: Request) {
  const { message, history } = await request.json()

  if (!message || typeof message !== 'string') {
    return NextResponse.json({ error: 'message is required' }, { status: 400 })
  }

  // Try Odoo copilot endpoint first
  if (ODOO_API_KEY) {
    try {
      const res = await fetch(`${ODOO_URL}/copilot/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${ODOO_API_KEY}`,
        },
        body: JSON.stringify({ message, history: history || [] }),
      })
      if (res.ok) {
        const data = await res.json()
        return NextResponse.json({ reply: data.reply || data.response, source: 'odoo-copilot' })
      }
    } catch {
      // Fall through
    }
  }

  // Try Foundry/Azure OpenAI direct
  if (FOUNDRY_ENDPOINT && FOUNDRY_KEY) {
    try {
      const messages = [
        { role: 'system', content: `You are the IPAI Ops Copilot. You have access to this platform context:\n${Object.values(PLATFORM_CONTEXT).join('\n\n')}\n\nAnswer questions about the platform concisely and accurately.` },
        ...(history || []).map((h: any) => ({ role: h.role, content: h.content })),
        { role: 'user', content: message },
      ]
      const res = await fetch(`${FOUNDRY_ENDPOINT}/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-03-01-preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'api-key': FOUNDRY_KEY },
        body: JSON.stringify({ messages, max_tokens: 500, temperature: 0.3 }),
      })
      if (res.ok) {
        const data = await res.json()
        return NextResponse.json({ reply: data.choices?.[0]?.message?.content, source: 'foundry' })
      }
    } catch {
      // Fall through
    }
  }

  // Local fallback
  return NextResponse.json({ reply: localFallback(message), source: 'local' })
}

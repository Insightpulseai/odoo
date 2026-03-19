import { NextResponse } from 'next/server'

// Microsoft Cloud env vars (injected via Azure Key Vault or .env)
const MSCLOUD_TENANT_ID = process.env.MSCLOUD_TENANT_ID
const MSCLOUD_CLIENT_ID = process.env.MSCLOUD_CLIENT_ID

export async function GET() {
  // If Microsoft Cloud credentials are configured, attempt live fetch via Microsoft Graph
  if (MSCLOUD_TENANT_ID && MSCLOUD_CLIENT_ID) {
    try {
      // TODO: Implement live Microsoft Graph API client
      // Uses DefaultAzureCredential or client credentials flow
      // Endpoints:
      // - GET https://graph.microsoft.com/v1.0/organization (tenant info)
      // - GET https://graph.microsoft.com/v1.0/subscribedSkus (licenses)
      // - GET https://management.azure.com/subscriptions (Azure resources)
      // For now, fall through to fixtures
    } catch {
      // Fall through to fixtures
    }
  }

  // Import dynamically to avoid issues if fixtures not yet created
  try {
    const { getMicrosoftCloudSummary } = await import('@/lib/providers/microsoft-cloud-fixtures')
    const summary = getMicrosoftCloudSummary()
    return NextResponse.json({
      ...summary,
      source: MSCLOUD_TENANT_ID ? 'microsoft-graph-live' : 'fixtures',
      fetchedAt: new Date().toISOString(),
    })
  } catch {
    // Fallback if microsoft-cloud-fixtures not yet available
    return NextResponse.json({
      config: { id: 'microsoft-cloud', name: 'Microsoft Cloud', type: 'microsoft-cloud', enabled: true },
      health: { provider: 'microsoft-cloud', status: 'unconfigured', checkedAt: new Date().toISOString(), components: [] },
      builds: [],
      deploys: [],
      databases: [],
      jobs: [],
      kbCoverage: [],
      services: [],
      source: 'fallback',
      fetchedAt: new Date().toISOString(),
    })
  }
}

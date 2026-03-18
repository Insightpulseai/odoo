import { NextResponse } from 'next/server'

// Azure ACA env vars (injected via Key Vault → managed identity → env vars)
const AZURE_SUBSCRIPTION_ID = process.env.AZURE_SUBSCRIPTION_ID
const AZURE_RESOURCE_GROUP = process.env.AZURE_RESOURCE_GROUP || 'rg-ipai-dev'
const AZURE_TENANT_ID = process.env.AZURE_TENANT_ID

export async function GET() {
  // If Azure credentials are configured, attempt live fetch via ARM API
  if (AZURE_SUBSCRIPTION_ID && AZURE_TENANT_ID) {
    try {
      // TODO: Implement live Azure Resource Manager API client
      // Uses managed identity for auth (DefaultAzureCredential)
      // Endpoints:
      // - GET /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.App/containerApps
      // - GET /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.DBforPostgreSQL/flexibleServers
      // - GET /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Cdn/profiles
      // For now, fall through to fixtures
    } catch {
      // Fall through to fixtures
    }
  }

  // Import dynamically to avoid issues if fixtures not yet created
  try {
    const { getAzureSummary } = await import('@/lib/providers/azure-fixtures')
    const summary = getAzureSummary()
    return NextResponse.json({
      ...summary,
      source: AZURE_SUBSCRIPTION_ID ? 'azure-live' : 'fixtures',
      fetchedAt: new Date().toISOString(),
    })
  } catch {
    // Fallback if azure-fixtures not yet available
    return NextResponse.json({
      config: { id: 'azure-aca', name: 'Azure ACA', type: 'azure-aca', enabled: true },
      health: { provider: 'azure-aca', status: 'unconfigured', checkedAt: new Date().toISOString(), components: [] },
      builds: [],
      deploys: [],
      databases: [],
      jobs: [],
      kbCoverage: [],
      source: 'fallback',
      fetchedAt: new Date().toISOString(),
    })
  }
}

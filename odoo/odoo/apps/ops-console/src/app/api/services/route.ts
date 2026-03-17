import { NextResponse } from 'next/server'
import { loadServiceCards } from '@/lib/view-models/services'

export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const serviceCards = loadServiceCards()

    const services = serviceCards.map(svc => ({
      name: svc.name,
      endpoint: svc.instances[0] ?? '',
      status: 'live' as const,  // Registry doesn't have runtime health — mark as live (catalog presence)
      type: svc.serviceClass,
      class: svc.serviceClass,
      resourceGroup: svc.resourceGroup,
      region: svc.region,
      instances: svc.instances,
      consumedBy: svc.consumedBy,
      sourceFile: svc.sourceFile,
    }))

    return NextResponse.json({
      services,
      source: 'registry',
      checkedAt: new Date().toISOString(),
    })
  } catch (err) {
    console.error('[api/services] Registry load failed:', err)
    return NextResponse.json({
      services: [],
      source: 'error',
      error: String(err),
      checkedAt: new Date().toISOString(),
    }, { status: 500 })
  }
}

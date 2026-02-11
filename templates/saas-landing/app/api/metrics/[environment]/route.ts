import { NextResponse } from 'next/server'
import { fetchMetrics } from '@/lib/odoo-api'

export async function GET(
  request: Request,
  { params }: { params: { environment: string } }
) {
  try {
    const metrics = await fetchMetrics(params.environment)
    return NextResponse.json(metrics)
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch metrics' },
      { status: 500 }
    )
  }
}

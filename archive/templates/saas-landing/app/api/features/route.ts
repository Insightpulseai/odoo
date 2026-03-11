import { NextResponse } from 'next/server'
import { fetchPlatformFeatures } from '@/lib/odoo-api'

export async function GET() {
  try {
    const features = await fetchPlatformFeatures()
    return NextResponse.json({ features })
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch features' },
      { status: 500 }
    )
  }
}

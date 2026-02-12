import { NextResponse } from 'next/server'
import { fetchDeployments, triggerDeployment } from '@/lib/odoo-api'

export async function GET() {
  try {
    const deployments = await fetchDeployments()
    return NextResponse.json({ deployments })
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch deployments' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  try {
    const { branch, environment } = await request.json()

    if (!branch || !environment) {
      return NextResponse.json(
        { error: 'Branch and environment are required' },
        { status: 400 }
      )
    }

    const result = await triggerDeployment(branch, environment)
    return NextResponse.json(result)
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Failed to trigger deployment' },
      { status: 500 }
    )
  }
}

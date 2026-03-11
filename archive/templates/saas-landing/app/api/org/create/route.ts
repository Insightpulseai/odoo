import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function POST(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { name, description } = await request.json()

    if (!name || typeof name !== 'string') {
      return NextResponse.json({ error: 'Name is required' }, { status: 400 })
    }

    // For now, org_id = user.id (simple model: user is org owner)
    // Future: separate orgs table with proper relationships
    return NextResponse.json({
      org_id: user.id,
      name,
      description: description || null,
      owner_id: user.id,
      owner_email: user.email
    })
  } catch (error) {
    console.error('Org creation error:', error)
    return NextResponse.json(
      { error: 'Failed to create organization' },
      { status: 500 }
    )
  }
}

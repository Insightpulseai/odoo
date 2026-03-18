import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const org_id = searchParams.get('org_id')

    if (!org_id) {
      return NextResponse.json({ error: 'org_id query parameter is required' }, { status: 400 })
    }

    // Validate user is org admin
    if (user.id !== org_id) {
      return NextResponse.json(
        { error: 'Forbidden: You do not have permission to view invites for this organization' },
        { status: 403 }
      )
    }

    // Query invites (RLS will filter to user's org)
    const { data: invites, error } = await supabase
      .from('registry.org_invites')
      .select('id, email, role, status, expires_at, accepted_at, created_at, updated_at')
      .eq('org_id', org_id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Query error:', error)
      throw error
    }

    return NextResponse.json({ invites: invites || [] })
  } catch (error) {
    console.error('Invite list error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch invites' },
      { status: 500 }
    )
  }
}

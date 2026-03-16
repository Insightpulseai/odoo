import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'

export async function POST(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { invite_id } = await request.json()

    if (!invite_id || typeof invite_id !== 'string') {
      return NextResponse.json({ error: 'invite_id is required' }, { status: 400 })
    }

    // Call RPC to cancel invite
    const { error } = await supabase.rpc('cancel_org_invite', {
      p_invite_id: invite_id
    })

    if (error) {
      console.error('RPC error:', error)

      if (error.message.includes('not found')) {
        return NextResponse.json({ error: 'Invite not found' }, { status: 404 })
      }
      if (error.message.includes('Forbidden')) {
        return NextResponse.json(
          { error: 'Forbidden: You do not have permission to cancel this invite' },
          { status: 403 }
        )
      }

      throw error
    }

    return NextResponse.json({ message: 'Invite cancelled successfully' })
  } catch (error) {
    console.error('Invite cancel error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to cancel invite' },
      { status: 500 }
    )
  }
}

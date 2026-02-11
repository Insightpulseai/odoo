import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'
import { isValidTokenFormat } from '@/lib/auth/invite-token'

export async function POST(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { token } = await request.json()

    if (!token || typeof token !== 'string') {
      return NextResponse.json({ error: 'Token is required' }, { status: 400 })
    }

    if (!isValidTokenFormat(token)) {
      return NextResponse.json({ error: 'Invalid token format' }, { status: 400 })
    }

    // Call RPC to accept invite
    const { data, error } = await supabase.rpc('accept_org_invite', {
      p_token: token,
      p_user_id: user.id
    }).single()

    if (error) {
      console.error('RPC error:', error)

      if (error.message.includes('expired')) {
        return NextResponse.json({ error: 'Invite expired' }, { status: 410 })
      }
      if (error.message.includes('not found') || error.message.includes('Invalid or used')) {
        return NextResponse.json({ error: 'Invalid or already used invite' }, { status: 404 })
      }

      throw error
    }

    return NextResponse.json({
      org_id: data.org_id,
      role: data.role,
      message: 'Invite accepted successfully'
    })
  } catch (error) {
    console.error('Invite accept error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to accept invite' },
      { status: 500 }
    )
  }
}

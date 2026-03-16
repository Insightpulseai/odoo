import { NextRequest, NextResponse } from 'next/server'
import { createServerClient } from '@/lib/supabase/server'
import { sendOrgInviteEmail } from '@/lib/email/zoho'
import { generateInviteToken } from '@/lib/auth/invite-token'

export async function POST(request: NextRequest) {
  try {
    const supabase = createServerClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { org_id, email, role, org_name } = await request.json()

    // Validate inputs
    if (!org_id || !email || !role || !org_name) {
      return NextResponse.json(
        { error: 'Missing required fields: org_id, email, role, org_name' },
        { status: 400 }
      )
    }

    // Validate role
    if (!['admin', 'member', 'viewer'].includes(role)) {
      return NextResponse.json(
        { error: 'Invalid role. Must be: admin, member, or viewer' },
        { status: 400 }
      )
    }

    // Validate user is org admin (user.id === org_id)
    if (user.id !== org_id) {
      return NextResponse.json(
        { error: 'Forbidden: You do not have permission to invite users to this organization' },
        { status: 403 }
      )
    }

    // Generate token
    const token = generateInviteToken()

    // Call RPC to create invite with hashed token
    const { data: invite, error } = await supabase.rpc('create_org_invite_with_token', {
      p_org_id: org_id,
      p_email: email,
      p_role: role,
      p_token: token
    }).single()

    if (error) {
      console.error('RPC error:', error)
      throw new Error(error.message || 'Failed to create invite')
    }

    // Send email
    await sendOrgInviteEmail({
      to: email,
      orgName: org_name,
      role,
      token,
      inviterName: user.email || user.user_metadata?.full_name || 'Team',
      expiresAt: new Date(invite.expires_at)
    })

    return NextResponse.json({
      invite: {
        id: invite.id,
        email: invite.email,
        role: invite.role,
        status: invite.status,
        expires_at: invite.expires_at,
        created_at: invite.created_at
      }
    })
  } catch (error) {
    console.error('Invite send error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to send invite' },
      { status: 500 }
    )
  }
}

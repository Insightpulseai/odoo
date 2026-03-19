import 'server-only'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const { question, spaceId } = await req.json() as {
    question: string
    spaceId?: string
  }

  const supabaseUrl = process.env.SUPABASE_URL
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

  if (!supabaseUrl || !serviceKey) {
    return NextResponse.json(
      { error: 'Supabase service env vars missing' },
      { status: 500 }
    )
  }

  const fnUrl = `${supabaseUrl}/functions/v1/workspace-ask-docs`

  const res = await fetch(fnUrl, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${serviceKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, space_id: spaceId }),
  })

  const data = await res.json() as unknown

  return NextResponse.json(data, { status: res.status })
}

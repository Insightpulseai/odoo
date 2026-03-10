// app/api/runs/[runId]/events/route.ts
// Returns event stream for a specific run (for the Runs UI drill-down).
import 'server-only'

import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function GET(
  _req: Request,
  { params }: { params: { runId: string } },
) {
  const url = process.env.SUPABASE_URL
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY
  if (!url || !key) return NextResponse.json([], { status: 500 })

  const supabase = createClient(url, key)
  const { data } = await supabase
    .schema('ops')
    .from('run_events')
    .select('id, event_type, payload, timestamp')
    .eq('run_id', params.runId)
    .order('timestamp', { ascending: true })

  return NextResponse.json(data ?? [])
}

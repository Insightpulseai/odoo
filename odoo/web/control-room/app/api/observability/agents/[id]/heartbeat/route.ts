import { NextRequest, NextResponse } from 'next/server';
import { sendAgentHeartbeat } from '@/lib/supabase/observability';

/**
 * POST /api/observability/agents/[id]/heartbeat
 * Send a heartbeat for an agent
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const success = await sendAgentHeartbeat(params.id);

    if (!success) {
      return NextResponse.json(
        { error: 'Agent not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ ok: true, message: 'Heartbeat recorded' });
  } catch (error) {
    console.error('Failed to send heartbeat:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to send heartbeat' },
      { status: 500 }
    );
  }
}

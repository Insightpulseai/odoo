import { NextRequest, NextResponse } from 'next/server';
import { listAgents, getAgentStats } from '@/lib/supabase/observability';

/**
 * GET /api/observability/agents
 * List registered agents with their states
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    const filters = {
      status: searchParams.get('status')?.split(',') as any[] || undefined,
      limit: Number(searchParams.get('limit')) || 50,
    };

    const [agents, stats] = await Promise.all([
      listAgents(filters),
      getAgentStats(),
    ]);

    return NextResponse.json({ agents, stats });
  } catch (error) {
    console.error('Failed to list agents:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to list agents' },
      { status: 500 }
    );
  }
}

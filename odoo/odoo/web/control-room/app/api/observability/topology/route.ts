import { NextRequest, NextResponse } from 'next/server';
import { getTopology } from '@/lib/supabase/observability';

/**
 * GET /api/observability/topology
 * Get ecosystem topology (nodes and edges)
 */
export async function GET(request: NextRequest) {
  try {
    const topology = await getTopology();

    return NextResponse.json(topology);
  } catch (error) {
    console.error('Failed to get topology:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to get topology' },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { listServices, getHealthSummary } from '@/lib/supabase/observability';

/**
 * GET /api/observability/health
 * Get aggregated health status for all services
 */
export async function GET(request: NextRequest) {
  try {
    const [services, summary] = await Promise.all([
      listServices(),
      getHealthSummary(),
    ]);

    return NextResponse.json({ services, summary });
  } catch (error) {
    console.error('Failed to get health:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to get health' },
      { status: 500 }
    );
  }
}

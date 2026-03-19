import { NextRequest, NextResponse } from 'next/server';
import { opsQueries } from '@/lib/supabase-ops';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const run = await opsQueries.getRun(params.id);
    return NextResponse.json(run);
  } catch (error) {
    console.error('Failed to fetch run:', error);
    return NextResponse.json({ error: 'Failed to fetch run' }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { opsQueries } from '@/lib/supabase-ops';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const events = await opsQueries.getRunEvents(params.id);
    return NextResponse.json(events);
  } catch (error) {
    console.error('Failed to fetch events:', error);
    return NextResponse.json({ error: 'Failed to fetch events' }, { status: 500 });
  }
}

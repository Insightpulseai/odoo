import { NextResponse } from 'next/server';
import { createServerClient, DatabaseRelation, DatabaseSchema } from '@/lib/supabase';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const includeViews = searchParams.get('includeViews') !== 'false';
    const includeSystem = searchParams.get('includeSystem') === 'true';

    const supabase = createServerClient();

    // Call the list_relations RPC
    const { data, error } = await supabase.rpc('list_relations', {
      include_views: includeViews,
      include_system: includeSystem,
    });

    if (error) {
      console.error('Error fetching relations:', error);
      return NextResponse.json(
        { error: 'Failed to fetch database relations', details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(data as DatabaseRelation[]);
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// GET /api/tables/schemas - List all schemas with exposure status
export async function OPTIONS() {
  return NextResponse.json({ methods: ['GET'] });
}

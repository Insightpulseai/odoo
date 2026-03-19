import { NextResponse } from 'next/server';
import { createServerClient, DatabaseSchema } from '@/lib/supabase';

export async function GET() {
  try {
    const supabase = createServerClient();

    // Call the list_schemas RPC
    const { data, error } = await supabase.rpc('list_schemas');

    if (error) {
      console.error('Error fetching schemas:', error);
      return NextResponse.json(
        { error: 'Failed to fetch schemas', details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(data as DatabaseSchema[]);
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { schema_name, exposed, description } = body;

    if (!schema_name) {
      return NextResponse.json(
        { error: 'schema_name is required' },
        { status: 400 }
      );
    }

    const supabase = createServerClient();

    // Call the toggle_schema_exposure RPC
    const { data, error } = await supabase.rpc('toggle_schema_exposure', {
      p_schema_name: schema_name,
      p_exposed: exposed ?? true,
      p_description: description ?? null,
    });

    if (error) {
      console.error('Error toggling schema exposure:', error);
      return NextResponse.json(
        { error: 'Failed to toggle schema exposure', details: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

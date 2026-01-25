import { NextResponse } from 'next/server';
import { createServerClient, TableColumn } from '@/lib/supabase';

interface RouteParams {
  params: Promise<{
    schema: string;
    table: string;
  }>;
}

export async function GET(request: Request, { params }: RouteParams) {
  try {
    const { schema, table } = await params;
    const { searchParams } = new URL(request.url);
    const includeRows = searchParams.get('includeRows') !== 'false';
    const rowLimit = Math.min(parseInt(searchParams.get('limit') || '100', 10), 1000);

    const supabase = createServerClient();

    // Get columns
    const { data: columns, error: columnsError } = await supabase.rpc('get_table_columns', {
      p_schema_name: schema,
      p_table_name: table,
    });

    if (columnsError) {
      console.error('Error fetching columns:', columnsError);
      return NextResponse.json(
        { error: 'Failed to fetch table columns', details: columnsError.message },
        { status: 500 }
      );
    }

    // Get exact row count
    const { data: rowCount, error: countError } = await supabase.rpc('count_rows', {
      p_schema_name: schema,
      p_relation_name: table,
    });

    if (countError) {
      console.error('Error fetching row count:', countError);
      // Non-fatal, continue with null count
    }

    // Get sample rows if requested
    let rows: unknown[] = [];
    if (includeRows) {
      const { data: sampleRows, error: rowsError } = await supabase.rpc('get_table_sample', {
        p_schema_name: schema,
        p_table_name: table,
        p_limit: rowLimit,
      });

      if (rowsError) {
        console.error('Error fetching sample rows:', rowsError);
        // Non-fatal, continue with empty rows
      } else {
        rows = sampleRows || [];
      }
    }

    return NextResponse.json({
      schema_name: schema,
      table_name: table,
      columns: columns as TableColumn[],
      row_count: rowCount ?? null,
      rows,
    });
  } catch (error) {
    console.error('Unexpected error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

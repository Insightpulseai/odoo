import { NextRequest, NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { kpisQuerySchema } from '@/lib/schemas';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryResult = kpisQuerySchema.safeParse({
      from: searchParams.get('from'),
      to: searchParams.get('to'),
    });

    if (!queryResult.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: queryResult.error.issues },
        { status: 400 }
      );
    }

    const { from, to } = queryResult.data;
    const client = getDatabricksClient();
    const kpis = await client.getKPIs(from, to);

    return NextResponse.json(kpis);
  } catch (error) {
    console.error('Failed to fetch KPIs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch KPIs' },
      { status: 500 }
    );
  }
}

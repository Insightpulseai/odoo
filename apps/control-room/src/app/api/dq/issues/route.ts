import { NextRequest, NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { dqIssuesQuerySchema } from '@/lib/schemas';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryResult = dqIssuesQuerySchema.safeParse({
      severity: searchParams.get('severity'),
      resolved: searchParams.get('resolved'),
      table: searchParams.get('table'),
      limit: searchParams.get('limit'),
    });

    if (!queryResult.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: queryResult.error.issues },
        { status: 400 }
      );
    }

    const client = getDatabricksClient();
    const issues = await client.getDQIssues(queryResult.data);

    return NextResponse.json({ issues });
  } catch (error) {
    console.error('Failed to fetch DQ issues:', error);
    return NextResponse.json(
      { error: 'Failed to fetch DQ issues' },
      { status: 500 }
    );
  }
}

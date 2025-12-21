import { NextRequest, NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { jobRunsQuerySchema } from '@/lib/schemas';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryResult = jobRunsQuerySchema.safeParse({
      jobId: searchParams.get('jobId'),
      limit: searchParams.get('limit'),
    });

    if (!queryResult.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: queryResult.error.issues },
        { status: 400 }
      );
    }

    const { jobId, limit } = queryResult.data;
    const client = getDatabricksClient();
    const runs = await client.getJobRuns(jobId, limit);

    return NextResponse.json({ runs });
  } catch (error) {
    console.error('Failed to fetch job runs:', error);
    return NextResponse.json(
      { error: 'Failed to fetch job runs' },
      { status: 500 }
    );
  }
}

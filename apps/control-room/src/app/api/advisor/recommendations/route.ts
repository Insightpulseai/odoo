import { NextRequest, NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { advisorQuerySchema } from '@/lib/schemas';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryResult = advisorQuerySchema.safeParse({
      category: searchParams.get('category'),
      impact: searchParams.get('impact'),
      dismissed: searchParams.get('dismissed'),
      limit: searchParams.get('limit'),
    });

    if (!queryResult.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: queryResult.error.issues },
        { status: 400 }
      );
    }

    const client = getDatabricksClient();
    const recommendations = await client.getAdvisorRecommendations(queryResult.data);

    return NextResponse.json({ recommendations });
  } catch (error) {
    console.error('Failed to fetch advisor recommendations:', error);
    return NextResponse.json(
      { error: 'Failed to fetch advisor recommendations' },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { projectsQuerySchema } from '@/lib/schemas';
import type { PaginatedResponse, Project } from '@/types/api';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const queryResult = projectsQuerySchema.safeParse({
      status: searchParams.get('status'),
      priority: searchParams.get('priority'),
      programId: searchParams.get('programId'),
      search: searchParams.get('search'),
      page: searchParams.get('page'),
      pageSize: searchParams.get('pageSize'),
    });

    if (!queryResult.success) {
      return NextResponse.json(
        { error: 'Invalid query parameters', details: queryResult.error.issues },
        { status: 400 }
      );
    }

    const { page, pageSize, ...filters } = queryResult.data;
    const client = getDatabricksClient();
    const { data, total } = await client.getProjects({
      ...filters,
      page,
      pageSize,
    });

    const response: PaginatedResponse<Project> = {
      data,
      total,
      page,
      pageSize,
      hasMore: page * pageSize < total,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Failed to fetch projects:', error);
    return NextResponse.json(
      { error: 'Failed to fetch projects' },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { getNotionClient } from '@/lib/notion';
import { createActionRequestSchema } from '@/lib/schemas';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parseResult = createActionRequestSchema.safeParse(body);

    if (!parseResult.success) {
      return NextResponse.json(
        { error: 'Invalid request body', details: parseResult.error.issues },
        { status: 400 }
      );
    }

    const client = getNotionClient();
    const result = await client.createAction(parseResult.data);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Failed to create action' },
        { status: 500 }
      );
    }

    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    console.error('Failed to create Notion action:', error);
    return NextResponse.json(
      { error: 'Failed to create action' },
      { status: 500 }
    );
  }
}

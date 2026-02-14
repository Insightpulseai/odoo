import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const syncQuerySchema = z.object({
  entity_type: z.string(),
  since: z.string().datetime().optional(),
  limit: z.coerce.number().min(1).max(1000).default(100),
});

interface SyncRecord {
  id: string;
  entity_type: string;
  operation: 'create' | 'update' | 'delete';
  data: Record<string, unknown>;
  updated_at: string;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const params = {
      entity_type: searchParams.get('entity_type') || '',
      since: searchParams.get('since'),
      limit: searchParams.get('limit') || '100',
    };

    const parsed = syncQuerySchema.safeParse(params);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { entity_type, since, limit } = parsed.data;

    // TODO: Fetch changes from Supabase since the given timestamp
    // SELECT * FROM {entity_type}
    // WHERE updated_at > {since}
    // ORDER BY updated_at ASC
    // LIMIT {limit}

    // Mock response
    const changes: SyncRecord[] = [];
    const now = new Date().toISOString();

    // In real implementation:
    // 1. Query changes since 'since' timestamp
    // 2. Include creates, updates, and deletes
    // 3. Return cursor for pagination

    return NextResponse.json({
      entity_type,
      changes,
      has_more: false,
      sync_token: btoa(now), // Opaque token for next sync
      server_time: now,
    });
  } catch (error) {
    console.error('Sync delta error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Push changes from client
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const changesSchema = z.object({
      entity_type: z.string(),
      changes: z.array(z.object({
        id: z.string(),
        operation: z.enum(['create', 'update', 'delete']),
        data: z.record(z.unknown()),
        client_timestamp: z.string().datetime(),
      })),
    });

    const parsed = changesSchema.safeParse(body);

    if (!parsed.success) {
      return NextResponse.json(
        { error: 'Invalid request', details: parsed.error.flatten() },
        { status: 400 }
      );
    }

    const { entity_type, changes } = parsed.data;

    // Process each change
    const results = [];
    for (const change of changes) {
      try {
        // TODO: Apply change to Supabase with conflict resolution
        // Check if server version is newer than client_timestamp
        // If conflict, return conflict info

        results.push({
          id: change.id,
          status: 'applied',
          server_id: change.id, // May differ for creates
        });
      } catch (err) {
        results.push({
          id: change.id,
          status: 'error',
          error: err instanceof Error ? err.message : 'Unknown error',
        });
      }
    }

    return NextResponse.json({
      entity_type,
      results,
      server_time: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Sync push error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

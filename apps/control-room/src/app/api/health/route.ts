import { NextResponse } from 'next/server';
import { getDatabricksClient } from '@/lib/databricks';
import { getNotionClient } from '@/lib/notion';
import type { HealthResponse } from '@/types/api';

export async function GET() {
  try {
    const [databricksHealthy, notionHealthy] = await Promise.all([
      getDatabricksClient().checkHealth(),
      getNotionClient().checkHealth(),
    ]);

    const allHealthy = databricksHealthy && notionHealthy;

    const response: HealthResponse = {
      status: allHealthy ? 'healthy' : 'degraded',
      timestamp: new Date().toISOString(),
      services: {
        databricks: databricksHealthy ? 'connected' : 'disconnected',
        notion: notionHealthy ? 'connected' : 'disconnected',
      },
    };

    return NextResponse.json(response, {
      status: allHealthy ? 200 : 503,
    });
  } catch (error) {
    const response: HealthResponse = {
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      services: {
        databricks: 'disconnected',
        notion: 'disconnected',
      },
    };

    return NextResponse.json(response, { status: 503 });
  }
}

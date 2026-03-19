import { NextResponse } from 'next/server';
import type { ServiceHealth } from '@/lib/supabase';

interface ServiceConfig {
  name: string;
  url: string;
  type: 'odoo' | 'superset' | 'n8n' | 'mcp' | 'supabase' | 'custom';
}

// Service endpoints - configure based on environment
const SERVICES: ServiceConfig[] = [
  {
    name: 'odoo-core',
    url: process.env.ODOO_CORE_URL
      ? `${process.env.ODOO_CORE_URL}/web/health`
      : 'http://localhost:8069/web/health',
    type: 'odoo',
  },
  {
    name: 'odoo-marketing',
    url: process.env.ODOO_MARKETING_URL
      ? `${process.env.ODOO_MARKETING_URL}/web/health`
      : 'http://localhost:8070/web/health',
    type: 'odoo',
  },
  {
    name: 'odoo-accounting',
    url: process.env.ODOO_ACCOUNTING_URL
      ? `${process.env.ODOO_ACCOUNTING_URL}/web/health`
      : 'http://localhost:8071/web/health',
    type: 'odoo',
  },
  {
    name: 'superset',
    url: process.env.SUPERSET_URL
      ? `${process.env.SUPERSET_URL}/health`
      : 'http://localhost:8088/health',
    type: 'superset',
  },
  {
    name: 'n8n',
    url: process.env.N8N_URL
      ? `${process.env.N8N_URL}/healthz`
      : 'http://localhost:5678/healthz',
    type: 'n8n',
  },
  {
    name: 'mcp-coordinator',
    url: process.env.MCP_COORDINATOR_URL
      ? `${process.env.MCP_COORDINATOR_URL}/health`
      : 'http://localhost:8766/health',
    type: 'mcp',
  },
  {
    name: 'supabase',
    url: process.env.NEXT_PUBLIC_SUPABASE_URL
      ? `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/`
      : 'http://localhost:54321/rest/v1/',
    type: 'supabase',
  },
];

async function checkServiceHealth(service: ServiceConfig): Promise<ServiceHealth> {
  const start = Date.now();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const headers: Record<string, string> = {};

    // Add auth headers for Supabase
    if (service.type === 'supabase' && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      headers['apikey'] = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    }

    const response = await fetch(service.url, {
      signal: controller.signal,
      headers,
    });

    clearTimeout(timeoutId);

    return {
      name: service.name,
      status: response.ok ? 'healthy' : 'unhealthy',
      responseTime: Date.now() - start,
      statusCode: response.status,
      lastCheck: new Date().toISOString(),
    };
  } catch (error) {
    return {
      name: service.name,
      status: 'unreachable',
      responseTime: Date.now() - start,
      error: error instanceof Error ? error.message : 'Unknown error',
      lastCheck: new Date().toISOString(),
    };
  }
}

export async function GET() {
  try {
    const results = await Promise.all(SERVICES.map(checkServiceHealth));

    const healthyCount = results.filter((r) => r.status === 'healthy').length;
    const totalCount = results.length;

    let overallStatus: 'healthy' | 'degraded' | 'down';
    if (healthyCount === totalCount) {
      overallStatus = 'healthy';
    } else if (healthyCount > 0) {
      overallStatus = 'degraded';
    } else {
      overallStatus = 'down';
    }

    return NextResponse.json({
      status: overallStatus,
      healthy: healthyCount,
      total: totalCount,
      services: results,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Health API error:', error);
    return NextResponse.json(
      {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

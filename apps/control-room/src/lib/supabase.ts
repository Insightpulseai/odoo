import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Server-side client with service role (only use in API routes)
export function createServerClient() {
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!serviceRoleKey) {
    throw new Error('SUPABASE_SERVICE_ROLE_KEY is required for server operations');
  }
  return createClient(supabaseUrl, serviceRoleKey);
}

// Types for MCP Jobs
export interface MCPJob {
  id: string;
  source: string;
  job_type: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  payload: Record<string, unknown>;
  result: Record<string, unknown> | null;
  error: string | null;
  priority: number;
  max_retries: number;
  retry_count: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface MCPJobRun {
  id: string;
  job_id: string;
  run_number: number;
  status: 'started' | 'completed' | 'failed';
  started_at: string;
  completed_at: string | null;
  result: Record<string, unknown> | null;
  error: string | null;
  duration_ms: number | null;
}

export interface MCPJobStats {
  total: number;
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  deadLetter: number;
  avgDurationMs: number;
  successRate: number;
}

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'unreachable' | 'error';
  responseTime: number;
  statusCode?: number;
  error?: string;
  lastCheck: string;
}

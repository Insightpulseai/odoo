import { createClient, SupabaseClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!SUPABASE_URL) {
  throw new Error('Missing SUPABASE_URL environment variable');
}

/**
 * Create a Supabase client with service role key for server-side operations.
 * This client bypasses RLS and has full access to the database.
 */
export function createServerClient(): SupabaseClient {
  if (!SUPABASE_SERVICE_ROLE_KEY) {
    throw new Error('Missing SUPABASE_SERVICE_ROLE_KEY environment variable');
  }
  return createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
}

/**
 * Get a secret from Supabase Vault via the control_plane schema.
 * @param secretName - The logical name of the secret (e.g., 'DIGITALOCEAN_API_TOKEN')
 * @param accessor - Who is accessing the secret (e.g., 'bugbot')
 * @param accessType - Type of access ('read', 'proxy', 'exchange')
 */
export async function getSecret(
  secretName: string,
  accessor: string,
  accessType: 'read' | 'proxy' | 'exchange' = 'read'
): Promise<string | null> {
  const supabase = createServerClient();

  const { data, error } = await supabase.rpc('control_plane_get_secret_logged', {
    p_name: secretName,
    p_accessor: accessor,
    p_access_type: accessType,
  });

  if (error) {
    console.error(`Failed to get secret ${secretName}:`, error);
    return null;
  }

  return data as string | null;
}

/**
 * Check if a bot is allowed to access a specific secret.
 */
export async function botCanAccessSecret(
  botId: string,
  secretName: string
): Promise<boolean> {
  const supabase = createServerClient();

  const { data, error } = await supabase
    .from('control_plane.bot_registry')
    .select('allowed_secrets')
    .eq('bot_id', botId)
    .eq('is_active', true)
    .single();

  if (error || !data) {
    return false;
  }

  return (data.allowed_secrets as string[]).includes(secretName);
}

/**
 * Log bot execution to the control plane.
 */
export async function logBotExecution(params: {
  botId: string;
  executionType: string;
  source?: string;
  requestPayload?: object;
  responsePayload?: object;
  aiModel?: string;
  tokensUsed?: number;
  latencyMs?: number;
  status: 'success' | 'error' | 'timeout';
  errorMessage?: string;
}): Promise<void> {
  const supabase = createServerClient();

  await supabase.from('control_plane.bot_execution_log').insert({
    bot_id: params.botId,
    execution_type: params.executionType,
    source: params.source,
    request_payload: params.requestPayload,
    response_payload: params.responsePayload,
    ai_model: params.aiModel,
    tokens_used: params.tokensUsed,
    latency_ms: params.latencyMs,
    status: params.status,
    error_message: params.errorMessage,
  });
}

/**
 * Update bot heartbeat timestamp.
 */
export async function updateBotHeartbeat(botId: string): Promise<void> {
  const supabase = createServerClient();

  await supabase
    .from('control_plane.bot_registry')
    .update({ last_heartbeat_at: new Date().toISOString() })
    .eq('bot_id', botId);
}

export interface BotExecutionLog {
  id: string;
  bot_id: string;
  execution_type: string;
  source?: string;
  request_payload?: object;
  response_payload?: object;
  ai_model?: string;
  tokens_used?: number;
  latency_ms?: number;
  status: 'success' | 'error' | 'timeout';
  error_message?: string;
  executed_at: string;
}

export interface BotRegistry {
  bot_id: string;
  display_name: string;
  description?: string;
  bot_type: 'sre' | 'deployment' | 'infra' | 'general';
  endpoint_url?: string;
  allowed_secrets: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_heartbeat_at?: string;
}

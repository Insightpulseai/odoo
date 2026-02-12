/**
 * Dataverse Enterprise Console - Policy Decision Audit Log
 * Portfolio Initiative: PORT-2026-012
 * Control: CTRL-POLICY-001 (Real-time Policy Audit)
 *
 * Implements append-only audit trail for all policy decisions
 * Pattern: Immutable log with evidence linkage
 */

import { SupabaseClient } from '@supabase/supabase-js';
import { PolicyDecisionLog } from './types.js';

/**
 * Log policy decision to ops.policy_decisions (append-only)
 */
export async function logPolicyDecision(
  decision: PolicyDecisionLog,
  supabase: SupabaseClient
): Promise<{ success: boolean; id?: string; error?: string }> {
  const { data, error } = await supabase
    .from('policy_decisions')
    .insert({
      bot_id: decision.bot_id,
      request_id: decision.request_id,
      policy_type: decision.policy_type,
      decision: decision.decision,
      reason: decision.reason,
      model_requested: decision.model_requested,
      tool_requested: decision.tool_requested,
      privacy_mode_enabled: decision.privacy_mode_enabled,
      evidence_id: decision.evidence_id,
      evidence_path: decision.evidence_path,
      metadata: decision.metadata || {}
    })
    .select('id')
    .single();

  if (error) {
    console.error('[Audit] Error logging policy decision:', error);
    return { success: false, error: error.message };
  }

  console.log(`[Audit] Logged ${decision.decision} decision for ${decision.policy_type} policy`);
  return { success: true, id: data.id };
}

/**
 * Get recent policy decisions
 * Used by admin console audit viewer
 */
export async function getRecentPolicyDecisions(
  filters: {
    bot_id?: string;
    policy_type?: string;
    decision?: 'allow' | 'block' | 'warn';
    hours?: number;
    limit?: number;
  },
  supabase: SupabaseClient
): Promise<PolicyDecisionLog[]> {
  let query = supabase
    .from('policy_decisions')
    .select('*');

  if (filters.bot_id) {
    query = query.eq('bot_id', filters.bot_id);
  }

  if (filters.policy_type) {
    query = query.eq('policy_type', filters.policy_type);
  }

  if (filters.decision) {
    query = query.eq('decision', filters.decision);
  }

  if (filters.hours) {
    const threshold = new Date(Date.now() - filters.hours * 60 * 60 * 1000);
    query = query.gte('ts', threshold.toISOString());
  }

  query = query.order('ts', { ascending: false });

  if (filters.limit) {
    query = query.limit(filters.limit);
  }

  const { data, error } = await query;

  if (error) {
    console.error('[Audit] Error fetching policy decisions:', error);
    return [];
  }

  return data || [];
}

/**
 * Get policy decision metrics
 * Used by admin console dashboard
 */
export async function getPolicyMetrics(
  hours: number,
  supabase: SupabaseClient
): Promise<{
  total: number;
  allowed: number;
  blocked: number;
  warned: number;
  byPolicyType: Record<string, { allow: number; block: number; warn: number }>;
}> {
  const threshold = new Date(Date.now() - hours * 60 * 60 * 1000);

  const { data, error } = await supabase
    .from('policy_decisions')
    .select('policy_type, decision')
    .gte('ts', threshold.toISOString());

  if (error || !data) {
    console.error('[Audit] Error fetching metrics:', error);
    return {
      total: 0,
      allowed: 0,
      blocked: 0,
      warned: 0,
      byPolicyType: {}
    };
  }

  const metrics = {
    total: data.length,
    allowed: 0,
    blocked: 0,
    warned: 0,
    byPolicyType: {} as Record<string, { allow: number; block: number; warn: number }>
  };

  data.forEach(row => {
    // Overall counts
    if (row.decision === 'allow') metrics.allowed++;
    if (row.decision === 'block') metrics.blocked++;
    if (row.decision === 'warn') metrics.warned++;

    // By policy type
    if (!metrics.byPolicyType[row.policy_type]) {
      metrics.byPolicyType[row.policy_type] = { allow: 0, block: 0, warn: 0 };
    }
    if (row.decision === 'allow') metrics.byPolicyType[row.policy_type].allow++;
    if (row.decision === 'block') metrics.byPolicyType[row.policy_type].block++;
    if (row.decision === 'warn') metrics.byPolicyType[row.policy_type].warn++;
  });

  return metrics;
}

/**
 * Get blocked requests with evidence
 * Used by admin console violations viewer
 */
export async function getBlockedRequests(
  hours: number,
  limit: number,
  supabase: SupabaseClient
): Promise<PolicyDecisionLog[]> {
  const threshold = new Date(Date.now() - hours * 60 * 60 * 1000);

  const { data, error } = await supabase
    .from('policy_decisions')
    .select('*')
    .eq('decision', 'block')
    .gte('ts', threshold.toISOString())
    .order('ts', { ascending: false })
    .limit(limit);

  if (error) {
    console.error('[Audit] Error fetching blocked requests:', error);
    return [];
  }

  return data || [];
}

/**
 * Export policy decisions to CSV
 * Used for compliance reporting
 */
export function exportPolicyDecisionsToCSV(decisions: PolicyDecisionLog[]): string {
  const headers = [
    'Timestamp',
    'Bot ID',
    'Request ID',
    'Policy Type',
    'Decision',
    'Reason',
    'Model Requested',
    'Tool Requested',
    'Privacy Mode',
    'Evidence ID'
  ];

  const rows = decisions.map(d => [
    new Date(d.ts!).toISOString(),
    d.bot_id,
    d.request_id,
    d.policy_type,
    d.decision,
    d.reason,
    d.model_requested || '',
    d.tool_requested || '',
    d.privacy_mode_enabled ? 'true' : 'false',
    d.evidence_id || ''
  ]);

  const csv = [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n');

  return csv;
}

/**
 * Stream policy decisions in real-time
 * Used by admin console audit viewer (Supabase Realtime)
 */
export function subscribeToPolicyDecisions(
  callback: (decision: PolicyDecisionLog) => void,
  filters: {
    bot_id?: string;
    policy_type?: string;
    decision?: string;
  },
  supabase: SupabaseClient
): { unsubscribe: () => void } {
  let channel = supabase
    .channel('policy_decisions_stream')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'ops',
        table: 'policy_decisions'
      },
      payload => {
        const decision = payload.new as PolicyDecisionLog;

        // Apply filters
        if (filters.bot_id && decision.bot_id !== filters.bot_id) return;
        if (filters.policy_type && decision.policy_type !== filters.policy_type) return;
        if (filters.decision && decision.decision !== filters.decision) return;

        callback(decision);
      }
    )
    .subscribe();

  return {
    unsubscribe: () => {
      supabase.removeChannel(channel);
    }
  };
}

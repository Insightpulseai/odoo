/**
 * Dataverse Enterprise Console - Model Governance
 * Portfolio Initiative: PORT-2026-012
 * Control: CTRL-MODEL-001 (Model Governance)
 *
 * Implements Cursor Enterprise model governance:
 * - Allowlist/blocklist enforcement
 * - Per-org policy configuration
 * - Evidence-linked blocking
 */

import { SupabaseClient } from '@supabase/supabase-js';
import {
  PolicyContext,
  PolicyDecision,
  EnforcementRequest,
  ModelPolicy
} from './types.js';
import { generateEvidenceId, generateEvidencePath } from './enforcement.js';

/**
 * Check if model is allowed for organization
 * Logic: Blocked if explicit block policy, otherwise allowed
 */
export async function checkModelPolicy(
  requestData: EnforcementRequest,
  context: PolicyContext,
  supabase: SupabaseClient
): Promise<PolicyDecision> {
  const model = requestData.model;
  if (!model) {
    return {
      allowed: true,
      reason: 'No model specified'
    };
  }

  // Check for explicit block policy
  const { data: blockPolicy, error: blockError } = await supabase
    .from('model_policy')
    .select('*')
    .eq('org_id', context.org_id)
    .eq('model_name', model)
    .eq('policy_type', 'block')
    .single();

  if (blockError && blockError.code !== 'PGRST116') { // PGRST116 = no rows
    console.error('[ModelPolicy] Error fetching block policy:', blockError);
  }

  if (blockPolicy) {
    const evidenceId = generateEvidenceId('model', 'block');
    const evidencePath = generateEvidencePath('model-governance');

    return {
      allowed: false,
      reason: `Model ${model} blocked by org policy: ${blockPolicy.reason || 'No reason provided'}`,
      evidence_id: evidenceId,
      metadata: {
        model_family: blockPolicy.model_family,
        policy_reason: blockPolicy.reason,
        evidence_path: evidencePath
      }
    };
  }

  // Check for explicit allow policy (optional - absence means allowed)
  const { data: allowPolicy } = await supabase
    .from('model_policy')
    .select('*')
    .eq('org_id', context.org_id)
    .eq('model_name', model)
    .eq('policy_type', 'allow')
    .single();

  if (allowPolicy) {
    return {
      allowed: true,
      reason: `Model ${model} explicitly allowed: ${allowPolicy.reason || 'Production-approved'}`,
      metadata: {
        model_family: allowPolicy.model_family,
        policy_reason: allowPolicy.reason
      }
    };
  }

  // No explicit policy = allowed by default (permissive)
  return {
    allowed: true,
    reason: `Model ${model} allowed (no blocking policy)`,
    metadata: {
      note: 'No explicit policy - default allow'
    }
  };
}

/**
 * Get all model policies for an organization
 * Used by admin console
 */
export async function getOrgModelPolicies(
  orgId: string,
  supabase: SupabaseClient
): Promise<ModelPolicy[]> {
  const { data, error } = await supabase
    .from('model_policy')
    .select('*')
    .eq('org_id', orgId)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('[ModelPolicy] Error fetching policies:', error);
    return [];
  }

  return data || [];
}

/**
 * Create or update model policy
 * Used by admin console
 */
export async function setModelPolicy(
  orgId: string,
  modelFamily: string,
  modelName: string,
  policyType: 'allow' | 'block',
  reason: string,
  supabase: SupabaseClient
): Promise<{ success: boolean; error?: string }> {
  const { error } = await supabase
    .from('model_policy')
    .upsert({
      org_id: orgId,
      model_family: modelFamily,
      model_name: modelName,
      policy_type: policyType,
      reason: reason,
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'org_id,model_name'
    });

  if (error) {
    console.error('[ModelPolicy] Error setting policy:', error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

/**
 * Delete model policy
 * Used by admin console
 */
export async function deleteModelPolicy(
  orgId: string,
  modelName: string,
  supabase: SupabaseClient
): Promise<{ success: boolean; error?: string }> {
  const { error } = await supabase
    .from('model_policy')
    .delete()
    .eq('org_id', orgId)
    .eq('model_name', modelName);

  if (error) {
    console.error('[ModelPolicy] Error deleting policy:', error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

/**
 * Get model usage statistics
 * Used by admin console analytics
 */
export async function getModelUsageStats(
  orgId: string,
  timeRangeHours: number,
  supabase: SupabaseClient
): Promise<Record<string, number>> {
  const { data, error } = await supabase
    .from('policy_decisions')
    .select('model_requested')
    .gte('ts', new Date(Date.now() - timeRangeHours * 60 * 60 * 1000).toISOString())
    .not('model_requested', 'is', null);

  if (error) {
    console.error('[ModelPolicy] Error fetching usage stats:', error);
    return {};
  }

  // Count occurrences
  const stats: Record<string, number> = {};
  data?.forEach(row => {
    const model = row.model_requested;
    stats[model] = (stats[model] || 0) + 1;
  });

  return stats;
}

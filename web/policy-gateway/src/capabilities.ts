/**
 * Dataverse Enterprise Console - Capability Validation
 * Portfolio Initiative: PORT-2026-012
 * Control: CTRL-CAPABILITY-001 (Capability Attestation Requirement)
 *
 * Implements Cursor's attestation-based access control:
 * - Bots must prove they have capabilities before tool access
 * - Code evidence required
 * - Test suite validation
 * - Expiry-based attestations
 */

import { SupabaseClient } from '@supabase/supabase-js';
import {
  PolicyContext,
  PolicyDecision,
  EnforcementRequest,
  CapabilityAttestation
} from './types.js';
import { generateEvidenceId, generateEvidencePath } from './enforcement.js';

/**
 * Check if bot has attested capabilities for requested tool
 * Logic:
 * 1. Get required capabilities for tool (from gold.capability_map)
 * 2. Check bot's capability attestations
 * 3. Verify non-expired
 * 4. Block if missing or expired
 */
export async function checkCapabilityAttestation(
  requestData: EnforcementRequest,
  context: PolicyContext,
  supabase: SupabaseClient
): Promise<PolicyDecision> {
  const toolName = requestData.tool_name;
  if (!toolName) {
    return {
      allowed: true,
      reason: 'No tool specified'
    };
  }

  // Get required capabilities for tool
  // Note: This assumes gold.capability_map has a required_for_tools column (added in Phase 3)
  const { data: capabilityMap, error: capError } = await supabase
    .from('capability_map')
    .select('capability_key, required_for_tools')
    .contains('required_for_tools', [toolName]);

  if (capError) {
    console.error('[Capability] Error fetching capability map:', capError);
    // Fail-safe: if can't check requirements, allow (audit mode)
    return {
      allowed: true,
      reason: `Capability check skipped (map fetch error): ${capError.message}`,
      metadata: { warning: 'Capability validation failed - allowed by default' }
    };
  }

  if (!capabilityMap || capabilityMap.length === 0) {
    // No capability requirements for this tool
    return {
      allowed: true,
      reason: `No capability requirements for tool: ${toolName}`
    };
  }

  const requiredCapabilities = capabilityMap.map(c => c.capability_key);

  // Check bot's attestations
  const { data: attestations, error: attestError } = await supabase
    .from('capability_attestations')
    .select('*')
    .eq('bot_id', context.bot_id)
    .in('capability_key', requiredCapabilities);

  if (attestError) {
    console.error('[Capability] Error fetching attestations:', attestError);
    return {
      allowed: true,
      reason: `Capability check skipped (attestation fetch error): ${attestError.message}`,
      metadata: { warning: 'Attestation validation failed - allowed by default' }
    };
  }

  // Filter attested and non-expired capabilities
  const now = new Date();
  const attested = attestations
    ?.filter(a =>
      a.has_capability &&
      (!a.expiry_date || new Date(a.expiry_date) > now)
    )
    .map(a => a.capability_key) || [];

  const missing = requiredCapabilities.filter(cap => !attested.includes(cap));

  if (missing.length > 0) {
    const evidenceId = generateEvidenceId('capability', 'missing');
    const evidencePath = generateEvidencePath('capability-validation');

    return {
      allowed: false,
      reason: `Bot lacks required capabilities: ${missing.join(', ')}`,
      evidence_id: evidenceId,
      metadata: {
        missing_capabilities: missing,
        required_capabilities: requiredCapabilities,
        attested_capabilities: attested,
        attestation_status: attestations,
        evidence_path: evidencePath,
        remediation: 'Attest capabilities via ops.capability_attestations or provide code evidence'
      }
    };
  }

  // All required capabilities attested
  return {
    allowed: true,
    reason: `All required capabilities attested: ${attested.join(', ')}`,
    metadata: {
      required_capabilities: requiredCapabilities,
      attested_capabilities: attested
    }
  };
}

/**
 * Get bot capability attestations
 * Used by admin console
 */
export async function getBotCapabilities(
  botId: string,
  supabase: SupabaseClient
): Promise<CapabilityAttestation[]> {
  const { data, error } = await supabase
    .from('capability_attestations')
    .select('*')
    .eq('bot_id', botId)
    .order('last_validated_at', { ascending: false });

  if (error) {
    console.error('[Capability] Error fetching bot capabilities:', error);
    return [];
  }

  return data || [];
}

/**
 * Attest bot capability
 * Used by admin console or CI validation
 */
export async function attestCapability(
  botId: string,
  capabilityKey: string,
  hasCapability: boolean,
  attestationMethod: 'code_scan' | 'manual_verification' | 'test_suite' | 'runtime_validation',
  attestationEvidence: string,
  validatorId: string,
  expiryDays?: number,
  supabase: SupabaseClient
): Promise<{ success: boolean; error?: string }> {
  const expiryDate = expiryDays
    ? new Date(Date.now() + expiryDays * 24 * 60 * 60 * 1000).toISOString()
    : null;

  const { error } = await supabase
    .from('capability_attestations')
    .upsert({
      bot_id: botId,
      capability_key: capabilityKey,
      has_capability: hasCapability,
      attestation_method: attestationMethod,
      attestation_evidence: attestationEvidence,
      last_validated_at: new Date().toISOString(),
      validator_id: validatorId,
      expiry_date: expiryDate,
      updated_at: new Date().toISOString()
    }, {
      onConflict: 'bot_id,capability_key'
    });

  if (error) {
    console.error('[Capability] Error attesting capability:', error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

/**
 * Revoke capability attestation
 * Used by admin console
 */
export async function revokeCapability(
  botId: string,
  capabilityKey: string,
  supabase: SupabaseClient
): Promise<{ success: boolean; error?: string }> {
  const { error } = await supabase
    .from('capability_attestations')
    .update({
      has_capability: false,
      updated_at: new Date().toISOString()
    })
    .eq('bot_id', botId)
    .eq('capability_key', capabilityKey);

  if (error) {
    console.error('[Capability] Error revoking capability:', error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

/**
 * Get capability status summary for bot
 * Used by admin console dashboard
 */
export async function getCapabilityStatusSummary(
  botId: string,
  supabase: SupabaseClient
): Promise<{
  total: number;
  attested: number;
  expired: number;
  missing: number;
}> {
  const { data: attestations } = await supabase
    .from('capability_attestations')
    .select('*')
    .eq('bot_id', botId);

  if (!attestations || attestations.length === 0) {
    return { total: 0, attested: 0, expired: 0, missing: 0 };
  }

  const now = new Date();
  const attested = attestations.filter(a =>
    a.has_capability &&
    (!a.expiry_date || new Date(a.expiry_date) > now)
  ).length;
  const expired = attestations.filter(a =>
    a.expiry_date && new Date(a.expiry_date) <= now
  ).length;
  const missing = attestations.filter(a => !a.has_capability).length;

  return {
    total: attestations.length,
    attested,
    expired,
    missing
  };
}

/**
 * Check if capabilities are expiring soon (within N days)
 * Used for proactive alerts
 */
export async function getExpiringCapabilities(
  botId: string,
  daysThreshold: number,
  supabase: SupabaseClient
): Promise<CapabilityAttestation[]> {
  const thresholdDate = new Date(Date.now() + daysThreshold * 24 * 60 * 60 * 1000);

  const { data, error } = await supabase
    .from('capability_attestations')
    .select('*')
    .eq('bot_id', botId)
    .eq('has_capability', true)
    .not('expiry_date', 'is', null)
    .lte('expiry_date', thresholdDate.toISOString());

  if (error) {
    console.error('[Capability] Error fetching expiring capabilities:', error);
    return [];
  }

  return data || [];
}

/**
 * Dataverse Enterprise Console - Policy Enforcement Engine
 * Portfolio Initiative: PORT-2026-012
 * Control: CTRL-POLICY-001 (Policy Gateway Enforcement)
 *
 * Core enforcement logic that replicates Cursor Enterprise patterns:
 * 1. Privacy Mode (x-ghost-mode equivalent)
 * 2. Model Governance (allowlist/blocklist)
 * 3. Capability Validation (attestation-based)
 * 4. Real-time Audit (append-only log)
 */

import { SupabaseClient } from '@supabase/supabase-js';
import { v4 as uuidv4 } from 'uuid';
import {
  PolicyContext,
  PolicyDecision,
  EnforcementRequest,
  PolicyDecisionLog
} from './types.js';
import { checkPrivacyMode } from './privacy.js';
import { checkModelPolicy } from './models.js';
import { checkCapabilityAttestation } from './capabilities.js';
import { logPolicyDecision } from './audit.js';

/**
 * Main enforcement orchestrator
 * Runs all policy checks in sequence, fails fast on violations
 */
export async function enforcePolicies(
  requestData: EnforcementRequest,
  context: PolicyContext,
  supabase: SupabaseClient
): Promise<PolicyDecision> {
  console.log(`[PolicyGateway] Enforcing policies for request ${context.request_id}`);

  // 1. Privacy Mode Check (always first - determines routing)
  const privacyDecision = await checkPrivacyMode(requestData, context, supabase);
  if (!privacyDecision.allowed) {
    await logPolicyDecision({
      bot_id: context.bot_id,
      request_id: context.request_id,
      policy_type: 'privacy',
      decision: 'block',
      reason: privacyDecision.reason,
      privacy_mode_enabled: requestData.headers?.['x-privacy-mode'] !== 'false',
      evidence_id: privacyDecision.evidence_id,
      metadata: privacyDecision.metadata
    }, supabase);
    return privacyDecision;
  }

  // 2. Model Policy Check (if model specified)
  if (requestData.model) {
    const modelDecision = await checkModelPolicy(requestData, context, supabase);
    if (!modelDecision.allowed) {
      await logPolicyDecision({
        bot_id: context.bot_id,
        request_id: context.request_id,
        policy_type: 'model',
        decision: 'block',
        reason: modelDecision.reason,
        model_requested: requestData.model,
        privacy_mode_enabled: requestData.headers?.['x-privacy-mode'] !== 'false',
        evidence_id: modelDecision.evidence_id,
        metadata: modelDecision.metadata
      }, supabase);
      return modelDecision;
    }
  }

  // 3. Capability Validation (if tool specified)
  if (requestData.tool_name) {
    const capabilityDecision = await checkCapabilityAttestation(requestData, context, supabase);
    if (!capabilityDecision.allowed) {
      await logPolicyDecision({
        bot_id: context.bot_id,
        request_id: context.request_id,
        policy_type: 'capability',
        decision: 'block',
        reason: capabilityDecision.reason,
        tool_requested: requestData.tool_name,
        privacy_mode_enabled: requestData.headers?.['x-privacy-mode'] !== 'false',
        evidence_id: capabilityDecision.evidence_id,
        metadata: capabilityDecision.metadata
      }, supabase);
      return capabilityDecision;
    }
  }

  // All policies passed - log success and return
  const finalDecision: PolicyDecision = {
    allowed: true,
    reason: 'All policy checks passed',
    route_to: privacyDecision.route_to, // Preserve privacy routing
    metadata: {
      privacy_mode: privacyDecision.metadata?.privacy_enabled,
      model_approved: !!requestData.model,
      capability_verified: !!requestData.tool_name
    }
  };

  await logPolicyDecision({
    bot_id: context.bot_id,
    request_id: context.request_id,
    policy_type: 'composite',
    decision: 'allow',
    reason: finalDecision.reason,
    model_requested: requestData.model,
    tool_requested: requestData.tool_name,
    privacy_mode_enabled: requestData.headers?.['x-privacy-mode'] !== 'false',
    metadata: finalDecision.metadata
  }, supabase);

  return finalDecision;
}

/**
 * Generate evidence ID for blocked requests
 * Format: EVID-YYYYMMDD-<POLICY_TYPE>-<ACTION>
 */
export function generateEvidenceId(policyType: string, action: string): string {
  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const suffix = `${policyType.toUpperCase()}-${action.toUpperCase()}`;
  return `EVID-${timestamp}-${suffix}`;
}

/**
 * Create evidence artifact path
 * Pattern: docs/evidence/<YYYYMMDD-HHMM>/policy-violations/<policy_type>/
 */
export function generateEvidencePath(policyType: string): string {
  const now = new Date();
  const timestamp = now.toISOString().slice(0, 16).replace(/[-:]/g, '').replace('T', '-');
  return `docs/evidence/${timestamp}/policy-violations/${policyType}/`;
}

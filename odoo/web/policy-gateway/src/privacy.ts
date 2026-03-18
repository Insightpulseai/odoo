/**
 * Dataverse Enterprise Console - Privacy Mode Routing
 * Portfolio Initiative: PORT-2026-012
 * Control: CTRL-POLICY-001 (Privacy Enforcement)
 *
 * Implements Cursor's x-ghost-mode pattern:
 * - Privacy-by-default (missing header = privacy ON)
 * - Dual service routing (privacy replica vs standard)
 * - No plaintext code storage in privacy mode
 */

import { SupabaseClient } from '@supabase/supabase-js';
import {
  PolicyContext,
  PolicyDecision,
  EnforcementRequest,
  PrivacyConfig
} from './types.js';
import { generateEvidenceId } from './enforcement.js';

/**
 * Check privacy mode and determine routing
 * Default-safe: if header missing or config says privacy-enabled, route to privacy replica
 */
export async function checkPrivacyMode(
  requestData: EnforcementRequest,
  context: PolicyContext,
  supabase: SupabaseClient
): Promise<PolicyDecision> {
  const privacyHeader = requestData.headers?.['x-privacy-mode'];

  // Get org privacy config
  const { data: config, error } = await supabase
    .from('privacy_mode_config')
    .select('*')
    .eq('org_id', context.org_id)
    .single();

  if (error && error.code !== 'PGRST116') { // PGRST116 = no rows
    console.error('[Privacy] Error fetching config:', error);
    // Fail-safe: if can't get config, assume privacy mode
    return {
      allowed: true,
      reason: 'Privacy mode enforced (config fetch failed, fail-safe)',
      route_to: 'privacy_safe_replica',
      metadata: { privacy_enabled: true, config_error: error.message }
    };
  }

  // Default-safe logic (Cursor pattern)
  const defaultPrivacyEnabled = config?.default_privacy_enabled ?? true;
  const explicitPrivacyOff = privacyHeader === 'false';

  // Privacy mode is ON if:
  // 1. No explicit "false" header AND config says default privacy, OR
  // 2. Explicit "true" header
  const privacyEnabled = (!explicitPrivacyOff && defaultPrivacyEnabled) || privacyHeader === 'true';

  if (privacyEnabled) {
    // Check if enforcement level allows this
    if (config?.enforcement_level === 'strict') {
      return {
        allowed: true,
        reason: 'Privacy mode enforced (default-safe)',
        route_to: config?.privacy_replica_endpoint || 'privacy_safe_replica',
        metadata: {
          privacy_enabled: true,
          header_value: privacyHeader,
          config_default: defaultPrivacyEnabled,
          enforcement: 'strict'
        }
      };
    } else if (config?.enforcement_level === 'warn') {
      console.warn('[Privacy] Privacy mode recommended but enforcement=warn');
      return {
        allowed: true,
        reason: 'Privacy mode recommended (warn only)',
        route_to: 'standard_replica', // Don't block, just warn
        metadata: {
          privacy_enabled: false,
          warning: 'Privacy mode recommended for this org',
          enforcement: 'warn'
        }
      };
    } else { // audit
      console.info('[Privacy] Privacy mode detected but enforcement=audit');
      return {
        allowed: true,
        reason: 'Privacy mode detected (audit only)',
        route_to: 'standard_replica',
        metadata: {
          privacy_enabled: false,
          audit_note: 'Privacy mode detected but not enforced',
          enforcement: 'audit'
        }
      };
    }
  }

  // Privacy explicitly disabled
  return {
    allowed: true,
    reason: 'Standard mode (privacy disabled by header)',
    route_to: 'standard_replica',
    metadata: {
      privacy_enabled: false,
      header_value: privacyHeader,
      config_default: defaultPrivacyEnabled
    }
  };
}

/**
 * Validate if model is allowed in privacy mode
 * Some models may be prohibited in privacy mode (e.g., models that require plaintext storage)
 */
export async function validateModelForPrivacy(
  model: string,
  orgId: string,
  supabase: SupabaseClient
): Promise<boolean> {
  const { data: config } = await supabase
    .from('privacy_mode_config')
    .select('allowed_models_privacy')
    .eq('org_id', orgId)
    .single();

  if (!config || !config.allowed_models_privacy) {
    // Default: allow Claude models only
    return model.startsWith('claude-');
  }

  return config.allowed_models_privacy.includes(model);
}

/**
 * Check if path should be excluded from indexing (privacy mode)
 * Implements .cursorignore-style pattern matching
 */
export function shouldBlockIndexing(
  filePath: string,
  blockedPaths: string[]
): boolean {
  if (!blockedPaths || blockedPaths.length === 0) {
    return false;
  }

  // Simple glob matching (** = any directory, * = any characters)
  for (const pattern of blockedPaths) {
    const regexPattern = pattern
      .replace(/\*\*/g, '.*') // ** matches any directory
      .replace(/\*/g, '[^/]*') // * matches any characters except /
      .replace(/\./g, '\\.'); // Escape dots

    const regex = new RegExp(`^${regexPattern}$`);
    if (regex.test(filePath)) {
      return true;
    }
  }

  return false;
}

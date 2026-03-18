/**
 * Dataverse Enterprise Console - Policy Gateway Types
 * Portfolio Initiative: PORT-2026-012
 * Controls: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001
 */

export interface PolicyContext {
  org_id: string;
  bot_id: string;
  request_id: string;
  user_id?: string;
}

export interface PolicyDecision {
  allowed: boolean;
  reason: string;
  evidence_id?: string;
  route_to?: string;
  metadata?: Record<string, any>;
}

export interface EnforcementRequest {
  model?: string;
  tool_name?: string;
  org_id: string;
  bot_id: string;
  request_id: string;
  headers?: Record<string, string>;
  payload?: any;
}

export interface PrivacyConfig {
  id: string;
  org_id: string;
  default_privacy_enabled: boolean;
  allowed_models_privacy: string[];
  blocked_indexing_paths: string[];
  enforcement_level: 'strict' | 'warn' | 'audit';
  privacy_replica_endpoint?: string;
}

export interface ModelPolicy {
  id: string;
  org_id: string;
  model_family: string;
  model_name: string;
  policy_type: 'allow' | 'block';
  reason?: string;
}

export interface CapabilityAttestation {
  id: string;
  bot_id: string;
  capability_key: string;
  has_capability: boolean;
  attestation_method?: 'code_scan' | 'manual_verification' | 'test_suite' | 'runtime_validation';
  attestation_evidence?: string;
  last_validated_at?: string;
  expiry_date?: string;
}

export interface PolicyDecisionLog {
  bot_id: string;
  request_id: string;
  policy_type: 'privacy' | 'model' | 'capability' | 'rate_limit' | 'composite';
  decision: 'allow' | 'block' | 'warn';
  reason: string;
  model_requested?: string;
  tool_requested?: string;
  privacy_mode_enabled?: boolean;
  evidence_id?: string;
  evidence_path?: string;
  metadata?: Record<string, any>;
}

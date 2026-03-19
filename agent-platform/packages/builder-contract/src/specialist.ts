/**
 * Specialist handoff interface — PHASE 6.
 * Defines how the precursor routes to specialist agents (e.g., TaxPulse).
 */

/** Specialist domain identifiers */
export type SpecialistDomain =
  | 'tax-compliance'
  | 'finance-close'
  | 'marketing-ops'
  | 'hr-payroll'
  | 'general';

/** Specialist registration */
export interface SpecialistRegistration {
  domain: SpecialistDomain;
  agent_id: string;
  version: string;
  capabilities: string[];
  /** Whether this specialist is ready for production use */
  production_ready: boolean;
  /** Known blockers preventing production readiness */
  blockers: string[];
}

/** Specialist routing decision */
export interface SpecialistRoutingDecision {
  /** Whether to route to a specialist */
  should_route: boolean;
  /** Target specialist domain */
  target_domain: SpecialistDomain;
  /** Confidence score (0-1) */
  confidence: number;
  /** If routing is blocked, the reason */
  block_reason?: string;
}

/**
 * Specialist router interface — implemented by orchestrator.
 * Fail-closed: if specialist is not production_ready, returns block_reason.
 */
export interface SpecialistRouter {
  /** Register a specialist agent */
  register(registration: SpecialistRegistration): void;

  /** Determine if request should route to a specialist */
  route(prompt: string, context: Record<string, unknown>): SpecialistRoutingDecision;

  /** List registered specialists with their readiness status */
  listSpecialists(): SpecialistRegistration[];
}

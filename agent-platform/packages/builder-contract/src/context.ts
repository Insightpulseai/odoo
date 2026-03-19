/**
 * Context Envelope — server-computed context for every copilot request.
 * Mirrors: agents/foundry/ipai-odoo-copilot-azure/context-envelope-contract.md
 */

/** Runtime mode — controls what the agent is permitted to do */
export type RuntimeMode = 'PROD-ADVISORY' | 'PROD-ACTION';

/** Surface where the request originates */
export type Surface = 'web' | 'erp' | 'copilot' | 'analytics' | 'ops';

/** Offering context */
export type Offering = 'odoo-on-cloud' | 'odoo-copilot' | 'analytics';

/** Record scope for contextual requests */
export interface RecordScope {
  model: string;
  id: number;
}

/**
 * Context envelope injected server-side into every agent request.
 * Never exposed to the client. Always logged in audit.
 */
export interface ContextEnvelope {
  // Identity
  user_id: string;
  user_email: string;
  tenant_id: string;

  // Authorization
  app_roles: string[];
  groups: string[];

  // Surface
  surface: Surface;
  offering: Offering;

  // Odoo scope
  company_id: number;
  operating_entity_ids: number[];
  record_scope: RecordScope;

  // Runtime
  mode: RuntimeMode;
  permitted_tools: string[];
  retrieval_scope: string[];
}

/** Construct a maximally-restrictive default envelope */
export function defaultContextEnvelope(): ContextEnvelope {
  return {
    user_id: '',
    user_email: '',
    tenant_id: '',
    app_roles: [],
    groups: [],
    surface: 'web',
    offering: 'odoo-copilot',
    company_id: 0,
    operating_entity_ids: [],
    record_scope: { model: '', id: 0 },
    mode: 'PROD-ADVISORY',
    permitted_tools: [],
    retrieval_scope: [],
  };
}

/**
 * PolicyEngine — enforces guardrails, tool permissions, and fail-closed rules.
 *
 * Key rules:
 * - PROD-ADVISORY mode: no write tools permitted
 * - Tool allowlist enforcement: only permitted_tools from context envelope
 * - Fail-closed for unresolved specialists (e.g., tax/compliance with ATC divergence)
 * - Rate limiting (delegated to caller)
 */

import type {
  ContextEnvelope,
  ToolDefinition,
  SpecialistRegistration,
  SpecialistRoutingDecision,
  SpecialistDomain,
  SpecialistRouter,
} from '@ipai/builder-contract';

/** Policy check result */
export interface PolicyCheckResult {
  permitted: boolean;
  reason: string;
}

/**
 * PolicyEngine — the guardian of agent behavior.
 */
export class PolicyEngine {
  private specialists: Map<SpecialistDomain, SpecialistRegistration> = new Map();

  /**
   * Check if a tool call is permitted given the current context.
   */
  checkToolPermission(toolName: string, context: ContextEnvelope): PolicyCheckResult {
    // Rule 1: In PROD-ADVISORY mode, no write tools allowed
    if (context.mode === 'PROD-ADVISORY') {
      const writePatterns = ['create', 'update', 'delete', 'approve', 'confirm', 'post'];
      const isWriteTool = writePatterns.some((p) => toolName.toLowerCase().includes(p));
      if (isWriteTool) {
        return {
          permitted: false,
          reason: `Write tool "${toolName}" blocked: runtime mode is PROD-ADVISORY`,
        };
      }
    }

    // Rule 2: Tool must be in permitted_tools list
    if (context.permitted_tools.length > 0 && !context.permitted_tools.includes(toolName)) {
      return {
        permitted: false,
        reason: `Tool "${toolName}" not in permitted_tools for user role`,
      };
    }

    return { permitted: true, reason: '' };
  }

  /**
   * Filter tool definitions to only those permitted by current context.
   */
  filterPermittedTools(tools: ToolDefinition[], context: ContextEnvelope): ToolDefinition[] {
    return tools.filter((tool) => {
      const check = this.checkToolPermission(tool.function.name, context);
      return check.permitted;
    });
  }

  /**
   * Build context envelope prefix for injection into the conversation.
   */
  buildContextPrefix(context: ContextEnvelope): string {
    // Omit sensitive fields from the prefix sent to the model
    const safeContext = {
      user_id: context.user_id,
      app_roles: context.app_roles,
      surface: context.surface,
      offering: context.offering,
      company_id: context.company_id,
      mode: context.mode,
      permitted_tools: context.permitted_tools,
      retrieval_scope: context.retrieval_scope,
      record_scope: context.record_scope,
    };

    return `[CONTEXT_ENVELOPE]\n${JSON.stringify(safeContext)}\n[/CONTEXT_ENVELOPE]`;
  }

  /**
   * Create a specialist router that respects fail-closed rules.
   */
  createSpecialistRouter(): SpecialistRouter {
    return {
      register: (reg: SpecialistRegistration) => {
        this.specialists.set(reg.domain, reg);
      },

      route: (prompt: string, _context: Record<string, unknown>): SpecialistRoutingDecision => {
        const lower = prompt.toLowerCase();

        // Detect tax/compliance domain
        if (lower.includes('withholding') || lower.includes('atc') || lower.includes('tax computation')) {
          const taxSpec = this.specialists.get('tax-compliance');
          if (!taxSpec) {
            return {
              should_route: false,
              target_domain: 'tax-compliance',
              confidence: 0.8,
              block_reason: 'Tax specialist not registered. Fail-closed: no autonomous tax operations.',
            };
          }
          if (!taxSpec.production_ready) {
            return {
              should_route: false,
              target_domain: 'tax-compliance',
              confidence: 0.8,
              block_reason: `Tax specialist blocked: ${taxSpec.blockers.join(', ')}`,
            };
          }
          return {
            should_route: true,
            target_domain: 'tax-compliance',
            confidence: 0.85,
          };
        }

        // Detect finance-close domain
        if (lower.includes('close') || lower.includes('reconcil') || lower.includes('fiscal year')) {
          const finSpec = this.specialists.get('finance-close');
          if (finSpec?.production_ready) {
            return {
              should_route: true,
              target_domain: 'finance-close',
              confidence: 0.8,
            };
          }
        }

        // Default: stay with general precursor
        return {
          should_route: false,
          target_domain: 'general',
          confidence: 1.0,
        };
      },

      listSpecialists: (): SpecialistRegistration[] => {
        return Array.from(this.specialists.values());
      },
    };
  }
}

export interface RoutingRule {
  pattern: string; // glob pattern e.g. task.odoo.*
  min_maturity?: string; // L0 - L5
  exclude_agents?: string[];
}

export class RoutingRulesEngine {
  private rules: RoutingRule[] = [];

  // Configuration could be loaded from external agents/foundry/routing-rules.yaml
  loadConfig(config: RoutingRule[]) {
    this.rules = config;
  }

  /**
   * Matches a task type (e.g. 'task.odoo.lint') against wildcard glob patterns.
   */
  match(taskType: string): RoutingRule[] {
    return this.rules.filter(rule => {
      // Convert basic glob * to regex .*
      const regexPattern = '^' + rule.pattern.replace(/\*/g, '.*') + '$';
      const regex = new RegExp(regexPattern);
      return regex.test(taskType);
    });
  }
  
  getAllRules() {
    return this.rules;
  }
}

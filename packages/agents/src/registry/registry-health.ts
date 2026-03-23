import { AgentRegistry } from './registry.js';
import { validatePassportDetails } from './passport-validator.js';

export interface RegistryHealth {
  status: 'healthy' | 'degraded' | 'critical';
  totalAgents: number;
  invalidPassports: string[];
  retiredCount: number;
}

export function registryHealth(registry: AgentRegistry): RegistryHealth {
  const all = registry.list();
  const invalid: string[] = [];
  let retired = 0;

  for (const p of all) {
    if (p.isRetired()) retired++;
    
    // Check deep schema/rule logic
    const validation = validatePassportDetails(p);
    if (!validation.valid) {
      invalid.push(p.data.id);
    }
  }

  return {
    status: invalid.length > 0 ? 'degraded' : 'healthy',
    totalAgents: all.length,
    invalidPassports: invalid,
    retiredCount: retired
  };
}

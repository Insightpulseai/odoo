import { AgentPassport } from './passport.js';
import { RegistryIndex } from './registry-index.js';

export interface AgentFilter {
  domain?: string;
  minMaturity?: string;
  stage?: string;
  owner?: string;
  excludeRetired?: boolean;
}

export function searchAgents(index: RegistryIndex, filter: AgentFilter): AgentPassport[] {
  let results = index.getAll();

  if (filter.domain) {
    results = results.filter(a => a.data.domain === filter.domain);
  }
  if (filter.stage) {
    results = results.filter(a => a.currentStage() === filter.stage);
  }
  if (filter.owner) {
    results = results.filter(a => a.data.owners.includes(filter.owner!));
  }
  if (filter.excludeRetired) {
    results = results.filter(a => !a.isRetired());
  }
  if (filter.minMaturity) {
    results = results.filter(a => a.maturityLevel() >= filter.minMaturity!);
  }

  // Sort by maturity descending, then ID ascending
  results.sort((a, b) => {
    const matDiff = b.maturityLevel().localeCompare(a.maturityLevel());
    if (matDiff !== 0) return matDiff;
    return a.data.id.localeCompare(b.data.id);
  });

  return results;
}

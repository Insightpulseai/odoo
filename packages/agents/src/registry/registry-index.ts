import { AgentPassport } from './passport.js';
import { AgentRegistry } from './registry.js';

export class RegistryIndex {
  private cache: Map<string, AgentPassport> = new Map();
  private registry: AgentRegistry;

  constructor(registry: AgentRegistry) {
    this.registry = registry;
  }

  async build() {
    this.cache.clear();
    const all = this.registry.list();
    for (const p of all) {
      this.cache.set(p.data.id, p);
    }
  }

  getAll(): AgentPassport[] {
    return Array.from(this.cache.values());
  }

  getById(id: string): AgentPassport | undefined {
    return this.cache.get(id);
  }
}

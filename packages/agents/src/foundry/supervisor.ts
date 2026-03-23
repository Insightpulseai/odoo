import * as fs from 'fs';
import * as yaml from 'js-yaml';
import * as path from 'path';
import { AgentRegistry } from '../registry/registry.js';
import { RegistryIndex } from '../registry/registry-index.js';
import { TransitionWorker } from './transition-worker.js';

export class FoundrySupervisor {
  private config: any;
  private mode: 'dry-run' | 'live';

  constructor(
    private registry: AgentRegistry,
    private index: RegistryIndex,
    private worker: TransitionWorker,
    forceMode?: 'dry-run' | 'live'
  ) {
    let configRaw = '';
    try {
      configRaw = fs.readFileSync(path.resolve(process.cwd(), 'ssot/agents/foundry_supervisor.yaml'), 'utf8');
      this.config = yaml.load(configRaw) || {};
    } catch {
       const legacyRaw = fs.readFileSync(path.resolve(process.cwd(), 'agents/foundry/config/supervisor.yaml'), 'utf8');
       this.config = yaml.load(legacyRaw);
    }
    this.mode = forceMode || this.config?.mode?.default || 'dry-run';
  }

  async runCycle() {
    console.log(`[FoundrySupervisor] Starting registry sync cycle in ${this.mode.toUpperCase()} mode...`);
    
    try {
      await this.index.build();
    } catch (e: any) {
      console.error(`[FoundrySupervisor] Fatal error: Stale registry snapshot or missing directory (${e.message})`);
      return; // Fail closed if registry cannot be read
    }
    
    const agents = this.index.getAll();
    const autoPromoteStages: string[] = ['S04', 'S05', 'S06']; // Default targets MVP

    for (const agent of agents) {
      if (agent.isRetired()) continue;

      const current = agent.currentStage();
      let target: string | null = null;
      if (current === 'S03') target = 'S04';
      if (current === 'S04') target = 'S05';
      if (current === 'S05') target = 'S06';

      if (target && autoPromoteStages.includes(target)) {
        console.log(`[FoundrySupervisor] Evaluator tracking ${agent.data.id}: ${current} -> ${target}`);
        try {
          const isLive = this.mode === 'live';
          const success = await this.worker.attemptPromotion(agent.data.id, target, isLive);
          if (success) {
             console.log(`[FoundrySupervisor] ✅ Promotion clear for ${agent.data.id}`);
          }
        } catch (e: any) {
          console.error(`[FoundrySupervisor] Exception processing ${agent.data.id}: ${e.message}`);
        }
      }
    }
    console.log(`[FoundrySupervisor] Cycle complete.`);
  }

  startDaemon() {
    const interval = 60000;
    console.log(`[FoundrySupervisor] Starting daemon loop every ${interval}ms`);
    setInterval(() => this.runCycle(), interval);
  }
}

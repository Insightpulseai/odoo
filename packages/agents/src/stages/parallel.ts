import { StageGateEngine, StageGateResult } from './gate-engine.js';
import { AgentPassport } from '../registry/passport.js';

export class ParallelStageTracker {
  constructor(private gateEngine: StageGateEngine) {}

  /**
   * For decoupled stages like S04 and S05, process concurrently and capture independent results
   */
  async attemptParallelStages(passport: AgentPassport, targetStages: string[]): Promise<Map<string, StageGateResult>> {
    const results = new Map<string, StageGateResult>();
    
    const promises = targetStages.map(async (stageId) => {
      const result = await this.gateEngine.evaluate(passport, stageId);
      results.set(stageId, result);
    });

    await Promise.all(promises);
    return results;
  }
}

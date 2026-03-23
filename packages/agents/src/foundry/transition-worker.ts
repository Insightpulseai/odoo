import { AgentRegistry } from '../registry/registry.js';
import { StageGateEngine } from '../stages/gate-engine.js';
import { PassportVersioner } from '../registry/passport-version.js';
import { RecordGenerator } from './records.js';
import { TransitionLog } from '../stages/transition-log.js';

export class TransitionWorker {
  // Simple in-memory locking for MVP contention checking
  private activeLocks = new Set<string>();

  constructor(
    private registry: AgentRegistry,
    private engine: StageGateEngine,
    private versioner: PassportVersioner,
    private transitionLog: TransitionLog
  ) {}

  async attemptPromotion(agentId: string, targetStage: string, isLive: boolean = false): Promise<boolean> {
    if (this.activeLocks.has(agentId)) {
      throw new Error(`Lock contention: Agent ${agentId} is currently being evaluated by another process.`);
    }
    this.activeLocks.add(agentId);

    try {
      const passport = this.registry.get(agentId);
      const transitionKey = RecordGenerator.getTransitionKey(agentId, passport.currentStage(), targetStage);

      if (RecordGenerator.hasRecord(transitionKey)) {
        console.warn(`[TransitionWorker] Duplicate detected. Agent ${agentId} already holds a promotion record for ${targetStage}. Bypassing.`);
        return false;
      }

      const result = await this.engine.evaluate(passport, targetStage);

      if (result.overall_result === 'pass') {
        if (!isLive) {
          console.log(`[DRY RUN] Would mint promotion for ${agentId} to ${targetStage}`);
          return true; // Simulate pass but do not write to dict
        }

        RecordGenerator.emitPromotion(agentId, result);
        
        const updated = this.versioner.bumpVersion(passport, 'minor');
        const newData = JSON.parse(JSON.stringify(updated.data));
        newData.stage = targetStage;
        
        const finalPassport = Reflect.construct(updated.constructor, [newData]);
        this.registry.update(agentId, finalPassport);
        
        this.transitionLog.log(agentId, result);
        return true;
      } else {
        if (isLive) this.transitionLog.log(agentId, result);
        return false;
      }
    } finally {
      this.activeLocks.delete(agentId);
    }
  }
}

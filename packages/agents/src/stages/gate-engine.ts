import { AgentPassport } from '../registry/passport.js';
import { StageDefinition, StageLoader } from './loader.js';
import { CriteriaEvaluator, CriterionResult } from './criteria-evaluator.js';

export interface StageGateResult {
  gate_id: string;
  stage_from: string;
  stage_to: string;
  criteria: CriterionResult[];
  overall_result: 'pass' | 'fail';
  evaluated_by: string;
}

export class StageGateEngine {
  private stages: Map<string, StageDefinition>;
  private evaluator: CriteriaEvaluator;

  constructor() {
    const list = StageLoader.loadStages();
    this.stages = new Map(list.map(s => [s.id, s]));
    this.evaluator = new CriteriaEvaluator();
  }

  async evaluate(passport: AgentPassport, targetStageId: string): Promise<StageGateResult> {
    const currentStageId = passport.currentStage();
    const currentStage = this.stages.get(currentStageId);
    const targetStage = this.stages.get(targetStageId);

    if (!currentStage || !targetStage) {
      throw new Error(`Invalid stage transition requested: ${currentStageId} -> ${targetStageId}`);
    }

    const gateId = `${currentStageId}-to-${targetStageId}`;
    const results: CriterionResult[] = [];

    // Enforce EXIT criteria from the CURRENT stage block constraints
    if (currentStage.exit_criteria) {
      for (const criterion of currentStage.exit_criteria) {
        results.push(await this.evaluator.evaluate(passport, criterion));
      }
    }

    // Enforce ENTRY criteria of the TARGET stage
    if (targetStage.entry_criteria) {
      for (const criterion of targetStage.entry_criteria) {
        results.push(await this.evaluator.evaluate(passport, criterion));
      }
    }

    const overall = results.every(r => r.result === 'pass') ? 'pass' : 'fail';

    return {
      gate_id: gateId,
      stage_from: currentStageId,
      stage_to: targetStageId,
      criteria: results,
      overall_result: overall,
      evaluated_by: 'system-gate-engine'
    };
  }
}

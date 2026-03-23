import { AgentPassport } from '../registry/passport.js';
import { StageLoader } from './loader.js';
import { CriteriaEvaluator } from './criteria-evaluator.js';

export class ArtifactValidator {
  private evaluator = new CriteriaEvaluator();
  private stages = StageLoader.loadStages();

  async validateStageArtifacts(passport: AgentPassport, stageId: string) {
    const stage = this.stages.find(s => s.id === stageId);
    if (!stage) throw new Error(`Stage ${stageId} not found`);

    const results = [];
    // Just explicitly grab the physical artifact verifications mapped
    const artifacts = (stage.exit_criteria || []).filter(c => c.type === 'artifact_exists');

    for (const c of artifacts) {
      results.push(await this.evaluator.evaluate(passport, c));
    }

    return results;
  }
}

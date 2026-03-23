import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';

export interface CriterionDefinition {
  name: string;
  type: 'artifact_exists' | 'schema_valid' | 'eval_passing' | 'judge_signed' | 'metric_threshold';
  ref?: string;
  threshold?: number;
}

export interface StageDefinition {
  id: string;
  name: string;
  description: string;
  entry_criteria: CriterionDefinition[];
  exit_criteria: CriterionDefinition[];
}

export class StageLoader {
  static loadStages(stagesPath?: string): StageDefinition[] {
    const defaultPath = path.resolve(process.cwd(), 'agents/foundry/gates/stages.yaml');
    const targetPath = stagesPath || defaultPath;
    
    if (!fs.existsSync(targetPath)) {
      throw new Error(`Stages configuration not found at ${targetPath}`);
    }

    const raw = fs.readFileSync(targetPath, 'utf8');
    const parsed = yaml.load(raw) as { stages: StageDefinition[] };
    return parsed.stages || [];
  }
}

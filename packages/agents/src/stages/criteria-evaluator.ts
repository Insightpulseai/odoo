import { CriterionDefinition } from './loader.js';
import { AgentPassport } from '../registry/passport.js';
import { EvalRunner } from '../evals/runner.js';

export interface CriterionResult {
  name: string;
  result: 'pass' | 'fail';
  evidence_ref?: string;
  evaluated_at: string;
  message?: string;
}

export type CriterionEvaluatorPlugin = (
  passport: AgentPassport, 
  criterion: CriterionDefinition
) => CriterionResult | Promise<CriterionResult>;

export class CriteriaEvaluator {
  private plugins = new Map<string, CriterionEvaluatorPlugin>();

  constructor() {
    this.registerDefaults();
  }

  register(type: string, plugin: CriterionEvaluatorPlugin) {
    this.plugins.set(type, plugin);
  }

  async evaluate(passport: AgentPassport, criterion: CriterionDefinition): Promise<CriterionResult> {
    const plugin = this.plugins.get(criterion.type);
    if (!plugin) {
       return {
         name: criterion.name,
         result: 'fail',
         evaluated_at: new Date().toISOString(),
         message: `Unsupported criterion type: ${criterion.type}`
       };
    }
    return await plugin(passport, criterion);
  }

  private registerDefaults() {
    // Artifact verification logic
    this.register('artifact_exists', (passport, criterion) => {
      const ref = criterion.ref?.replace('{agent_id}', passport.data.id);
      if (!ref) return { name: criterion.name, result: 'fail', evaluated_at: new Date().toISOString() };
      
      const absolutePath = path.resolve(process.cwd(), ref);
      const exists = fs.existsSync(absolutePath);
      return {
        name: criterion.name,
        result: exists ? 'pass' : 'fail',
        evidence_ref: ref,
        evaluated_at: new Date().toISOString(),
        message: exists ? 'Found' : 'Missing physical file constraint'
      };
    });

    // Run real evaluation dynamically via EvalRunner mapping for S04 exits
    this.register('eval_passing', async (passport, criterion) => {
      // Assuming a generic default suite exists mapped to the agent ID for the pipeline
      const suitePath = path.resolve(process.cwd(), `agents/evals/${passport.data.id}-suite.yaml`);
      
      if (!fs.existsSync(suitePath)) {
        return {
          name: criterion.name,
          result: 'fail',
          evaluated_at: new Date().toISOString(),
          message: `Missing eval suite configuration for agent at ${suitePath}`
        };
      }

      try {
        const runner = new EvalRunner();
        // Uses default LLM Judge
        const result = await runner.run(passport, suitePath);
        
        const passed = result.data.passed && result.data.score >= (criterion.threshold || 0);

        return {
          name: criterion.name,
          result: passed ? 'pass' : 'fail',
          evaluated_at: new Date().toISOString(),
          message: `Eval Score: ${result.data.score}`
        };
      } catch (err) {
        return {
           name: criterion.name,
           result: 'fail',
           evaluated_at: new Date().toISOString(),
           message: `Eval Runner framework failure: ${err.message}`
        };
      }
    });
  }
}

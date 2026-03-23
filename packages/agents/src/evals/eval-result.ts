import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import * as fs from 'fs';
import * as path from 'path';

export interface EvalResultData {
  agent_id: string;
  target_stage: string;
  judge_id: string;
  decision: 'pass' | 'fail' | 'ambiguous';
  confidence: number;
  reasoning: string;
  evidence_refs: string[];
}

const ajv = new Ajv({ allErrors: true, useDefaults: true });
addFormats(ajv);

const schemaPath = path.resolve(process.cwd(), 'ssot/agents/eval_score_contract.schema.json');
let schemaDoc: any = { type: 'object' };
try {
  schemaDoc = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
} catch (e) { }

const validateSchema = ajv.compile(schemaDoc);

export class EvalResult {
  public readonly data: EvalResultData;

  private constructor(data: EvalResultData) {
    this.data = Object.freeze(JSON.parse(JSON.stringify(data)));
  }

  static create(params: EvalResultData): EvalResult {
    const isValid = validateSchema(params);
    if (!isValid) {
      throw new Error(`Invalid EvalResult schema: ${ajv.errorsText(validateSchema.errors)}`);
    }
    return new EvalResult(params);
  }

  toJSON(): string { return JSON.stringify(this.data, null, 2); }
}

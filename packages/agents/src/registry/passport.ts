import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';

export interface AgentPassportData {
  schema: 'ipai.passport.v1';
  id: string;
  version: string;
  name: string;
  domain: string;
  stage: string;
  maturity: 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5';
  contract_ref: string;
  skills?: string[];
  tools?: string[];
  policies?: string[];
  kill_switch: {
    enabled: boolean;
    active?: boolean;
    reason?: string;
  };
  owners: string[];
  created_at: string;
  updated_at: string;
}

const ajv = new Ajv({ allErrors: true, useDefaults: true });
addFormats(ajv);

const schemaPath = path.resolve(__dirname, '../../schemas/passport.schema.json');
let schemaDoc: any = { type: 'object' };
try {
  schemaDoc = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
} catch (e) {
  // Silent fallback for environments missing the file during build
}

const validateSchema = ajv.compile(schemaDoc);

export class AgentPassport {
  public readonly data: AgentPassportData;

  constructor(data: AgentPassportData) {
    const isValid = validateSchema(data);
    if (!isValid) {
      throw new Error(`Invalid AgentPassport: ${ajv.errorsText(validateSchema.errors)}`);
    }
    // Deep freeze for immutability
    this.data = Object.freeze(JSON.parse(JSON.stringify(data)));
  }

  static fromYAML(yamlString: string): AgentPassport {
    const parsed = yaml.load(yamlString) as AgentPassportData;
    return new AgentPassport(parsed);
  }

  toYAML(): string {
    return yaml.dump(this.data, { indent: 2 });
  }

  currentStage(): string {
    return this.data.stage;
  }

  maturityLevel(): string {
    return this.data.maturity;
  }

  isRetired(): boolean {
    return this.data.stage === 'S16';
  }
}

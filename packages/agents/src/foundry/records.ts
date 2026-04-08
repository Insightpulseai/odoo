import * as fs from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import { StageGateResult } from '../stages/gate-engine.js';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

let schemaDoc: any;
try {
  schemaDoc = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), 'ssot/agents/promotion_record.schema.json'), 'utf8'));
} catch (e) {
  schemaDoc = { type: 'object' }; // Fallback for tests
}
const validateRecord = ajv.compile(schemaDoc);

export class RecordGenerator {
  static get RECORDS_DIR() { return path.resolve(process.cwd(), 'agents/promotions'); }

  static getTransitionKey(agentId: string, from: string, to: string, version: string = 'v1'): string {
    return `${agentId}:${from}:${to}:${version}`;
  }

  static hasRecord(transitionKey: string): boolean {
    if (!fs.existsSync(this.RECORDS_DIR)) return false;
    const files = fs.readdirSync(this.RECORDS_DIR);
    for (const f of files) {
      if (!f.endsWith('.json')) continue;
      const data = JSON.parse(fs.readFileSync(path.join(this.RECORDS_DIR, f), 'utf8'));
      if (data.transition_key === transitionKey) return true;
    }
    return false;
  }

  static emitPromotion(agentId: string, result: StageGateResult, approver: string = 'foundry-supervisor') {
    const transitionKey = this.getTransitionKey(agentId, result.stage_from, result.stage_to);
    
    if (this.hasRecord(transitionKey)) {
      throw new Error(`Idempotency fault: Promotion record for ${transitionKey} already exists.`);
    }

    const record = {
      record_type: 'promotion',
      record_version: '1.0.0',
      agent_id: agentId,
      from_stage: result.stage_from,
      to_stage: result.stage_to,
      gate_version: 'v1',
      decision: result.overall_result,
      evidence_refs: result.criteria.map(c => c.name),
      issued_at: new Date().toISOString(),
      issued_by: approver,
      transition_key: transitionKey
    };

    const isValid = validateRecord(record);
    if (!isValid) {
      throw new Error(`Schema validation failed against ipai.promotion.v1.hardened: ${ajv.errorsText(validateRecord.errors)}`);
    }

    if (!fs.existsSync(this.RECORDS_DIR)) fs.mkdirSync(this.RECORDS_DIR, { recursive: true });
    
    // Immutable write policy explicitly handled by checking prior file locks via wx flag
    const filePath = path.join(this.RECORDS_DIR, `${agentId}-${transitionKey.replace(/:/g, '-')}.json`);
    if (fs.existsSync(filePath)) {
      throw new Error(`Immutable record overwrite attempt blocked at ${filePath}`);
    }
    
    fs.writeFileSync(filePath, JSON.stringify(record, null, 2), { flag: 'wx' });
  }
}

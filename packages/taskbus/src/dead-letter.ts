import * as fs from 'fs';
import * as path from 'path';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

let schemaDoc: any;
try {
  schemaDoc = JSON.parse(fs.readFileSync(path.resolve(process.cwd(), 'ssot/agents/dead_letter_record.schema.json'), 'utf8'));
} catch (e) {
  schemaDoc = { type: 'object' };
}
const validateDL = ajv.compile(schemaDoc);

export class DeadLetterQueue {
  private logPath = path.resolve(process.cwd(), 'agents/dead-letters');

  appendToDLQ(taskId: string, type: string, reason: string, attempts: number) {
    if (!fs.existsSync(this.logPath)) fs.mkdirSync(this.logPath, { recursive: true });
    
    const record = {
      record_type: 'dead_letter',
      record_version: '1.0.0',
      task_id: taskId,
      task_type: type,
      failure_reason: reason,
      attempts,
      first_seen_at: new Date().toISOString(),
      last_failed_at: new Date().toISOString(),
      trace_id: `dlq-${Date.now()}`,
      evidence_refs: []
    };

    if (!validateDL(record)) throw new Error('Invalid DLQ schema write');

    // Immutable write
    fs.writeFileSync(path.join(this.logPath, `${taskId}.json`), JSON.stringify(record, null, 2), { flag: 'wx' });
  }
}

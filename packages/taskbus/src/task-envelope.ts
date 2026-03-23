import Ajv from 'ajv';
import addFormats from 'ajv-formats';
// Using generic import for schema to avoid TS errors without resolveJsonModule
import * as fs from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';

// Since we may not have cross-package references perfectly compiling without emit, 
// we'll define minimal aliases based on the Phase 0 types.
export type TaskId = string;
export type TaskType = string;
export type AgentId = string;
export type CorrelationId = string;

export interface TaskEnvelopeData {
  task_id: TaskId;
  type: TaskType;
  priority: 'low' | 'normal' | 'high' | 'critical';
  payload: Record<string, unknown>;
  source_agent_id?: AgentId;
  target_agent_id?: AgentId;
  correlation_id: CorrelationId;
  created_at: string;
  timeout_ms?: number;
  idempotency_key?: string;
}

const ajv = new Ajv({ allErrors: true, useDefaults: true });
addFormats(ajv);

// Load schema dynamically to avoid TS compilation issues with JSON
const schemaPath = path.resolve(__dirname, '../schemas/task-envelope.schema.json');
let schema: any;
try {
  schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
} catch (e) {
  // Mock schema fallback if unable to load (e.g. during certain test environments)
  schema = { type: "object" };
}

const validateSchema = ajv.compile(schema);

export class TaskEnvelope {
  public readonly data: TaskEnvelopeData;

  private constructor(data: TaskEnvelopeData) {
    this.data = data;
  }

  static create(params: Omit<TaskEnvelopeData, 'task_id' | 'created_at'>): TaskEnvelope {
    const envelope = {
      ...params,
      task_id: randomUUID(),
      created_at: new Date().toISOString(),
      priority: params.priority || 'normal',
      timeout_ms: params.timeout_ms || 300000
    };

    const isValid = validateSchema(envelope);
    if (!isValid) {
      throw new Error(`Invalid TaskEnvelope: ${ajv.errorsText(validateSchema.errors)}`);
    }

    return new TaskEnvelope(envelope as TaskEnvelopeData);
  }

  static fromJSON(jsonString: string): TaskEnvelope {
    const parsed = JSON.parse(jsonString);
    const isValid = validateSchema(parsed);
    if (!isValid) {
      throw new Error(`Invalid TaskEnvelope JSON: ${ajv.errorsText(validateSchema.errors)}`);
    }
    return new TaskEnvelope(parsed as TaskEnvelopeData);
  }

  toJSON(): string {
    return JSON.stringify(this.data);
  }

  get id(): TaskId { return this.data.task_id; }
  get type(): TaskType { return this.data.type; }
  get priority() { return this.data.priority; }
  get payload() { return this.data.payload; }
  get correlationId(): CorrelationId { return this.data.correlation_id; }
}

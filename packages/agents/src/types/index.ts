// Branded Types implementation details
declare const brand: unique symbol;

export type Brand<K, T> = K & { [brand]: T };

export type AgentId = Brand<string, 'AgentId'>;
export type TaskType = Brand<string, 'TaskType'>;
export type CorrelationId = Brand<string, 'CorrelationId'>;
export type ISO8601 = Brand<string, 'ISO8601'>;
export type TaskId = Brand<string, 'TaskId'>;

export type StageId = 
  | 'S01' | 'S02' | 'S03' | 'S04' 
  | 'S05' | 'S06' | 'S07' | 'S08' 
  | 'S09' | 'S10' | 'S11' | 'S12' 
  | 'S13' | 'S14' | 'S15' | 'S16';

export type MaturityLevel = 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5';

export type GateResult = 'pass' | 'fail';

/**
 * Creates an AgentId from a string
 */
export function createAgentId(id: string): AgentId {
  return id as AgentId;
}

/**
 * Creates a TaskType from a string
 */
export function createTaskType(type: string): TaskType {
  return type as TaskType;
}

/**
 * Creates a CorrelationId from a uuid string
 */
export function createCorrelationId(id: string): CorrelationId {
  return id as CorrelationId;
}

/**
 * Creates an ISO8601 date string
 */
export function createISO8601(dateString: string): ISO8601 {
  return dateString as ISO8601;
}

/**
 * Creates a TaskId from a uuid string
 */
export function createTaskId(id: string): TaskId {
  return id as TaskId;
}

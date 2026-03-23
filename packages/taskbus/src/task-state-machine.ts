import EventEmitter from 'events';
import { TaskEnvelope, TaskId, AgentId } from './task-envelope.js';

export type TaskState = 
  | 'pending'
  | 'routed'
  | 'in_progress'
  | 'completed'
  | 'failed'
  | 'timed_out'
  | 'dead_letter';

export interface StateTransitionEvent {
  taskId: TaskId;
  fromState: TaskState | null;
  toState: TaskState;
  timestamp: string;
  workerId?: AgentId | 'system';
  reason?: string;
  error?: Error;
}

export class TaskStateMachine extends EventEmitter {
  private currentState: TaskState;
  private envelope: TaskEnvelope;
  private historyLog: StateTransitionEvent[] = [];
  
  // Valid transitions dictionary
  private static readonly VALID_TRANSITIONS: Record<TaskState, TaskState[]> = {
    'pending': ['routed', 'failed', 'dead_letter'],
    'routed': ['in_progress', 'failed', 'dead_letter'],
    'in_progress': ['completed', 'failed', 'timed_out'],
    'completed': [], // Terminal
    'failed': ['routed', 'dead_letter'], // Can be retried
    'timed_out': ['routed', 'dead_letter'], // Can be retried
    'dead_letter': [] // Terminal
  };

  constructor(envelope: TaskEnvelope) {
    super();
    this.envelope = envelope;
    this.currentState = 'pending';
    this.recordTransition(null, 'pending', 'system', 'Task created');
  }

  public get state(): TaskState {
    return this.currentState;
  }

  public get history(): ReadonlyArray<StateTransitionEvent> {
    return this.historyLog;
  }

  public transition(
    toState: TaskState, 
    workerId: AgentId | 'system', 
    reason?: string, 
    error?: Error
  ): void {
    const validNextStates = TaskStateMachine.VALID_TRANSITIONS[this.currentState];
    
    if (!validNextStates.includes(toState)) {
      throw new Error(
        `Invalid state transition for task ${this.envelope.id}: Cannot transition from ${this.currentState} to ${toState}`
      );
    }

    const previousState = this.currentState;
    this.currentState = toState;
    
    const event = this.recordTransition(previousState, toState, workerId, reason, error);
    
    // Emit global bus event
    this.emit('transition', event);
    this.emit(toState, event);
  }

  private recordTransition(
    fromState: TaskState | null,
    toState: TaskState,
    workerId: string = 'system',
    reason?: string,
    error?: Error
  ): StateTransitionEvent {
    const event: StateTransitionEvent = {
      taskId: this.envelope.id,
      fromState,
      toState,
      timestamp: new Date().toISOString(),
      workerId,
      reason,
      error
    };
    this.historyLog.push(event);
    return event;
  }
}

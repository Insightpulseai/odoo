import { StateTransitionEvent } from './task-state-machine.js';
import * as fs from 'fs';

export class TaskEventLog {
  private logPath: string;

  constructor(logPath: string = 'agents/foundry/task-events.jsonl') {
    this.logPath = logPath;
  }

  append(event: StateTransitionEvent) {
    const entry = {
      ...event,
      error: event.error ? event.error.message : undefined
    };
    try {
      fs.appendFileSync(this.logPath, JSON.stringify(entry) + '\n');
    } catch (e) {
      console.error('Failed to write to task event log. Proceeding memory-only.', e);
    }
  }
}

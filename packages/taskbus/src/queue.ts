import { TaskEnvelope } from './task-envelope.js';

export interface TaskQueueBackend {
  enqueue(envelope: TaskEnvelope, priorityScore: number): void;
  dequeue(): TaskEnvelope | null;
  peek(): TaskEnvelope | null;
  size(): number;
  drain(): TaskEnvelope[];
}

/**
 * Priority mapping heuristic -> smaller number = higher priority
 */
const PRIORITY_SCORES: Record<string, number> = {
  'critical': 0,
  'high': 1,
  'normal': 2,
  'low': 3
};

export class InMemoryTaskQueue implements TaskQueueBackend {
  private queue: { envelope: TaskEnvelope; score: number }[] = [];

  enqueue(envelope: TaskEnvelope, priorityScore?: number): void {
    const score = priorityScore ?? PRIORITY_SCORES[envelope.priority] ?? 2;
    this.queue.push({ envelope, score });
    // Stable sort ascending by score
    this.queue.sort((a, b) => a.score - b.score);
  }

  dequeue(): TaskEnvelope | null {
    const item = this.queue.shift();
    return item ? item.envelope : null;
  }

  peek(): TaskEnvelope | null {
    return this.queue.length > 0 ? this.queue[0].envelope : null;
  }

  size(): number {
    return this.queue.length;
  }

  drain(): TaskEnvelope[] {
    const drained = this.queue.map(q => q.envelope);
    this.queue = [];
    return drained;
  }
}

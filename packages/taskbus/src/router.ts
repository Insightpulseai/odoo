import { RouterMetrics } from './metrics.js';
import { ClaimLeaseManager } from './lease.js';
import { DeadLetterQueue } from './dead-letter.js';
import { TaskEnvelope } from './task-envelope.js';

export type RouterState = 'queued' | 'claimed' | 'retry_scheduled' | 'dead_lettered' | 'completed' | 'quarantined';

export class StatefulTaskRouter {
  private queue: TaskEnvelope[] = [];
  private states = new Map<string, RouterState>();
  private dedupeLog = new Set<string>();

  constructor(
    private metrics: RouterMetrics,
    private leaseManager: ClaimLeaseManager,
    private dlq: DeadLetterQueue
  ) {}

  enqueue(envelopeStr: string) {
    let envelope: TaskEnvelope;
    try {
      envelope = TaskEnvelope.fromJSON(envelopeStr);
    } catch {
      this.metrics.recordCount('malformed_envelope_rejects');
      return 'quarantined';
    }

    const dedupeKey = `${envelope.id}:${envelope.type}:1`;
    if (this.dedupeLog.has(dedupeKey)) {
      this.metrics.recordCount('duplicate_suppression_count');
      return 'suppressed';
    }
    
    this.dedupeLog.add(dedupeKey);
    this.queue.push(envelope);
    this.states.set(envelope.id, 'queued');
    this.metrics.recordCount('tasks_enqueued');
    this.metrics.setGauge('queue_depth_gauge', this.queue.length);
    return 'queued';
  }

  claim(workerId: string): TaskEnvelope | null {
    // Find first available that we can lock
    for (let i = 0; i < this.queue.length; i++) {
        const task = this.queue[i];
        if (this.states.get(task.id) === 'queued' || this.states.get(task.id) === 'retry_scheduled') {
           const acquired = this.leaseManager.acquire(task.id, workerId);
           if (acquired) {
              this.states.set(task.id, 'claimed');
              return task;
           }
        }
    }
    return null;
  }

  complete(taskId: string, workerId: string) {
    if (this.states.get(taskId) !== 'claimed') return;
    this.states.set(taskId, 'completed');
    this.leaseManager.release(taskId, workerId);
    this.queue = this.queue.filter(t => t.id !== taskId);
    this.metrics.setGauge('queue_depth_gauge', this.queue.length);
  }

  fail(taskId: string, reason: string) {
    if (this.states.get(taskId) !== 'claimed') return;
    
    const attempts = this.leaseManager.getAttempts(taskId);
    if (attempts >= 5) {
      this.states.set(taskId, 'dead_lettered');
      const task = this.queue.find(t => t.id === taskId);
      if (task) this.dlq.appendToDLQ(taskId, task.type, reason, attempts);
      this.queue = this.queue.filter(t => t.id !== taskId);
      this.metrics.recordCount('retry_exhaustion_count');
      this.metrics.recordCount('dead_letter_count');
    } else {
      this.states.set(taskId, 'retry_scheduled');
      this.metrics.recordCount('retries_scheduled');
    }
  }

  getState(taskId: string) { return this.states.get(taskId); }
  getMetrics() { return this.metrics; }
}

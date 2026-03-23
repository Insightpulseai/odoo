import { RouterMetrics } from './metrics.js';

export class ClaimLeaseManager {
  private leases = new Map<string, { workerId: string; expiresAt: number; attempts: number }>();
  constructor(private ttlMs = 60000, private metrics: RouterMetrics) {}

  acquire(taskId: string, workerId: string, maxAttempts = 5): boolean {
    const existing = this.leases.get(taskId);
    if (existing) {
      if (Date.now() < existing.expiresAt) {
        this.metrics.recordCount('claim_conflicts');
        return false; // Active lock exists
      }
      this.metrics.recordCount('lease_expiries');
    }
    const attempts = (existing?.attempts || 0) + 1;
    if (attempts > maxAttempts) return false; // Handled by retry exhaustion

    this.leases.set(taskId, { workerId, expiresAt: Date.now() + this.ttlMs, attempts });
    this.metrics.recordCount('tasks_claimed');
    return true;
  }

  release(taskId: string, workerId: string) {
    const existing = this.leases.get(taskId);
    if (existing && existing.workerId === workerId) {
      this.leases.delete(taskId);
    }
  }

  getAttempts(taskId: string) {
    return this.leases.get(taskId)?.attempts || 0;
  }
}

import { InMemoryTaskQueue } from './queue.js';
import { RoutingRulesEngine } from './routing-rules.js';

export interface TaskBusHealth {
  status: 'healthy' | 'degraded' | 'down';
  queueDepth: number;
  rulesLoaded: number;
  timestamp: string;
}

export function taskBusHealth(queue: InMemoryTaskQueue, rulesEngine: RoutingRulesEngine): TaskBusHealth {
  const depth = queue.size();
  return {
    status: depth > 1000 ? 'degraded' : 'healthy', // arbitrary degradation threshold
    queueDepth: depth,
    rulesLoaded: rulesEngine.getAllRules().length,
    timestamp: new Date().toISOString()
  };
}

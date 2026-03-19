/**
 * Restart Policy
 *
 * Deterministic, pure function for deciding if config changes require VM restart.
 *
 * Constitution Rule: Safe Restarts
 * - Resource changes require explicit user approval
 * - Config changes set restart_required flag
 * - No auto-restart on config change
 */

import type { ColimaConfig } from './contracts/index.js';

// ============================================================================
// Types
// ============================================================================

/**
 * Restart Decision
 */
export interface RestartDecision {
  required: boolean;
  reasons: string[];
}

/**
 * Restart Reasons (field names that trigger restart)
 */
export type RestartReason =
  | 'cpu'
  | 'memory'
  | 'disk'
  | 'kubernetes'
  | 'runtime';

// ============================================================================
// Restart Policy Logic
// ============================================================================

/**
 * Check if config changes require VM restart
 *
 * Pure, deterministic function with structured output.
 *
 * @param prev - Previous config
 * @param next - Updated config
 * @returns RestartDecision with required flag and reasons
 *
 * @example
 * const decision = restartRequired(prevConfig, nextConfig);
 * if (decision.required) {
 *   console.log(`Restart required due to: ${decision.reasons.join(', ')}`);
 * }
 */
export function restartRequired(
  prev: ColimaConfig,
  next: ColimaConfig
): RestartDecision {
  const reasons: RestartReason[] = [];

  // CPU changes require restart
  if (prev.colima.cpu !== next.colima.cpu) {
    reasons.push('cpu');
  }

  // Memory changes require restart
  if (prev.colima.memory !== next.colima.memory) {
    reasons.push('memory');
  }

  // Disk changes require restart
  if (prev.colima.disk !== next.colima.disk) {
    reasons.push('disk');
  }

  // Kubernetes toggle requires restart
  if (prev.colima.kubernetes !== next.colima.kubernetes) {
    reasons.push('kubernetes');
  }

  // Runtime change requires restart
  if (prev.colima.runtime !== next.colima.runtime) {
    reasons.push('runtime');
  }

  return {
    required: reasons.length > 0,
    reasons,
  };
}

/**
 * Get human-readable restart message
 *
 * @param decision - RestartDecision from restartRequired()
 * @returns User-friendly message
 *
 * @example
 * const msg = getRestartMessage(decision);
 * // "Restart required to apply changes: cpu, memory"
 */
export function getRestartMessage(decision: RestartDecision): string {
  if (!decision.required) {
    return 'No restart required';
  }

  const reasons = decision.reasons.join(', ');
  return `Restart required to apply changes: ${reasons}`;
}

/**
 * Get detailed change descriptions
 *
 * @param prev - Previous config
 * @param next - Updated config
 * @returns Array of change descriptions (e.g., "cpu: 4 → 6")
 *
 * @example
 * const changes = getConfigChanges(prevConfig, nextConfig);
 * // ["cpu: 4 → 6", "memory: 8GB → 12GB"]
 */
export function getConfigChanges(
  prev: ColimaConfig,
  next: ColimaConfig
): string[] {
  const changes: string[] = [];

  // Daemon changes (no restart required)
  if (prev.daemon.port !== next.daemon.port) {
    changes.push(`daemon.port: ${prev.daemon.port} → ${next.daemon.port}`);
  }
  if (prev.daemon.host !== next.daemon.host) {
    changes.push(`daemon.host: ${prev.daemon.host} → ${next.daemon.host}`);
  }
  if (prev.daemon.autostart !== next.daemon.autostart) {
    changes.push(
      `daemon.autostart: ${prev.daemon.autostart} → ${next.daemon.autostart}`
    );
  }

  // Colima VM changes (may require restart)
  if (prev.colima.cpu !== next.colima.cpu) {
    changes.push(`cpu: ${prev.colima.cpu} → ${next.colima.cpu}`);
  }
  if (prev.colima.memory !== next.colima.memory) {
    changes.push(`memory: ${prev.colima.memory}GB → ${next.colima.memory}GB`);
  }
  if (prev.colima.disk !== next.colima.disk) {
    changes.push(`disk: ${prev.colima.disk}GB → ${next.colima.disk}GB`);
  }
  if (prev.colima.kubernetes !== next.colima.kubernetes) {
    changes.push(
      `kubernetes: ${prev.colima.kubernetes} → ${next.colima.kubernetes}`
    );
  }
  if (prev.colima.runtime !== next.colima.runtime) {
    changes.push(
      `runtime: ${prev.colima.runtime} → ${next.colima.runtime}`
    );
  }

  // Logs changes (no restart required)
  if (prev.logs.retention_days !== next.logs.retention_days) {
    changes.push(
      `logs.retention_days: ${prev.logs.retention_days} → ${next.logs.retention_days}`
    );
  }
  if (prev.logs.max_lines !== next.logs.max_lines) {
    changes.push(
      `logs.max_lines: ${prev.logs.max_lines} → ${next.logs.max_lines}`
    );
  }
  if (prev.logs.level !== next.logs.level) {
    changes.push(`logs.level: ${prev.logs.level} → ${next.logs.level}`);
  }

  return changes;
}

// ============================================================================
// Restart Policy Tests (used by vitest)
// ============================================================================

/**
 * Test scenarios for restart policy
 *
 * These scenarios are used by vitest to ensure deterministic behavior.
 */
export const RESTART_POLICY_SCENARIOS = {
  // Changes that DO require restart
  cpu_change: {
    prev: { colima: { cpu: 4 } },
    next: { colima: { cpu: 6 } },
    expected: { required: true, reasons: ['cpu'] },
  },
  memory_change: {
    prev: { colima: { memory: 8 } },
    next: { colima: { memory: 12 } },
    expected: { required: true, reasons: ['memory'] },
  },
  disk_change: {
    prev: { colima: { disk: 60 } },
    next: { colima: { disk: 80 } },
    expected: { required: true, reasons: ['disk'] },
  },
  kubernetes_toggle: {
    prev: { colima: { kubernetes: false } },
    next: { colima: { kubernetes: true } },
    expected: { required: true, reasons: ['kubernetes'] },
  },
  runtime_change: {
    prev: { colima: { runtime: 'docker' } },
    next: { colima: { runtime: 'containerd' } },
    expected: { required: true, reasons: ['runtime'] },
  },
  multiple_changes: {
    prev: { colima: { cpu: 4, memory: 8, kubernetes: false } },
    next: { colima: { cpu: 6, memory: 12, kubernetes: true } },
    expected: { required: true, reasons: ['cpu', 'memory', 'kubernetes'] },
  },

  // Changes that DO NOT require restart
  daemon_port_change: {
    prev: { daemon: { port: 35100 } },
    next: { daemon: { port: 35200 } },
    expected: { required: false, reasons: [] },
  },
  daemon_autostart_change: {
    prev: { daemon: { autostart: false } },
    next: { daemon: { autostart: true } },
    expected: { required: false, reasons: [] },
  },
  logs_level_change: {
    prev: { logs: { level: 'info' } },
    next: { logs: { level: 'debug' } },
    expected: { required: false, reasons: [] },
  },
  logs_retention_change: {
    prev: { logs: { retention_days: 7 } },
    next: { logs: { retention_days: 14 } },
    expected: { required: false, reasons: [] },
  },

  // No changes
  no_changes: {
    prev: { colima: { cpu: 4 }, daemon: { port: 35100 }, logs: { level: 'info' } },
    next: { colima: { cpu: 4 }, daemon: { port: 35100 }, logs: { level: 'info' } },
    expected: { required: false, reasons: [] },
  },
} as const;

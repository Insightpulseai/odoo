/**
 * Restart Policy Tests
 *
 * Lock down deterministic restart semantics.
 * These tests ensure the restart policy remains stable across changes.
 */

import { describe, it, expect } from 'vitest';
import {
  restartRequired,
  getRestartMessage,
  getConfigChanges,
  RESTART_POLICY_SCENARIOS,
} from '../../src/shared/restartPolicy.js';
import { DEFAULT_CONFIG } from '../../src/shared/contracts/index.js';
import type { ColimaConfig } from '../../src/shared/contracts/index.js';

describe('restartPolicy', () => {
  describe('restartRequired()', () => {
    it('should return false when no changes', () => {
      const result = restartRequired(DEFAULT_CONFIG, DEFAULT_CONFIG);
      expect(result.required).toBe(false);
      expect(result.reasons).toEqual([]);
    });

    it('should detect CPU changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, cpu: 6 } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('cpu');
    });

    it('should detect memory changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, memory: 12 } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('memory');
    });

    it('should detect disk changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, disk: 80 } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('disk');
    });

    it('should detect kubernetes toggle', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, kubernetes: true } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('kubernetes');
    });

    it('should detect runtime changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, runtime: 'containerd' } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('runtime');
    });

    it('should detect multiple changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = {
        ...DEFAULT_CONFIG,
        colima: {
          ...DEFAULT_CONFIG.colima,
          cpu: 6,
          memory: 12,
          kubernetes: true,
        },
      };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(true);
      expect(result.reasons).toContain('cpu');
      expect(result.reasons).toContain('memory');
      expect(result.reasons).toContain('kubernetes');
    });

    it('should NOT require restart for daemon port changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, daemon: { ...DEFAULT_CONFIG.daemon, port: 35200 } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(false);
    });

    it('should NOT require restart for daemon autostart changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, daemon: { ...DEFAULT_CONFIG.daemon, autostart: true } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(false);
    });

    it('should NOT require restart for log level changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, logs: { ...DEFAULT_CONFIG.logs, level: 'debug' } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(false);
    });

    it('should NOT require restart for log retention changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, logs: { ...DEFAULT_CONFIG.logs, retention_days: 14 } };

      const result = restartRequired(prev, next);
      expect(result.required).toBe(false);
    });
  });

  describe('getRestartMessage()', () => {
    it('should return "No restart required" when not required', () => {
      const decision = { required: false, reasons: [] };
      const msg = getRestartMessage(decision);
      expect(msg).toBe('No restart required');
    });

    it('should list reasons when restart required', () => {
      const decision = { required: true, reasons: ['cpu', 'memory'] };
      const msg = getRestartMessage(decision);
      expect(msg).toContain('cpu');
      expect(msg).toContain('memory');
    });
  });

  describe('getConfigChanges()', () => {
    it('should return empty array when no changes', () => {
      const changes = getConfigChanges(DEFAULT_CONFIG, DEFAULT_CONFIG);
      expect(changes).toEqual([]);
    });

    it('should describe CPU changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, cpu: 6 } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('cpu: 4 → 6');
    });

    it('should describe memory changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, memory: 12 } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('memory: 8GB → 12GB');
    });

    it('should describe disk changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, disk: 80 } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('disk: 60GB → 80GB');
    });

    it('should describe kubernetes changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, kubernetes: true } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('kubernetes: false → true');
    });

    it('should describe runtime changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, colima: { ...DEFAULT_CONFIG.colima, runtime: 'containerd' } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('runtime: docker → containerd');
    });

    it('should describe daemon changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, daemon: { ...DEFAULT_CONFIG.daemon, port: 35200 } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('daemon.port: 35100 → 35200');
    });

    it('should describe log changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = { ...DEFAULT_CONFIG, logs: { ...DEFAULT_CONFIG.logs, level: 'debug' } };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('logs.level: info → debug');
    });

    it('should describe multiple changes', () => {
      const prev = { ...DEFAULT_CONFIG };
      const next = {
        ...DEFAULT_CONFIG,
        colima: {
          ...DEFAULT_CONFIG.colima,
          cpu: 6,
          memory: 12,
        },
        daemon: {
          ...DEFAULT_CONFIG.daemon,
          port: 35200,
        },
      };

      const changes = getConfigChanges(prev, next);
      expect(changes).toContain('daemon.port: 35100 → 35200');
      expect(changes).toContain('cpu: 4 → 6');
      expect(changes).toContain('memory: 8GB → 12GB');
    });
  });

  describe('RESTART_POLICY_SCENARIOS (consistency check)', () => {
    // These tests verify that the scenarios defined in restartPolicy.ts
    // match the actual behavior of the functions.
    // This prevents scenario drift from implementation.

    // Not all scenarios are valid for the test since they use partial configs
    // Just test a representative sample

    it('should match cpu_change scenario', () => {
      const { prev, next, expected } = RESTART_POLICY_SCENARIOS.cpu_change;
      // Create full configs
      const prevFull = { ...DEFAULT_CONFIG, ...prev };
      const nextFull = { ...DEFAULT_CONFIG, ...next };

      const result = restartRequired(prevFull as ColimaConfig, nextFull as ColimaConfig);
      expect(result.required).toBe(expected.required);
      expect(result.reasons).toEqual(expected.reasons);
    });

    it('should match memory_change scenario', () => {
      const { prev, next, expected } = RESTART_POLICY_SCENARIOS.memory_change;
      const prevFull = { ...DEFAULT_CONFIG, ...prev };
      const nextFull = { ...DEFAULT_CONFIG, ...next };

      const result = restartRequired(prevFull as ColimaConfig, nextFull as ColimaConfig);
      expect(result.required).toBe(expected.required);
      expect(result.reasons).toEqual(expected.reasons);
    });

    it('should match daemon_port_change scenario (no restart)', () => {
      const { prev, next, expected } = RESTART_POLICY_SCENARIOS.daemon_port_change;
      const prevFull = { ...DEFAULT_CONFIG, ...prev };
      const nextFull = { ...DEFAULT_CONFIG, ...next };

      const result = restartRequired(prevFull as ColimaConfig, nextFull as ColimaConfig);
      expect(result.required).toBe(expected.required);
      expect(result.reasons).toEqual(expected.reasons);
    });
  });
});

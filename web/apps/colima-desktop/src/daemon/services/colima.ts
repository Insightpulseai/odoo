/**
 * Colima CLI Wrapper Service
 *
 * Core integration layer with Colima CLI.
 * Single source of truth for all VM operations.
 *
 * CRITICAL FILE - See spec/colima-desktop/plan.md
 *
 * Responsibilities:
 * - Compose colima commands (start, stop, status, list, version)
 * - Parse stdout/stderr into typed interfaces
 * - Handle errors (command not found, non-zero exit, timeout)
 * - Provide typed API for all Colima operations
 *
 * NOTE: All command execution delegated to exec.run() wrapper
 */

import { run, isExecError, getErrorMessage } from './exec.js';
import type {
  ColimaStatus,
  ColimaVersionInfo,
  VMState,
  LifecycleRequest,
} from '../../shared/contracts/index.js';

// ============================================================================
// Constants
// ============================================================================

const COLIMA_BINARY = 'colima';
const START_TIMEOUT = 120000; // 2 minutes (VM start can be slow)

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Parse resource value from status output
 * Examples: "4" -> 4, "8GiB" -> 8, "60GB" -> 60
 */
function parseResourceValue(value: string): number {
  const match = value.match(/^(\d+)/);
  return match ? parseInt(match[1], 10) : 0;
}

// ============================================================================
// ColimaService Class
// ============================================================================

export class ColimaService {
  /**
   * Check if Colima is installed
   */
  async isInstalled(): Promise<boolean> {
    try {
      await this.version();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get Colima and Lima versions
   */
  async version(): Promise<ColimaVersionInfo> {
    try {
      const result = await run(COLIMA_BINARY, ['version'], {
        timeout: 5000,
      });

      const lines = result.stdout.split('\n');
      const colimaLine = lines.find((l) => l.includes('colima version'));
      const limaLine = lines.find((l) => l.includes('lima version'));
      const qemuLine = lines.find((l) => l.includes('qemu-img version'));

      return {
        colima_version: colimaLine?.split(' ').pop() ?? 'unknown',
        lima_version: limaLine?.split(' ').pop() ?? 'unknown',
        qemu_version: qemuLine?.split(' ')[2] ?? 'unknown',
      };
    } catch (err) {
      throw this.wrapError('version', err);
    }
  }

  /**
   * Get VM status
   */
  async status(): Promise<ColimaStatus> {
    try {
      const result = await run(COLIMA_BINARY, ['status'], {
        timeout: 10000,
      });

      // Parse status output
      // Example output:
      // INFO[0000] colima is running
      // INFO[0000] arch: aarch64
      // INFO[0000] runtime: docker
      // INFO[0000] cpu: 4
      // INFO[0000] memory: 8GiB
      // INFO[0000] disk: 60GiB

      const lines = result.stdout.split('\n');
      const state = this.parseStatusState(result.stdout, result.exitCode);

      // Extract resources from output
      const cpuLine = lines.find((l) => l.includes('cpu:'));
      const memLine = lines.find((l) => l.includes('memory:'));
      const diskLine = lines.find((l) => l.includes('disk:'));
      const archLine = lines.find((l) => l.includes('arch:'));
      const runtimeLine = lines.find((l) => l.includes('runtime:'));

      return {
        state,
        cpu: cpuLine ? parseResourceValue(cpuLine.split(':')[1]) : 0,
        memory: memLine ? parseResourceValue(memLine.split(':')[1]) : 0,
        disk: diskLine ? parseResourceValue(diskLine.split(':')[1]) : 0,
        kubernetes: await this.isKubernetesEnabled(),
        arch: archLine?.split(':')[1]?.trim() ?? 'unknown',
        runtime:
          (runtimeLine?.split(':')[1]?.trim() as 'docker' | 'containerd') ??
          'docker',
      };
    } catch (err) {
      // If colima status fails, VM is likely stopped
      if (isExecError(err)) {
        return {
          state: 'stopped',
          cpu: 0,
          memory: 0,
          disk: 0,
          kubernetes: false,
          arch: 'unknown',
          runtime: 'docker',
        };
      }
      throw this.wrapError('status', err);
    }
  }

  /**
   * Start VM
   */
  async start(opts: LifecycleRequest = {}): Promise<void> {
    try {
      const args = ['start'];

      if (opts.cpu) args.push('--cpu', opts.cpu.toString());
      if (opts.memory) args.push('--memory', opts.memory.toString());
      if (opts.disk) args.push('--disk', opts.disk.toString());

      await run(COLIMA_BINARY, args, {
        timeout: START_TIMEOUT,
      });
    } catch (err) {
      throw this.wrapError('start', err);
    }
  }

  /**
   * Stop VM
   */
  async stop(): Promise<void> {
    try {
      await run(COLIMA_BINARY, ['stop'], {
        timeout: 60000, // 1 minute
      });
    } catch (err) {
      throw this.wrapError('stop', err);
    }
  }

  /**
   * Restart VM
   */
  async restart(opts: LifecycleRequest = {}): Promise<void> {
    try {
      // Colima restart command applies config changes
      const args = ['restart'];

      if (opts.cpu) args.push('--cpu', opts.cpu.toString());
      if (opts.memory) args.push('--memory', opts.memory.toString());
      if (opts.disk) args.push('--disk', opts.disk.toString());

      await run(COLIMA_BINARY, args, {
        timeout: START_TIMEOUT,
      });
    } catch (err) {
      throw this.wrapError('restart', err);
    }
  }

  /**
   * Delete VM
   */
  async delete(): Promise<void> {
    try {
      await run(COLIMA_BINARY, ['delete', '-f'], {
        timeout: 60000,
      });
    } catch (err) {
      throw this.wrapError('delete', err);
    }
  }

  /**
   * Check if Kubernetes is enabled
   */
  async isKubernetesEnabled(): Promise<boolean> {
    try {
      const result = await run(COLIMA_BINARY, ['kubernetes'], {
        timeout: 5000,
      });

      // Check if kubernetes is running
      return result.stdout.toLowerCase().includes('running');
    } catch {
      return false;
    }
  }

  /**
   * Enable/disable Kubernetes
   */
  async setKubernetes(enabled: boolean): Promise<void> {
    try {
      const args = ['kubernetes'];
      if (enabled) {
        args.push('start');
      } else {
        args.push('stop');
      }

      await run(COLIMA_BINARY, args, {
        timeout: 60000,
      });
    } catch (err) {
      throw this.wrapError(
        `kubernetes ${enabled ? 'start' : 'stop'}`,
        err
      );
    }
  }

  // ==========================================================================
  // Helper Methods
  // ==========================================================================

  /**
   * Parse status state from output and exit code
   */
  private parseStatusState(stdout: string, exitCode: number): VMState {
    if (exitCode !== 0) return 'stopped';

    const lower = stdout.toLowerCase();
    if (lower.includes('running')) return 'running';
    if (lower.includes('starting')) return 'starting';
    if (lower.includes('stopping')) return 'stopping';
    if (lower.includes('stopped')) return 'stopped';

    return 'error';
  }

  /**
   * Wrap errors with context
   */
  private wrapError(command: string, err: unknown): Error {
    if (isExecError(err)) {
      const msg = getErrorMessage(err);
      return new Error(`Colima ${command} failed: ${msg}`);
    }

    if (err instanceof Error) {
      return new Error(`Colima ${command} failed: ${err.message}`);
    }

    return new Error(`Colima ${command} failed: ${String(err)}`);
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const colimaService = new ColimaService();

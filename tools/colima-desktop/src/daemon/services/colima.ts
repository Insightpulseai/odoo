/**
 * Colima CLI Wrapper Service
 *
 * Core integration layer with Colima CLI.
 * Single source of truth for all VM operations.
 *
 * CRITICAL FILE - See spec/colima-desktop/plan.md
 *
 * Responsibilities:
 * - Spawn colima commands (start, stop, status, list, version)
 * - Parse stdout/stderr into typed interfaces
 * - Handle errors (command not found, non-zero exit, timeout)
 * - Provide typed API for all Colima operations
 */

import { spawn } from 'node:child_process';
import type {
  ColimaStatus,
  ColimaVersionInfo,
  VMState,
  LifecycleRequest,
  ColimaCliError,
} from '../../shared/types.js';

// ============================================================================
// Types
// ============================================================================

interface SpawnOptions {
  timeout?: number;
  cwd?: string;
  env?: NodeJS.ProcessEnv;
}

interface SpawnResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

// ============================================================================
// Constants
// ============================================================================

const COLIMA_BINARY = 'colima';
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const START_TIMEOUT = 120000; // 2 minutes (VM start can be slow)

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Spawn a command and capture output
 */
async function spawnCommand(
  command: string,
  args: string[],
  options: SpawnOptions = {}
): Promise<SpawnResult> {
  return new Promise((resolve, reject) => {
    const timeout = options.timeout ?? DEFAULT_TIMEOUT;
    let stdout = '';
    let stderr = '';
    let timedOut = false;

    const proc = spawn(command, args, {
      cwd: options.cwd,
      env: options.env ?? process.env,
    });

    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill('SIGTERM');
      reject(
        new Error(
          `Command timed out after ${timeout}ms: ${command} ${args.join(' ')}`
        )
      );
    }, timeout);

    proc.stdout?.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr?.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('error', (err) => {
      clearTimeout(timer);
      if (!timedOut) {
        reject(err);
      }
    });

    proc.on('close', (code) => {
      clearTimeout(timer);
      if (!timedOut) {
        resolve({
          stdout: stdout.trim(),
          stderr: stderr.trim(),
          exitCode: code ?? 0,
        });
      }
    });
  });
}

/**
 * Parse VM state from colima status output
 */
function parseVMState(statusLine: string): VMState {
  const lower = statusLine.toLowerCase();
  if (lower.includes('running')) return 'running';
  if (lower.includes('stopped')) return 'stopped';
  if (lower.includes('starting')) return 'starting';
  if (lower.includes('stopping')) return 'stopping';
  return 'error';
}

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
      const result = await spawnCommand(COLIMA_BINARY, ['version'], {
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
      const result = await spawnCommand(COLIMA_BINARY, ['status'], {
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
      if (this.isColimaError(err)) {
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

      const result = await spawnCommand(COLIMA_BINARY, args, {
        timeout: START_TIMEOUT,
      });

      if (result.exitCode !== 0) {
        throw new Error(
          `Colima start failed (exit ${result.exitCode}): ${result.stderr}`
        );
      }
    } catch (err) {
      throw this.wrapError('start', err);
    }
  }

  /**
   * Stop VM
   */
  async stop(): Promise<void> {
    try {
      const result = await spawnCommand(COLIMA_BINARY, ['stop'], {
        timeout: 60000, // 1 minute
      });

      if (result.exitCode !== 0) {
        throw new Error(
          `Colima stop failed (exit ${result.exitCode}): ${result.stderr}`
        );
      }
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

      const result = await spawnCommand(COLIMA_BINARY, args, {
        timeout: START_TIMEOUT,
      });

      if (result.exitCode !== 0) {
        throw new Error(
          `Colima restart failed (exit ${result.exitCode}): ${result.stderr}`
        );
      }
    } catch (err) {
      throw this.wrapError('restart', err);
    }
  }

  /**
   * Delete VM
   */
  async delete(): Promise<void> {
    try {
      const result = await spawnCommand(COLIMA_BINARY, ['delete', '-f'], {
        timeout: 60000,
      });

      if (result.exitCode !== 0) {
        throw new Error(
          `Colima delete failed (exit ${result.exitCode}): ${result.stderr}`
        );
      }
    } catch (err) {
      throw this.wrapError('delete', err);
    }
  }

  /**
   * Check if Kubernetes is enabled
   */
  async isKubernetesEnabled(): Promise<boolean> {
    try {
      const result = await spawnCommand(COLIMA_BINARY, ['kubernetes'], {
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

      const result = await spawnCommand(COLIMA_BINARY, args, {
        timeout: 60000,
      });

      if (result.exitCode !== 0) {
        throw new Error(
          `Kubernetes ${enabled ? 'start' : 'stop'} failed: ${result.stderr}`
        );
      }
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
   * Check if error is from Colima CLI
   */
  private isColimaError(err: unknown): err is ColimaCliError {
    return (
      typeof err === 'object' &&
      err !== null &&
      'exitCode' in err &&
      'stdout' in err &&
      'stderr' in err
    );
  }

  /**
   * Wrap errors with context
   */
  private wrapError(command: string, err: unknown): Error {
    if (err instanceof Error) {
      if (err.message.includes('ENOENT')) {
        return new Error(
          'Colima not found. Install it with: brew install colima'
        );
      }
      return new Error(`Colima ${command} failed: ${err.message}`);
    }
    return new Error(`Colima ${command} failed: ${String(err)}`);
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const colimaService = new ColimaService();

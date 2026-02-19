/**
 * Execution Envelope
 *
 * Centralized command execution wrapper with standardized:
 * - Timeout handling
 * - stdout/stderr capture
 * - Structured error responses
 * - Redaction policy (for sensitive paths/tokens)
 *
 * All command spawning MUST go through this wrapper.
 */

import { spawn } from 'node:child_process';

// ============================================================================
// Types
// ============================================================================

/**
 * Execution Options
 */
export interface ExecOptions {
  /** Timeout in milliseconds (default: 30s) */
  timeout?: number;
  /** Working directory */
  cwd?: string;
  /** Environment variables */
  env?: NodeJS.ProcessEnv;
  /** Redact sensitive patterns from output (default: true) */
  redact?: boolean;
}

/**
 * Execution Result
 */
export interface ExecResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  timedOut: boolean;
  duration_ms: number;
}

/**
 * Execution Error
 */
export class ExecError extends Error {
  constructor(
    public command: string,
    public args: string[],
    public exitCode: number,
    public stdout: string,
    public stderr: string,
    public timedOut: boolean
  ) {
    super(
      timedOut
        ? `Command timed out: ${command} ${args.join(' ')}`
        : `Command failed (exit ${exitCode}): ${command} ${args.join(' ')}\n${stderr}`
    );
    this.name = 'ExecError';
  }
}

// ============================================================================
// Constants
// ============================================================================

const DEFAULT_TIMEOUT = 30000; // 30 seconds

/**
 * Sensitive patterns to redact from output
 */
const REDACTION_PATTERNS = [
  // Paths that might contain user info
  /\/Users\/[^\/]+/g,
  // Potential tokens (anything that looks like base64 or hex)
  /[a-zA-Z0-9+/]{40,}/g,
];

// ============================================================================
// Execution Wrapper
// ============================================================================

/**
 * Run a command with standardized execution envelope
 *
 * @param command - Command to execute
 * @param args - Command arguments
 * @param options - Execution options
 * @returns ExecResult with stdout, stderr, exitCode, etc.
 * @throws ExecError if command fails or times out
 *
 * @example
 * const result = await run('colima', ['status'], { timeout: 10000 });
 * console.log(result.stdout);
 */
export async function run(
  command: string,
  args: string[] = [],
  options: ExecOptions = {}
): Promise<ExecResult> {
  const timeout = options.timeout ?? DEFAULT_TIMEOUT;
  const redact = options.redact ?? true;
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    let stdout = '';
    let stderr = '';
    let timedOut = false;

    // Spawn process
    const proc = spawn(command, args, {
      cwd: options.cwd,
      env: options.env ?? process.env,
    });

    // Timeout handler
    const timer = setTimeout(() => {
      timedOut = true;
      proc.kill('SIGTERM');

      // Give it 5 seconds to terminate gracefully, then SIGKILL
      setTimeout(() => {
        if (!proc.killed) {
          proc.kill('SIGKILL');
        }
      }, 5000);
    }, timeout);

    // Capture stdout
    proc.stdout?.on('data', (data) => {
      stdout += data.toString();
    });

    // Capture stderr
    proc.stderr?.on('data', (data) => {
      stderr += data.toString();
    });

    // Handle errors
    proc.on('error', (err) => {
      clearTimeout(timer);
      if (!timedOut) {
        // Command not found or spawn failed
        reject(
          new ExecError(
            command,
            args,
            -1,
            '',
            err.message,
            false
          )
        );
      }
    });

    // Handle completion
    proc.on('close', (code) => {
      clearTimeout(timer);

      const duration_ms = Date.now() - startTime;
      const exitCode = code ?? 0;

      // Redact sensitive info if enabled
      const finalStdout = redact ? redactSensitive(stdout.trim()) : stdout.trim();
      const finalStderr = redact ? redactSensitive(stderr.trim()) : stderr.trim();

      const result: ExecResult = {
        stdout: finalStdout,
        stderr: finalStderr,
        exitCode,
        timedOut,
        duration_ms,
      };

      // Reject on timeout or non-zero exit
      if (timedOut) {
        reject(
          new ExecError(
            command,
            args,
            exitCode,
            finalStdout,
            finalStderr,
            true
          )
        );
      } else if (exitCode !== 0) {
        reject(
          new ExecError(
            command,
            args,
            exitCode,
            finalStdout,
            finalStderr,
            false
          )
        );
      } else {
        resolve(result);
      }
    });
  });
}

/**
 * Redact sensitive patterns from output
 *
 * @param text - Text to redact
 * @returns Text with sensitive patterns replaced
 */
function redactSensitive(text: string): string {
  let redacted = text;

  for (const pattern of REDACTION_PATTERNS) {
    redacted = redacted.replace(pattern, '[REDACTED]');
  }

  return redacted;
}

/**
 * Check if error is an ExecError
 *
 * @param err - Error to check
 * @returns True if error is ExecError
 */
export function isExecError(err: unknown): err is ExecError {
  return err instanceof ExecError;
}

/**
 * Extract user-friendly error message from ExecError
 *
 * @param err - ExecError instance
 * @returns User-friendly error message
 */
export function getErrorMessage(err: ExecError): string {
  if (err.timedOut) {
    return `Command timed out: ${err.command}`;
  }

  if (err.exitCode === -1) {
    return `Command not found: ${err.command}. Is it installed?`;
  }

  if (err.stderr) {
    return err.stderr;
  }

  return `Command failed (exit ${err.exitCode}): ${err.command}`;
}

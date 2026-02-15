/**
 * Configuration Management
 *
 * Responsibilities:
 * - Load YAML config from ~/.colima-desktop/config.yaml
 * - Validate config schema
 * - Provide defaults for missing fields
 * - Atomic writes (prevent corruption)
 * - Config change detection (restart required?)
 */

import { readFile, writeFile, mkdir, rename } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { parse, stringify } from 'yaml';
import type {
  ColimaConfig,
  DaemonConfig,
  ColimaVMConfig,
  LogsConfig,
  Paths,
} from './types.js';
import { DEFAULT_CONFIG, CONSTRAINTS, STATE_DIR, CONFIG_FILE } from './types.js';

// ============================================================================
// Path Resolution
// ============================================================================

/**
 * Get all paths for state directory
 */
export function getPaths(): Paths {
  const home = homedir();
  const state_dir = join(home, STATE_DIR);
  const logs_dir = join(state_dir, 'logs');
  const diagnostics_dir = join(state_dir, 'diagnostics');

  return {
    home,
    state_dir,
    config_file: join(state_dir, CONFIG_FILE),
    pid_file: join(state_dir, 'daemon.pid'),
    logs_dir,
    daemon_log: join(logs_dir, 'daemon.log'),
    colima_log: join(logs_dir, 'colima.log'),
    lima_log: join(logs_dir, 'lima.log'),
    diagnostics_dir,
  };
}

// ============================================================================
// Validation
// ============================================================================

/**
 * Validation Errors
 */
export class ValidationError extends Error {
  constructor(
    public field: string,
    public message: string,
    public received?: unknown
  ) {
    super(`Validation error: ${field} - ${message}`);
    this.name = 'ValidationError';
  }
}

/**
 * Validate daemon config
 */
function validateDaemonConfig(config: unknown): asserts config is DaemonConfig {
  if (typeof config !== 'object' || config === null) {
    throw new ValidationError('daemon', 'Must be an object');
  }

  const daemon = config as DaemonConfig;

  // Port
  if (typeof daemon.port !== 'number') {
    throw new ValidationError('daemon.port', 'Must be a number', daemon.port);
  }
  if (
    daemon.port < CONSTRAINTS.PORT.min ||
    daemon.port > CONSTRAINTS.PORT.max
  ) {
    throw new ValidationError(
      'daemon.port',
      `Must be between ${CONSTRAINTS.PORT.min} and ${CONSTRAINTS.PORT.max}`,
      daemon.port
    );
  }

  // Host
  if (typeof daemon.host !== 'string') {
    throw new ValidationError('daemon.host', 'Must be a string', daemon.host);
  }
  if (daemon.host !== 'localhost' && daemon.host !== '127.0.0.1') {
    throw new ValidationError(
      'daemon.host',
      'Must be "localhost" or "127.0.0.1" (security constraint)',
      daemon.host
    );
  }

  // Autostart
  if (typeof daemon.autostart !== 'boolean') {
    throw new ValidationError(
      'daemon.autostart',
      'Must be a boolean',
      daemon.autostart
    );
  }
}

/**
 * Validate Colima VM config
 */
function validateColimaConfig(config: unknown): asserts config is ColimaVMConfig {
  if (typeof config !== 'object' || config === null) {
    throw new ValidationError('colima', 'Must be an object');
  }

  const colima = config as ColimaVMConfig;

  // CPU
  if (typeof colima.cpu !== 'number') {
    throw new ValidationError('colima.cpu', 'Must be a number', colima.cpu);
  }
  if (colima.cpu < CONSTRAINTS.CPU.min || colima.cpu > CONSTRAINTS.CPU.max) {
    throw new ValidationError(
      'colima.cpu',
      `Must be between ${CONSTRAINTS.CPU.min} and ${CONSTRAINTS.CPU.max}`,
      colima.cpu
    );
  }

  // Memory
  if (typeof colima.memory !== 'number') {
    throw new ValidationError(
      'colima.memory',
      'Must be a number',
      colima.memory
    );
  }
  if (
    colima.memory < CONSTRAINTS.MEMORY.min ||
    colima.memory > CONSTRAINTS.MEMORY.max
  ) {
    throw new ValidationError(
      'colima.memory',
      `Must be between ${CONSTRAINTS.MEMORY.min} and ${CONSTRAINTS.MEMORY.max} GB`,
      colima.memory
    );
  }

  // Disk
  if (typeof colima.disk !== 'number') {
    throw new ValidationError('colima.disk', 'Must be a number', colima.disk);
  }
  if (
    colima.disk < CONSTRAINTS.DISK.min ||
    colima.disk > CONSTRAINTS.DISK.max
  ) {
    throw new ValidationError(
      'colima.disk',
      `Must be between ${CONSTRAINTS.DISK.min} and ${CONSTRAINTS.DISK.max} GB`,
      colima.disk
    );
  }

  // Kubernetes
  if (typeof colima.kubernetes !== 'boolean') {
    throw new ValidationError(
      'colima.kubernetes',
      'Must be a boolean',
      colima.kubernetes
    );
  }

  // Runtime
  if (colima.runtime !== 'docker' && colima.runtime !== 'containerd') {
    throw new ValidationError(
      'colima.runtime',
      'Must be "docker" or "containerd"',
      colima.runtime
    );
  }
}

/**
 * Validate logs config
 */
function validateLogsConfig(config: unknown): asserts config is LogsConfig {
  if (typeof config !== 'object' || config === null) {
    throw new ValidationError('logs', 'Must be an object');
  }

  const logs = config as LogsConfig;

  // Retention days
  if (typeof logs.retention_days !== 'number') {
    throw new ValidationError(
      'logs.retention_days',
      'Must be a number',
      logs.retention_days
    );
  }
  if (logs.retention_days < 1 || logs.retention_days > 365) {
    throw new ValidationError(
      'logs.retention_days',
      'Must be between 1 and 365',
      logs.retention_days
    );
  }

  // Max lines
  if (typeof logs.max_lines !== 'number') {
    throw new ValidationError(
      'logs.max_lines',
      'Must be a number',
      logs.max_lines
    );
  }
  if (logs.max_lines < 100 || logs.max_lines > 10000) {
    throw new ValidationError(
      'logs.max_lines',
      'Must be between 100 and 10000',
      logs.max_lines
    );
  }

  // Level
  if (!['debug', 'info', 'warn', 'error'].includes(logs.level)) {
    throw new ValidationError(
      'logs.level',
      'Must be one of: debug, info, warn, error',
      logs.level
    );
  }
}

/**
 * Validate complete config
 */
export function validateConfig(config: unknown): asserts config is ColimaConfig {
  if (typeof config !== 'object' || config === null) {
    throw new ValidationError('config', 'Must be an object');
  }

  const cfg = config as ColimaConfig;

  validateDaemonConfig(cfg.daemon);
  validateColimaConfig(cfg.colima);
  validateLogsConfig(cfg.logs);
}

// ============================================================================
// Config Loading
// ============================================================================

/**
 * Ensure state directory exists
 */
export async function ensureStateDir(): Promise<void> {
  const paths = getPaths();

  if (!existsSync(paths.state_dir)) {
    await mkdir(paths.state_dir, { recursive: true });
  }

  if (!existsSync(paths.logs_dir)) {
    await mkdir(paths.logs_dir, { recursive: true });
  }

  if (!existsSync(paths.diagnostics_dir)) {
    await mkdir(paths.diagnostics_dir, { recursive: true });
  }
}

/**
 * Load config from file (with defaults for missing fields)
 */
export async function loadConfig(): Promise<ColimaConfig> {
  const paths = getPaths();

  // Ensure state directory exists
  await ensureStateDir();

  // If config doesn't exist, create with defaults
  if (!existsSync(paths.config_file)) {
    await saveConfig(DEFAULT_CONFIG);
    return DEFAULT_CONFIG;
  }

  try {
    const content = await readFile(paths.config_file, 'utf-8');
    const parsed = parse(content);

    // Merge with defaults (in case new fields added)
    const config: ColimaConfig = {
      daemon: { ...DEFAULT_CONFIG.daemon, ...parsed.daemon },
      colima: { ...DEFAULT_CONFIG.colima, ...parsed.colima },
      logs: { ...DEFAULT_CONFIG.logs, ...parsed.logs },
    };

    // Validate
    validateConfig(config);

    return config;
  } catch (err) {
    if (err instanceof ValidationError) {
      throw err;
    }
    throw new Error(`Failed to load config: ${(err as Error).message}`);
  }
}

/**
 * Save config to file (atomic write)
 */
export async function saveConfig(config: ColimaConfig): Promise<void> {
  const paths = getPaths();

  // Validate before saving
  validateConfig(config);

  // Ensure state directory exists
  await ensureStateDir();

  // Atomic write: write to temp file, then rename
  const tmpPath = `${paths.config_file}.tmp`;
  const yamlContent = stringify(config);

  await writeFile(tmpPath, yamlContent, 'utf-8');
  await rename(tmpPath, paths.config_file);
}

// ============================================================================
// Config Change Detection
// ============================================================================

/**
 * Check if config changes require VM restart
 */
export function requiresRestart(
  current: ColimaConfig,
  updated: ColimaConfig
): boolean {
  // Changes that require restart
  return (
    current.colima.cpu !== updated.colima.cpu ||
    current.colima.memory !== updated.colima.memory ||
    current.colima.disk !== updated.colima.disk ||
    current.colima.kubernetes !== updated.colima.kubernetes ||
    current.colima.runtime !== updated.colima.runtime
  );
}

/**
 * Get list of changes between two configs
 */
export function getConfigChanges(
  current: ColimaConfig,
  updated: ColimaConfig
): string[] {
  const changes: string[] = [];

  // Daemon changes
  if (current.daemon.port !== updated.daemon.port) {
    changes.push(`daemon.port: ${current.daemon.port} → ${updated.daemon.port}`);
  }
  if (current.daemon.host !== updated.daemon.host) {
    changes.push(`daemon.host: ${current.daemon.host} → ${updated.daemon.host}`);
  }
  if (current.daemon.autostart !== updated.daemon.autostart) {
    changes.push(
      `daemon.autostart: ${current.daemon.autostart} → ${updated.daemon.autostart}`
    );
  }

  // Colima VM changes
  if (current.colima.cpu !== updated.colima.cpu) {
    changes.push(`cpu: ${current.colima.cpu} → ${updated.colima.cpu}`);
  }
  if (current.colima.memory !== updated.colima.memory) {
    changes.push(`memory: ${current.colima.memory}GB → ${updated.colima.memory}GB`);
  }
  if (current.colima.disk !== updated.colima.disk) {
    changes.push(`disk: ${current.colima.disk}GB → ${updated.colima.disk}GB`);
  }
  if (current.colima.kubernetes !== updated.colima.kubernetes) {
    changes.push(
      `kubernetes: ${current.colima.kubernetes} → ${updated.colima.kubernetes}`
    );
  }
  if (current.colima.runtime !== updated.colima.runtime) {
    changes.push(
      `runtime: ${current.colima.runtime} → ${updated.colima.runtime}`
    );
  }

  // Logs changes
  if (current.logs.retention_days !== updated.logs.retention_days) {
    changes.push(
      `logs.retention_days: ${current.logs.retention_days} → ${updated.logs.retention_days}`
    );
  }
  if (current.logs.max_lines !== updated.logs.max_lines) {
    changes.push(
      `logs.max_lines: ${current.logs.max_lines} → ${updated.logs.max_lines}`
    );
  }
  if (current.logs.level !== updated.logs.level) {
    changes.push(`logs.level: ${current.logs.level} → ${updated.logs.level}`);
  }

  return changes;
}

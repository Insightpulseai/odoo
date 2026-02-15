#!/usr/bin/env node
/**
 * Ensure Repo Root
 *
 * Deterministic repo root resolution for scripts and tests.
 * Prevents "works on my machine" issues from cwd dependence.
 *
 * Usage:
 * ```typescript
 * import { getRepoRoot, resolveFromRoot } from './ensure_repo_root.js';
 *
 * const root = await getRepoRoot();
 * const configPath = resolveFromRoot('tools/colima-desktop/config.yaml');
 * ```
 */

import { existsSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// ============================================================================
// Sentinel Files
// ============================================================================

/**
 * Sentinel files that indicate repo root
 * Checked in order of specificity
 */
const SENTINELS = [
  '.git',           // Git repository marker (most reliable)
  'package.json',   // Project root marker
  'pnpm-workspace.yaml', // Monorepo marker
  'CLAUDE.md',      // Repo SSOT marker
];

// ============================================================================
// Repo Root Resolution
// ============================================================================

/**
 * Find repository root by walking up from current directory
 *
 * @param startPath - Starting directory (default: current working directory)
 * @returns Absolute path to repo root
 * @throws Error if repo root not found
 *
 * @example
 * const root = await getRepoRoot();
 * // "/Users/user/repo"
 */
export async function getRepoRoot(startPath?: string): Promise<string> {
  let currentDir = resolve(startPath ?? process.cwd());
  const root = '/'; // Stop at filesystem root

  while (currentDir !== root) {
    // Check for sentinel files
    for (const sentinel of SENTINELS) {
      const sentinelPath = join(currentDir, sentinel);
      if (existsSync(sentinelPath)) {
        return currentDir;
      }
    }

    // Move up one directory
    const parentDir = dirname(currentDir);
    if (parentDir === currentDir) {
      // Reached filesystem root without finding sentinel
      break;
    }
    currentDir = parentDir;
  }

  throw new Error(
    `Could not find repository root. Searched from: ${startPath ?? process.cwd()}\n` +
    `Looking for one of: ${SENTINELS.join(', ')}`
  );
}

/**
 * Resolve path relative to repo root
 *
 * @param relativePath - Path relative to repo root
 * @returns Absolute path
 *
 * @example
 * const configPath = await resolveFromRoot('tools/colima-desktop/config.yaml');
 * // "/Users/user/repo/tools/colima-desktop/config.yaml"
 */
export async function resolveFromRoot(relativePath: string): Promise<string> {
  const root = await getRepoRoot();
  return join(root, relativePath);
}

/**
 * Get repo root synchronously
 *
 * @param startPath - Starting directory (default: current working directory)
 * @returns Absolute path to repo root
 * @throws Error if repo root not found
 */
export function getRepoRootSync(startPath?: string): string {
  let currentDir = resolve(startPath ?? process.cwd());
  const root = '/';

  while (currentDir !== root) {
    for (const sentinel of SENTINELS) {
      const sentinelPath = join(currentDir, sentinel);
      if (existsSync(sentinelPath)) {
        return currentDir;
      }
    }

    const parentDir = dirname(currentDir);
    if (parentDir === currentDir) {
      break;
    }
    currentDir = parentDir;
  }

  throw new Error(
    `Could not find repository root. Searched from: ${startPath ?? process.cwd()}\n` +
    `Looking for one of: ${SENTINELS.join(', ')}`
  );
}

/**
 * Resolve path relative to repo root (sync)
 *
 * @param relativePath - Path relative to repo root
 * @returns Absolute path
 */
export function resolveFromRootSync(relativePath: string): string {
  const root = getRepoRootSync();
  return join(root, relativePath);
}

// ============================================================================
// CLI Mode
// ============================================================================

if (import.meta.url === `file://${process.argv[1]}`) {
  // Running as CLI
  try {
    const root = await getRepoRoot();
    console.log(root);
    process.exit(0);
  } catch (err) {
    console.error((err as Error).message);
    process.exit(1);
  }
}

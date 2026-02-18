/**
 * Types Compatibility Shim
 *
 * @deprecated This file is deprecated. Import from './contracts/index.js' instead.
 *
 * This shim maintains backward compatibility for existing imports while
 * the codebase migrates to the modular contracts structure.
 *
 * Migration guide:
 * - OLD: import { StatusResponse } from './shared/types.js';
 * - NEW: import { StatusResponse } from './shared/contracts/index.js';
 *
 * This file will be removed in Phase 3.
 */

// Re-export everything from contracts
export * from './contracts/index.js';

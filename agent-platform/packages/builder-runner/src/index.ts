/**
 * @ipai/builder-runner -- CLI and server runner for the agent platform.
 *
 * Entry point: `builder-runner` CLI command (see cli.ts)
 * Programmatic usage: import Orchestrator, FoundryClient, etc. from upstream packages.
 */

// Re-export key types for programmatic access
export type { PrecursorRequest, PrecursorResponse } from '@ipai/builder-contract';
export { Orchestrator } from '@ipai/builder-orchestrator';
export { MockFoundryClient, AzureFoundryClient } from '@ipai/builder-foundry-client';

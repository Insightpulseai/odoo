/**
 * @ipai/builder-foundry-client — Foundry client abstraction layer.
 *
 * Provides:
 * - FoundryClient interface (adapter boundary)
 * - MockFoundryClient (local dev/test)
 * - AzureFoundryClient (production stub, real SDK in Stage 2)
 */

export * from './foundry-client.js';
export * from './mock-foundry-client.js';
export * from './azure-foundry-client.js';

/**
 * React Integration for IPAI Design Tokens
 * =========================================
 *
 * This module provides React hooks and components for integrating
 * Odoo brand tokens with Fluent UI and ChatGPT App SDK.
 *
 * Exports:
 * - useOdooTokens: Hook for fetching and using tokens
 * - OdooTokensProvider: Context provider for tokens
 * - useOdooTokensContext: Hook to access tokens from context
 */

export { useOdooTokens } from './useOdooTokens';
export type { UseOdooTokensOptions, UseOdooTokensResult } from './useOdooTokens';

export {
  OdooTokensProvider,
  useOdooTokensContext,
} from './OdooTokensProvider';
export type { OdooTokensProviderProps } from './OdooTokensProvider';

// Re-export token utilities
export {
  OdooTokens,
  defaultTokens,
  fetchOdooTokens,
  createFluentTheme,
  createAppSDKTheme,
  applyTokensToDocument,
} from '../odooTokens';

/**
 * Odoo Tokens Provider for React
 * ===============================
 *
 * Provides Odoo brand tokens via React Context, with automatic Fluent UI integration.
 *
 * Usage:
 * ```tsx
 * import { OdooTokensProvider, useOdooTokensContext } from '@ipai/design-tokens/react';
 *
 * function App() {
 *   return (
 *     <OdooTokensProvider
 *       baseUrl="https://erp.insightpulseai.com"
 *       companyId={1}
 *     >
 *       <FluentIntegration />
 *     </OdooTokensProvider>
 *   );
 * }
 *
 * function FluentIntegration() {
 *   const { fluentTheme } = useOdooTokensContext();
 *   return (
 *     <FluentProvider theme={fluentTheme}>
 *       <YourApp />
 *     </FluentProvider>
 *   );
 * }
 * ```
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useOdooTokens, UseOdooTokensOptions, UseOdooTokensResult } from './useOdooTokens';
import { defaultTokens, createFluentTheme, createAppSDKTheme } from '../odooTokens';

// Default context value (used before provider mounts)
const defaultContextValue: UseOdooTokensResult = {
  tokens: defaultTokens,
  fluentTheme: createFluentTheme(defaultTokens),
  appSDKTheme: createAppSDKTheme(defaultTokens),
  loading: true,
  error: null,
  refetch: async () => {},
};

const OdooTokensContext = createContext<UseOdooTokensResult>(defaultContextValue);

export interface OdooTokensProviderProps extends UseOdooTokensOptions {
  children: ReactNode;
  /** Optional fallback while loading */
  loadingFallback?: ReactNode;
  /** Optional error fallback */
  errorFallback?: ReactNode | ((error: Error) => ReactNode);
}

export function OdooTokensProvider({
  children,
  loadingFallback,
  errorFallback,
  ...options
}: OdooTokensProviderProps) {
  const tokensResult = useOdooTokens(options);

  // Show loading fallback
  if (tokensResult.loading && loadingFallback) {
    return <>{loadingFallback}</>;
  }

  // Show error fallback
  if (tokensResult.error && errorFallback) {
    if (typeof errorFallback === 'function') {
      return <>{errorFallback(tokensResult.error)}</>;
    }
    return <>{errorFallback}</>;
  }

  return (
    <OdooTokensContext.Provider value={tokensResult}>
      {children}
    </OdooTokensContext.Provider>
  );
}

/**
 * Hook to access Odoo tokens from context
 */
export function useOdooTokensContext(): UseOdooTokensResult {
  const context = useContext(OdooTokensContext);
  if (!context) {
    throw new Error('useOdooTokensContext must be used within OdooTokensProvider');
  }
  return context;
}

export default OdooTokensProvider;

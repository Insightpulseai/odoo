/**
 * React Hook for Odoo Brand Tokens
 * =================================
 *
 * Usage:
 * ```tsx
 * import { useOdooTokens } from '@ipai/design-tokens/react/useOdooTokens';
 *
 * function App() {
 *   const { tokens, fluentTheme, loading, error } = useOdooTokens({
 *     baseUrl: 'https://erp.insightpulseai.net',
 *     companyId: 1,
 *   });
 *
 *   if (loading) return <Spinner />;
 *
 *   return (
 *     <FluentProvider theme={fluentTheme}>
 *       <YourApp />
 *     </FluentProvider>
 *   );
 * }
 * ```
 */

import { useState, useEffect, useMemo } from 'react';
import {
  OdooTokens,
  defaultTokens,
  fetchOdooTokens,
  createFluentTheme,
  createAppSDKTheme,
  applyTokensToDocument,
} from '../odooTokens';

export interface UseOdooTokensOptions {
  /** Base URL of the Odoo instance */
  baseUrl: string;
  /** Optional company ID (defaults to current company) */
  companyId?: number;
  /** Apply tokens as CSS variables to document (default: true) */
  applyToDocument?: boolean;
  /** Refresh interval in ms (default: 300000 = 5 min) */
  refreshInterval?: number;
}

export interface UseOdooTokensResult {
  /** Raw tokens from Odoo */
  tokens: OdooTokens;
  /** Fluent UI v9 theme object */
  fluentTheme: ReturnType<typeof createFluentTheme>;
  /** ChatGPT App SDK theme object */
  appSDKTheme: ReturnType<typeof createAppSDKTheme>;
  /** Loading state */
  loading: boolean;
  /** Error if fetch failed */
  error: Error | null;
  /** Manually refetch tokens */
  refetch: () => Promise<void>;
}

export function useOdooTokens(options: UseOdooTokensOptions): UseOdooTokensResult {
  const {
    baseUrl,
    companyId,
    applyToDocument = true,
    refreshInterval = 300000,
  } = options;

  const [tokens, setTokens] = useState<OdooTokens>(defaultTokens);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTokensHandler = async () => {
    try {
      setLoading(true);
      setError(null);
      const newTokens = await fetchOdooTokens(baseUrl, companyId);
      setTokens(newTokens);

      if (applyToDocument) {
        applyTokensToDocument(newTokens);
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchTokensHandler();
  }, [baseUrl, companyId]);

  // Refresh interval
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchTokensHandler, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [baseUrl, companyId, refreshInterval]);

  // Memoized theme objects
  const fluentTheme = useMemo(() => createFluentTheme(tokens), [tokens]);
  const appSDKTheme = useMemo(() => createAppSDKTheme(tokens), [tokens]);

  return {
    tokens,
    fluentTheme,
    appSDKTheme,
    loading,
    error,
    refetch: fetchTokensHandler,
  };
}

export default useOdooTokens;

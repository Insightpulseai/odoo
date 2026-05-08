'use client';

/**
 * Lightweight MSAL provider — no @azure/msal-react dependency to keep the
 * dependency surface small. Initialises the PublicClientApplication on
 * mount, exposes a hook for sign-in / sign-out / current account.
 *
 * If MSAL env is not configured, the provider is a no-op and the rest of
 * the app continues to work (demo mode + Odoo session passthrough).
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { AccountInfo, PublicClientApplication } from '@azure/msal-browser';

import { buildMsalConfig, defaultLoginRequest, readMsalEnv } from './msal-config';

interface MsalContextValue {
  enabled: boolean;
  ready: boolean;
  account: AccountInfo | null;
  signIn: () => Promise<void>;
  signOut: () => Promise<void>;
}

const MsalContext = createContext<MsalContextValue>({
  enabled: false,
  ready: false,
  account: null,
  signIn: async () => {
    /* no-op */
  },
  signOut: async () => {
    /* no-op */
  },
});

export function MsalProvider({ children }: { children: ReactNode }) {
  const env = useMemo(() => readMsalEnv(), []);
  const [pca, setPca] = useState<PublicClientApplication | null>(null);
  const [ready, setReady] = useState(false);
  const [account, setAccount] = useState<AccountInfo | null>(null);

  useEffect(() => {
    if (!env.enabled) {
      setReady(true);
      return;
    }

    let cancelled = false;
    void (async () => {
      try {
        const { PublicClientApplication } = await import('@azure/msal-browser');
        const config = buildMsalConfig(env);
        if (!config) {
          setReady(true);
          return;
        }

        const instance = new PublicClientApplication(config);
        await instance.initialize();
        await instance.handleRedirectPromise();

        const accounts = instance.getAllAccounts();
        if (!cancelled) {
          setPca(instance);
          setAccount(accounts[0] ?? null);
          setReady(true);
        }
      } catch (err) {
        console.error('[msal] init failed', err);
        if (!cancelled) setReady(true);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [env]);

  const signIn = useCallback(async () => {
    if (!pca) return;
    try {
      const result = await pca.loginPopup(defaultLoginRequest);
      if (result?.account) setAccount(result.account);
    } catch (err) {
      console.error('[msal] login failed', err);
    }
  }, [pca]);

  const signOut = useCallback(async () => {
    if (!pca || !account) return;
    try {
      await pca.logoutPopup({ account });
      setAccount(null);
    } catch (err) {
      console.error('[msal] logout failed', err);
    }
  }, [pca, account]);

  const value = useMemo<MsalContextValue>(
    () => ({ enabled: env.enabled, ready, account, signIn, signOut }),
    [env.enabled, ready, account, signIn, signOut],
  );

  return <MsalContext.Provider value={value}>{children}</MsalContext.Provider>;
}

export function useMsal(): MsalContextValue {
  return useContext(MsalContext);
}

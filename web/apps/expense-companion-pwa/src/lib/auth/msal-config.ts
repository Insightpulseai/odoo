/**
 * MSAL.js (browser) config for Entra ID single-sign-on.
 *
 * Designed to share the same Entra app registration as the Odoo deployment
 * so users get one OAuth session across both surfaces. The actual client_id
 * + tenant_id are injected via env vars; this file never embeds them.
 *
 * Required env (set at build/deploy time):
 *   NEXT_PUBLIC_ENTRA_TENANT_ID
 *   NEXT_PUBLIC_ENTRA_CLIENT_ID
 *   NEXT_PUBLIC_ENTRA_REDIRECT_URI  (e.g. https://expense.insightpulseai.com/auth/callback)
 *
 * If any are missing, MSAL is disabled and the app falls back to anonymous
 * mode (still functional in demo mode against Odoo public endpoints).
 */

import type { Configuration } from '@azure/msal-browser';

export interface MsalEnv {
  tenantId: string | null;
  clientId: string | null;
  redirectUri: string | null;
  enabled: boolean;
}

export function readMsalEnv(): MsalEnv {
  const tenantId = process.env.NEXT_PUBLIC_ENTRA_TENANT_ID || null;
  const clientId = process.env.NEXT_PUBLIC_ENTRA_CLIENT_ID || null;
  const redirectUri =
    process.env.NEXT_PUBLIC_ENTRA_REDIRECT_URI ||
    (typeof window !== 'undefined' ? `${window.location.origin}/` : null);

  return {
    tenantId,
    clientId,
    redirectUri,
    enabled: Boolean(tenantId && clientId && redirectUri),
  };
}

export function buildMsalConfig(env: MsalEnv): Configuration | null {
  if (!env.enabled || !env.tenantId || !env.clientId || !env.redirectUri) {
    return null;
  }

  return {
    auth: {
      clientId: env.clientId,
      authority: `https://login.microsoftonline.com/${env.tenantId}`,
      redirectUri: env.redirectUri,
      postLogoutRedirectUri: env.redirectUri,
      navigateToLoginRequestUrl: true,
    },
    cache: {
      cacheLocation: 'localStorage',
      storeAuthStateInCookie: false,
    },
  };
}

// Default scopes — User.Read for the user profile.
// Add Odoo-specific scopes (e.g. api://<odoo-client-id>/expense.write)
// if/when the Odoo app exposes a scoped API surface.
export const defaultLoginRequest = {
  scopes: ['User.Read', 'openid', 'profile', 'email'],
};

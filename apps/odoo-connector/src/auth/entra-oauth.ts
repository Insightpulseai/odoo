/**
 * Entra OAuth — Token validation and scope extraction for the Odoo connector.
 *
 * Flow:
 *   ChatGPT → OAuth authorize → login.microsoftonline.com → redirect with code
 *   → connector exchanges code for token → validates token → extracts scopes
 *   → connector calls Odoo JSON-2 with bot service credentials
 *
 * The user's Entra identity determines WHICH scopes they have.
 * The Odoo API call always uses the bot user's bearer key.
 */

export interface EntraOAuthConfig {
  tenantId: string;
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  issuer: string;
  jwksUri: string;
  scopes: string[];
}

export interface TokenClaims {
  sub: string;
  oid: string;
  preferred_username?: string;
  email?: string;
  name?: string;
  scp?: string;
  roles?: string[];
  iss: string;
  aud: string;
  exp: number;
  iat: number;
}

export interface AuthenticatedUser {
  id: string;
  email: string;
  name: string;
  scopes: string[];
}

export function buildEntraConfig(overrides?: Partial<EntraOAuthConfig>): EntraOAuthConfig {
  const tenantId = overrides?.tenantId ?? requireEnv("ENTRA_TENANT_ID");
  const clientId = overrides?.clientId ?? requireEnv("ENTRA_CLIENT_ID");

  return {
    tenantId,
    clientId,
    clientSecret: overrides?.clientSecret ?? requireEnv("ENTRA_CLIENT_SECRET"),
    redirectUri: overrides?.redirectUri ?? requireEnv("ENTRA_REDIRECT_URI"),
    issuer: `https://login.microsoftonline.com/${tenantId}/v2.0`,
    jwksUri: `https://login.microsoftonline.com/${tenantId}/discovery/v2.0/keys`,
    scopes: overrides?.scopes ?? ["openid", "profile", "email"],
  };
}

/**
 * Build the authorization URL for the Entra OAuth flow.
 */
export function buildAuthorizationUrl(
  config: EntraOAuthConfig,
  state: string,
  requestedScopes?: string[],
): string {
  const scopes = requestedScopes ?? config.scopes;
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: "code",
    redirect_uri: config.redirectUri,
    scope: scopes.join(" "),
    state,
    response_mode: "query",
  });

  return `https://login.microsoftonline.com/${config.tenantId}/oauth2/v2.0/authorize?${params}`;
}

/**
 * Exchange an authorization code for tokens.
 */
export async function exchangeCodeForTokens(
  config: EntraOAuthConfig,
  code: string,
): Promise<{ accessToken: string; idToken?: string; expiresIn: number }> {
  const body = new URLSearchParams({
    client_id: config.clientId,
    client_secret: config.clientSecret,
    code,
    redirect_uri: config.redirectUri,
    grant_type: "authorization_code",
    scope: config.scopes.join(" "),
  });

  const res = await fetch(
    `https://login.microsoftonline.com/${config.tenantId}/oauth2/v2.0/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    },
  );

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Entra token exchange failed: ${res.status} ${text}`);
  }

  const data = (await res.json()) as {
    access_token: string;
    id_token?: string;
    expires_in: number;
  };

  return {
    accessToken: data.access_token,
    idToken: data.id_token,
    expiresIn: data.expires_in,
  };
}

/**
 * Validate an access token and extract claims.
 *
 * For production: use a proper JWT library with JWKS validation.
 * This implementation decodes the payload for scope extraction
 * and validates basic claims (issuer, audience, expiry).
 */
export function validateToken(
  config: EntraOAuthConfig,
  accessToken: string,
): TokenClaims | null {
  try {
    const parts = accessToken.split(".");
    if (parts.length !== 3) return null;

    const payload = JSON.parse(
      Buffer.from(parts[1], "base64url").toString("utf8"),
    ) as TokenClaims;

    // Validate issuer
    if (payload.iss !== config.issuer) {
      console.error(`Token issuer mismatch: ${payload.iss} !== ${config.issuer}`);
      return null;
    }

    // Validate audience
    if (payload.aud !== config.clientId) {
      console.error(`Token audience mismatch: ${payload.aud} !== ${config.clientId}`);
      return null;
    }

    // Validate expiry
    if (payload.exp * 1000 < Date.now()) {
      console.error("Token expired");
      return null;
    }

    return payload;
  } catch (err) {
    console.error("Token validation error:", err);
    return null;
  }
}

/**
 * Extract connector-level scopes from token claims.
 *
 * Maps Entra delegated scopes (scp claim) to connector feature-group scopes.
 * If no explicit odoo.* scopes are present, grants the default analyst preset.
 */
export function extractConnectorScopes(claims: TokenClaims): string[] {
  const entryScopes: string[] = [];

  // Delegated scopes from scp claim (space-separated)
  if (claims.scp) {
    entryScopes.push(...claims.scp.split(" "));
  }

  // Application roles from roles claim
  if (claims.roles) {
    entryScopes.push(...claims.roles);
  }

  // Filter to odoo.* scopes only
  const odooScopes = entryScopes.filter((s) => s.startsWith("odoo."));

  // If no explicit odoo.* scopes, grant default analyst read-only preset
  if (odooScopes.length === 0) {
    return [
      "odoo.contacts.records.read",
      "odoo.crm.leads.read",
      "odoo.sales.orders.read",
      "odoo.finance.invoices.read",
      "odoo.projects.projects.read",
      "odoo.projects.tasks.read",
      "odoo.reporting.kpis.read",
      "odoo.cms.pages.read",
      "odoo.cms.seo.read",
      "odoo.admin.debug.read",
    ];
  }

  return odooScopes;
}

/**
 * Build an AuthenticatedUser from validated token claims.
 */
export function buildAuthenticatedUser(claims: TokenClaims): AuthenticatedUser {
  return {
    id: claims.oid || claims.sub,
    email: claims.email || claims.preferred_username || "",
    name: claims.name || "",
    scopes: extractConnectorScopes(claims),
  };
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
}

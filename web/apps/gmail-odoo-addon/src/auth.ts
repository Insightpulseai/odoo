/**
 * InsightPulseAI Gmail Add-on — Authentication
 *
 * Provider-first auth flow: Microsoft Entra > Google OAuth > API key fallback.
 * Credentials are stored in per-user script properties (never shared).
 *
 * Auth model:
 *   Add-on click  → /web/login (Odoo login page with native OAuth buttons)
 *   Provider login → Microsoft / Google
 *   Provider return → /auth_oauth/signin (Odoo callback — NEVER opened by add-on)
 *   Session exchange → /ipai/mail_plugin/provider_session
 *
 * The Gmail account is the mailbox host surface only.
 * The ERP sign-in identity may use a different provider.
 */

// ---------------------------------------------------------------------------
// Session management
// ---------------------------------------------------------------------------

/**
 * Retrieve or refresh a valid Odoo session token.
 * Returns the token string or null if not authenticated.
 */
function getOdooSession(): string | null {
  const props = PropertiesService.getUserProperties();
  const token = props.getProperty("odoo_session_token");
  const expiresAt = props.getProperty("odoo_session_expires");

  if (token && expiresAt) {
    const expiry = new Date(expiresAt);
    if (expiry > new Date()) {
      return token;
    }
  }

  // Only re-authenticate automatically for API key sessions.
  // Provider-based sessions require explicit browser re-auth.
  const storedProvider = props.getProperty("odoo_auth_provider");
  if (storedProvider && storedProvider !== "local_odoo") {
    return null;
  }

  const email = props.getProperty("odoo_email");
  const apiKey = props.getProperty("odoo_api_key");

  if (!email || !apiKey) {
    return null;
  }

  return connectWithApiKey(email, apiKey);
}

/**
 * Return a summary of the current session state.
 */
function getSessionSummary(): SessionSummary {
  const props = PropertiesService.getUserProperties();
  const token = props.getProperty("odoo_session_token");
  const expiresAt = props.getProperty("odoo_session_expires");
  const provider = props.getProperty("odoo_auth_provider") as OdooAuthProvider | null;
  const userEmail = props.getProperty("odoo_email");

  const connected = !!token && !!expiresAt && new Date(expiresAt) > new Date();

  return {
    connected,
    provider: connected ? provider : null,
    userEmail: connected ? userEmail : null,
    tenantId: TENANT_CONFIG.tenantId,
    tenantDisplayName: TENANT_CONFIG.displayName,
    expiresAt: connected ? expiresAt : null,
  };
}

/**
 * Clear all stored session data.
 */
function clearSession(): void {
  const props = PropertiesService.getUserProperties();
  props.deleteProperty("odoo_session_token");
  props.deleteProperty("odoo_session_expires");
  props.deleteProperty("odoo_auth_provider");
  props.deleteProperty("odoo_email");
  props.deleteProperty("odoo_api_key");
  props.deleteProperty("odoo_auth_state");
  props.deleteProperty("odoo_auth_state_expires");
}

// ---------------------------------------------------------------------------
// Auth state nonce (replay/CSRF protection)
// ---------------------------------------------------------------------------

/**
 * Generate and store a nonce binding the auth attempt to this tenant+provider.
 * The nonce is single-use and expires after AUTH_STATE_TTL_MS.
 */
function buildAuthStateNonce(tenant: TenantConfig, provider: OdooAuthProvider): string {
  const nonce = Utilities.getUuid();
  const state = JSON.stringify({
    nonce,
    tenantId: tenant.tenantId,
    provider,
    ts: Date.now(),
  });

  const props = PropertiesService.getUserProperties();
  props.setProperty("odoo_auth_state", state);
  props.setProperty("odoo_auth_state_expires", String(Date.now() + AUTH_STATE_TTL_MS));

  return nonce;
}

/**
 * Verify that the returned state matches the stored nonce.
 * Consumes the nonce (single-use). Returns the provider if valid, null otherwise.
 */
function verifyAuthStateNonce(returnedNonce: string): OdooAuthProvider | null {
  const props = PropertiesService.getUserProperties();
  const raw = props.getProperty("odoo_auth_state");
  const expiresStr = props.getProperty("odoo_auth_state_expires");

  // Always consume — single use
  props.deleteProperty("odoo_auth_state");
  props.deleteProperty("odoo_auth_state_expires");

  if (!raw || !expiresStr) {
    return null;
  }

  const expires = parseInt(expiresStr, 10);
  if (Date.now() > expires) {
    Logger.log("Auth state nonce expired");
    return null;
  }

  try {
    const stored = JSON.parse(raw);
    if (stored.nonce !== returnedNonce) {
      Logger.log("Auth state nonce mismatch");
      return null;
    }
    if (stored.tenantId !== TENANT_CONFIG.tenantId) {
      Logger.log("Auth state tenant mismatch");
      return null;
    }
    return stored.provider as OdooAuthProvider;
  } catch {
    Logger.log("Auth state parse error");
    return null;
  }
}

/**
 * Check whether a provider is valid for the current tenant.
 */
function validateProviderForTenant(provider: OdooAuthProvider, tenant: TenantConfig): boolean {
  return tenant.authProviders.includes(provider);
}

// ---------------------------------------------------------------------------
// Provider auth flow
// ---------------------------------------------------------------------------

/**
 * Start provider-based auth by opening the Odoo login page.
 *
 * IMPORTANT: This opens /web/login — NOT /auth_oauth/signin.
 *   /web/login renders the OAuth provider buttons natively (Google, Microsoft).
 *   /auth_oauth/signin is the CALLBACK endpoint that providers redirect back to.
 *   The add-on must NEVER open /auth_oauth/signin directly.
 *
 * The user authenticates in a browser tab via Odoo's native login flow.
 * After successful login, the add-on sidebar reloads (OnClose.RELOAD_ADD_ON).
 */
function startProviderAuth(
  e: GoogleAppsScript.Addons.EventObject
): GoogleAppsScript.Card_Service.ActionResponse {
  const params = e.commonEventObject.parameters || {};
  const provider = (params.provider || TENANT_CONFIG.defaultAuthProvider) as OdooAuthProvider;

  if (!validateProviderForTenant(provider, TENANT_CONFIG)) {
    return pushCard(errorLoginCard("This sign-in method is not available for your ERP tenant."));
  }

  if (provider === "local_odoo") {
    return showApiKeyForm();
  }

  // Open the Odoo login page — NOT the OAuth callback endpoint.
  // /auth_oauth/signin is only for provider redirects BACK to Odoo.
  // The login page renders OAuth provider buttons natively.
  const loginPath = PROVIDER_AUTH_PATHS[provider as Exclude<OdooAuthProvider, "local_odoo">] || "/web/login";
  const loginUrl = `${ODOO_BASE_URL}${loginPath}?redirect=%2Fweb`;

  return CardService.newActionResponseBuilder()
    .setOpenLink(
      CardService.newOpenLink()
        .setUrl(loginUrl)
        .setOpenAs(CardService.OpenAs.OVERLAY)
        .setOnClose(CardService.OnClose.RELOAD_ADD_ON)
    )
    .build();
}

/**
 * Exchange a provider callback payload for an add-on session token.
 * Validates the state nonce before accepting the code.
 */
function exchangeSessionToken(
  e: GoogleAppsScript.Addons.EventObject
): GoogleAppsScript.Card_Service.ActionResponse {
  const formInputs = e.commonEventObject.formInputs;
  const code = formInputs?.provider_code?.stringInputs?.value?.[0] || "";
  const returnedNonce = formInputs?.provider_nonce?.stringInputs?.value?.[0] || "";

  if (!code) {
    return pushCard(errorLoginCard("No authorization code provided."));
  }

  // Validate nonce if provided (state round-trip)
  if (returnedNonce) {
    const validProvider = verifyAuthStateNonce(returnedNonce);
    if (!validProvider) {
      return pushCard(authFailureCard(
        "The authorization link has expired or was already used. Please start sign-in again.",
        null
      ));
    }
  }

  const url = apiUrl(API_PATHS.providerSession);

  try {
    const response = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
          code,
          source: "gmail_addon",
          tenant_id: TENANT_CONFIG.tenantId,
        },
      }),
      muteHttpExceptions: true,
    });

    const status = response.getResponseCode();
    if (status !== 200) {
      Logger.log(`Provider session failed: HTTP ${status}`);
      return pushCard(authFailureCard(
        "Could not complete sign-in. The ERP server returned an error.",
        status === 401 || status === 403 ? "first_login" : null
      ));
    }

    const body = JSON.parse(response.getContentText());
    if (body.error) {
      Logger.log(`Provider session error: ${body.error.message}`);
      const hint = body.error.data?.hint || null;
      return pushCard(authFailureCard(
        "Authentication failed. " + (body.error.message || "Try again or use API key."),
        hint
      ));
    }

    const result = body.result;
    const props = PropertiesService.getUserProperties();
    props.setProperty("odoo_session_token", result.token);
    props.setProperty("odoo_session_expires", result.expires_at);
    props.setProperty("odoo_auth_provider", result.provider || "");
    if (result.user_email) {
      props.setProperty("odoo_email", result.user_email);
    }
    // Never persist API key for provider-based sessions
    props.deleteProperty("odoo_api_key");

    return pushCard(connectedCard(result.user_email || ""));
  } catch (err) {
    Logger.log(`Provider session exception: ${err}`);
    return pushCard(errorLoginCard("Connection error. Check your network and try again."));
  }
}

// ---------------------------------------------------------------------------
// API key auth (advanced/fallback only)
// ---------------------------------------------------------------------------

/**
 * Authenticate with email + API key (advanced/fallback only).
 */
function connectWithApiKey(email: string, apiKey: string): string | null {
  const url = apiUrl(API_PATHS.session);

  try {
    const response = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: { email, api_key: apiKey },
      }),
      muteHttpExceptions: true,
    });

    const status = response.getResponseCode();
    if (status !== 200) {
      Logger.log(`Auth failed: HTTP ${status}`);
      return null;
    }

    const body = JSON.parse(response.getContentText());
    if (body.error) {
      Logger.log(`Auth error: ${body.error.message}`);
      return null;
    }

    const result = body.result;
    const props = PropertiesService.getUserProperties();
    props.setProperty("odoo_session_token", result.token);
    props.setProperty("odoo_session_expires", result.expires_at);
    props.setProperty("odoo_email", email);
    props.setProperty("odoo_api_key", apiKey);
    props.setProperty("odoo_auth_provider", "local_odoo");

    return result.token;
  } catch (err) {
    Logger.log(`Auth exception: ${err}`);
    return null;
  }
}

/**
 * Handle API key login form submission.
 */
function handleLogin(e: GoogleAppsScript.Addons.EventObject): GoogleAppsScript.Card_Service.ActionResponse {
  const formInputs = e.commonEventObject.formInputs;
  const email = formInputs?.odoo_email?.stringInputs?.value?.[0] || "";
  const apiKey = formInputs?.odoo_api_key?.stringInputs?.value?.[0] || "";

  const token = connectWithApiKey(email, apiKey);

  if (token) {
    return pushCard(connectedCard(email));
  }

  return pushCard(authFailureCard(
    "Could not authenticate. Check your email and API key.",
    null
  ));
}

/**
 * Handle the "Complete sign-in" form after browser OAuth.
 */
function handleProviderCallback(
  e: GoogleAppsScript.Addons.EventObject
): GoogleAppsScript.Card_Service.ActionResponse {
  return exchangeSessionToken(e);
}

/**
 * Handle disconnect action.
 */
function handleDisconnect(
  _e: GoogleAppsScript.Addons.EventObject
): GoogleAppsScript.Card_Service.ActionResponse {
  clearSession();

  return CardService.newActionResponseBuilder()
    .setNavigation(
      CardService.newNavigation().updateCard(loginCard())
    )
    .build();
}

// ---------------------------------------------------------------------------
// Card builders
// ---------------------------------------------------------------------------

/**
 * Resolve the host Gmail address. Best-effort only — never blocks rendering.
 */
function getHostEmail(): string {
  try {
    const email = Session.getActiveUser().getEmail();
    return email || "Current Gmail account";
  } catch {
    return "Current Gmail account";
  }
}

/**
 * Render the tenant-aware provider-first login card.
 * API key is behind progressive disclosure, collapsed every render.
 */
function loginCard(): GoogleAppsScript.Card_Service.Card {
  const hostEmail = getHostEmail();

  const header = CardService.newCardHeader()
    .setTitle("InsightPulseAI ERP")
    .setSubtitle("Connect your Gmail workspace to the ERP tenant.");

  // Tenant info section
  const tenantSection = CardService.newCardSection()
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel("Host mailbox")
        .setText(hostEmail)
    )
    .addWidget(
      CardService.newKeyValue()
        .setTopLabel("ERP tenant")
        .setText(`${TENANT_CONFIG.displayName}\n${TENANT_CONFIG.odooBaseUrl.replace("https://", "")}`)
    )
    .addWidget(
      CardService.newTextParagraph().setText(
        "<i>Your Gmail account and ERP identity can be different.\nChoose how you sign in to the ERP tenant.</i>"
      )
    );

  // Provider buttons — strictly gated by TENANT_CONFIG.authProviders
  const oauthProviders = TENANT_CONFIG.authProviders.filter(
    (p): p is Exclude<OdooAuthProvider, "local_odoo"> => p !== "local_odoo"
  );

  const builder = CardService.newCardBuilder()
    .setHeader(header)
    .addSection(tenantSection);

  if (oauthProviders.length > 0) {
    const providerSection = CardService.newCardSection()
      .setHeader("Sign in to ERP");

    for (const provider of oauthProviders) {
      const isDefault = provider === TENANT_CONFIG.defaultAuthProvider;
      const label = isDefault
        ? `${PROVIDER_LABELS[provider]} (recommended)`
        : PROVIDER_LABELS[provider];

      const action = CardService.newAction()
        .setFunctionName("startProviderAuth")
        .setParameters({ provider });

      providerSection.addWidget(
        CardService.newTextButton()
          .setText(label)
          .setOnClickAction(action)
      );
    }

    builder.addSection(providerSection);

    // Provider callback section (paste code after browser auth)
    const callbackSection = CardService.newCardSection()
      .setHeader("Complete sign-in")
      .setCollapsible(true)
      .setNumUncollapsibleWidgets(0)
      .addWidget(
        CardService.newTextParagraph().setText(
          "After signing in via your browser, paste the authorization code below."
        )
      )
      .addWidget(
        CardService.newTextInput()
          .setFieldName("provider_code")
          .setTitle("Authorization code")
          .setHint("Paste the code shown after sign-in")
      )
      .addWidget(
        CardService.newTextInput()
          .setFieldName("provider_nonce")
          .setTitle("State")
          .setHint("Paste the state value if shown")
      )
      .addWidget(
        CardService.newTextButton()
          .setText("Complete sign-in")
          .setOnClickAction(
            CardService.newAction().setFunctionName("handleProviderCallback")
          )
      );

    builder.addSection(callbackSection);
  }

  // Advanced: API key fallback — always collapsed, never sticky
  if (TENANT_CONFIG.authProviders.includes("local_odoo")) {
    const advancedSection = CardService.newCardSection()
      .setHeader("Advanced connection")
      .setCollapsible(true)
      .setNumUncollapsibleWidgets(0)
      .addWidget(
        CardService.newTextParagraph().setText(
          "Use ERP email + API key only for fallback, service, or admin scenarios."
        )
      )
      .addWidget(
        CardService.newTextInput()
          .setFieldName("odoo_email")
          .setTitle("ERP Email")
          .setHint("Your Odoo login email")
      )
      .addWidget(
        CardService.newTextInput()
          .setFieldName("odoo_api_key")
          .setTitle("API Key")
          .setHint("Odoo user API key")
      )
      .addWidget(
        CardService.newTextButton()
          .setText("Connect with API Key")
          .setOnClickAction(
            CardService.newAction().setFunctionName("handleLogin")
          )
      );

    builder.addSection(advancedSection);
  }

  return builder.build();
}

/**
 * Show the API key form directly (when provider === local_odoo via button).
 */
function showApiKeyForm(): GoogleAppsScript.Card_Service.ActionResponse {
  const card = CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader()
        .setTitle("InsightPulseAI ERP")
        .setSubtitle("Advanced connection")
    )
    .addSection(
      CardService.newCardSection()
        .addWidget(
          CardService.newTextParagraph().setText(
            "Use ERP email + API key for fallback, service, or admin access."
          )
        )
        .addWidget(
          CardService.newTextInput()
            .setFieldName("odoo_email")
            .setTitle("ERP Email")
            .setHint("Your Odoo login email")
        )
        .addWidget(
          CardService.newTextInput()
            .setFieldName("odoo_api_key")
            .setTitle("API Key")
            .setHint("Odoo user API key")
        )
        .addWidget(
          CardService.newTextButton()
            .setText("Connect")
            .setOnClickAction(
              CardService.newAction().setFunctionName("handleLogin")
            )
        )
    )
    .build();

  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card))
    .build();
}

/**
 * Success card shown after authentication.
 */
function connectedCard(userEmail: string): GoogleAppsScript.Card_Service.Card {
  const summary = getSessionSummary();
  const providerName = summary.provider
    ? PROVIDER_DISPLAY_NAMES[summary.provider]
    : "unknown method";

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("Connected"))
    .addSection(
      CardService.newCardSection()
        .addWidget(
          CardService.newTextParagraph().setText(
            `Connected to ${TENANT_CONFIG.displayName}.${userEmail ? `\nSigned in as ${userEmail}` : ""}\nMethod: ${providerName}`
          )
        )
    )
    .build();
}

/**
 * Auth failure card with optional first-login / provider-specific help.
 *
 * Hints:
 *   "first_login"  — account may need linking to provider
 *   "google_link"  — Google-specific linking failure
 */
function authFailureCard(message: string, hint: string | null): GoogleAppsScript.Card_Service.Card {
  const section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText(message));

  if (hint === "first_login" || hint === "google_link") {
    section.addWidget(
      CardService.newTextParagraph().setText(
        "<i>If this is your first time connecting, your ERP account may need to be linked " +
        "to your identity provider. Contact your administrator or check your ERP invitation email.\n\n" +
        "For Google: existing ERP users may need to use the Reset Password page first, " +
        "or an admin must enable Google sign-in for your account.</i>"
      )
    );

    // Offer alternative auth paths on provider failure
    section.addWidget(
      CardService.newTextButton()
        .setText("Continue with Microsoft")
        .setOnClickAction(
          CardService.newAction()
            .setFunctionName("startProviderAuth")
            .setParameters({ provider: "microsoft_entra_oauth" })
        )
    );

    section.addWidget(
      CardService.newTextButton()
        .setText("Open ERP login page")
        .setOpenLink(
          CardService.newOpenLink().setUrl(`${ODOO_BASE_URL}/web/login`)
        )
    );
  }

  section.addWidget(
    CardService.newTextButton()
      .setText("Try again")
      .setOnClickAction(
        CardService.newAction().setFunctionName("reloadLoginCard")
      )
  );

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("Sign-in failed"))
    .addSection(section)
    .build();
}

/**
 * Error card for login failures (simple variant).
 */
function errorLoginCard(message: string): GoogleAppsScript.Card_Service.Card {
  return authFailureCard(message, null);
}

/**
 * Reload the login card (used from error/retry buttons).
 */
function reloadLoginCard(
  _e: GoogleAppsScript.Addons.EventObject
): GoogleAppsScript.Card_Service.ActionResponse {
  return CardService.newActionResponseBuilder()
    .setNavigation(
      CardService.newNavigation().updateCard(loginCard())
    )
    .build();
}

/**
 * Helper: push a card via ActionResponse.
 */
function pushCard(
  card: GoogleAppsScript.Card_Service.Card
): GoogleAppsScript.Card_Service.ActionResponse {
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card))
    .build();
}

// ---------------------------------------------------------------------------
// Bridge
// ---------------------------------------------------------------------------

/**
 * Make an authenticated POST request to the Odoo bridge.
 */
function fetchBridge(path: string, params: Record<string, unknown>): Record<string, unknown> | null {
  const token = getOdooSession();
  if (!token) {
    return null;
  }

  const url = apiUrl(path);

  try {
    const response = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      payload: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params,
      }),
      muteHttpExceptions: true,
    });

    const status = response.getResponseCode();
    if (status !== 200) {
      Logger.log(`Bridge ${path} failed: HTTP ${status}`);
      return null;
    }

    const body = JSON.parse(response.getContentText());
    if (body.error) {
      Logger.log(`Bridge ${path} error: ${body.error.message}`);
      return null;
    }

    return body.result;
  } catch (err) {
    Logger.log(`Bridge ${path} exception: ${err}`);
    return null;
  }
}

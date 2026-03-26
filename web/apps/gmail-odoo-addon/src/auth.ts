/**
 * InsightPulseAI Gmail Add-on — Authentication
 *
 * Manages session tokens with the Odoo bridge.
 * Credentials are stored in per-user script properties (never shared).
 */

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

  // Attempt to re-authenticate with stored credentials
  const email = props.getProperty("odoo_email");
  const apiKey = props.getProperty("odoo_api_key");

  if (!email || !apiKey) {
    return null;
  }

  return authenticate(email, apiKey);
}

/**
 * Authenticate against the Odoo bridge and store the session token.
 */
function authenticate(email: string, apiKey: string): string | null {
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

    return result.token;
  } catch (err) {
    Logger.log(`Auth exception: ${err}`);
    return null;
  }
}

/**
 * Handle login form submission.
 */
function handleLogin(e: GoogleAppsScript.Addons.EventObject): GoogleAppsScript.Card_Service.ActionResponse {
  const formInputs = e.commonEventObject.formInputs;
  const email = formInputs?.odoo_email?.stringInputs?.value?.[0] || "";
  const apiKey = formInputs?.odoo_api_key?.stringInputs?.value?.[0] || "";

  const token = authenticate(email, apiKey);

  if (token) {
    const card = CardService.newCardBuilder()
      .setHeader(CardService.newCardHeader().setTitle("Connected"))
      .addSection(
        CardService.newCardSection().addWidget(
          CardService.newTextParagraph().setText(
            "Successfully connected to InsightPulseAI ERP."
          )
        )
      )
      .build();

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().pushCard(card))
      .build();
  }

  const card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle("Login Failed"))
    .addSection(
      CardService.newCardSection().addWidget(
        CardService.newTextParagraph().setText(
          "Could not authenticate. Check your email and API key."
        )
      )
    )
    .build();

  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().pushCard(card))
    .build();
}

/**
 * Render a login card for unauthenticated users.
 */
function loginCard(): GoogleAppsScript.Card_Service.Card {
  const emailInput = CardService.newTextInput()
    .setFieldName("odoo_email")
    .setTitle("Email")
    .setHint("Your Odoo login email");

  const apiKeyInput = CardService.newTextInput()
    .setFieldName("odoo_api_key")
    .setTitle("API Key")
    .setHint("Odoo user API key");

  const loginAction = CardService.newAction().setFunctionName("handleLogin");

  const loginButton = CardService.newTextButton()
    .setText("Connect")
    .setOnClickAction(loginAction);

  const section = CardService.newCardSection()
    .setHeader("Connect to InsightPulseAI ERP")
    .addWidget(emailInput)
    .addWidget(apiKeyInput)
    .addWidget(loginButton);

  return CardService.newCardBuilder()
    .setHeader(
      CardService.newCardHeader().setTitle("InsightPulseAI").setSubtitle("Sign in to continue")
    )
    .addSection(section)
    .build();
}

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

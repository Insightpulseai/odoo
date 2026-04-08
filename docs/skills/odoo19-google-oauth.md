# Odoo 19 Google OAuth Authentication -- Deep Reference

> Comprehensive technical reference for configuring Google Sign-In on Odoo 19 CE.
> Context: InsightPulseAI Gmail add-on connecting to `erp.insightpulseai.com`.
> Google OAuth is secondary auth provider (Microsoft Entra is primary).

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Google Cloud Console Setup](#2-google-cloud-console-setup)
3. [Odoo-Side Configuration](#3-odoo-side-configuration)
4. [User Flows](#4-user-flows)
5. [Login Page Behavior](#5-login-page-behavior)
6. [CE vs Enterprise](#6-ce-vs-enterprise)
7. [Gmail Add-On Integration](#7-gmail-add-on-integration)
8. [Security and Troubleshooting](#8-security-and-troubleshooting)
9. [Comparison: Google vs Microsoft OAuth in Odoo](#9-comparison-google-vs-microsoft-oauth-in-odoo)
10. [Exact Configuration for InsightPulseAI](#10-exact-configuration-for-insightpulseai)
11. [Known Issues and Limitations](#11-known-issues-and-limitations)
12. [Sources](#12-sources)

---

## 1. Architecture Overview

### OAuth Flow Type

Odoo 19's `auth_oauth` module uses the **OAuth 2.0 Implicit Flow** (`response_type=token`). This is a deliberate (though debated) design choice in Odoo's codebase. The access token is returned directly in the URL fragment after the user authenticates with Google.

**Flow sequence:**

```
User clicks "Log in with Google" on /web/login
  --> Browser redirects to Google's auth endpoint
      https://accounts.google.com/o/oauth2/auth
      ?response_type=token
      &client_id=<YOUR_CLIENT_ID>
      &redirect_uri=https://erp.insightpulseai.com/auth_oauth/signin
      &scope=openid+profile+email
      &state=<JSON_STATE>
  --> User authenticates with Google
  --> Google redirects to /auth_oauth/signin#access_token=<TOKEN>&...
  --> Odoo's fragment_to_query_string JS converts hash to query params
  --> Odoo controller validates token against Google's userinfo endpoint
  --> Odoo creates/finds user, establishes session
  --> User is redirected to /odoo (or target URL)
```

**Key implication:** Because Odoo uses implicit flow, it only needs the **Client ID** from Google. The **Client Secret is not used** for user authentication (unlike Gmail SMTP OAuth, which uses authorization code flow and requires both Client ID and Client Secret).

### Module Structure

The `auth_oauth` module lives in `addons/auth_oauth/` in the Odoo CE codebase. It is a **CE module** (not Enterprise-only). Key files:

| File | Purpose |
|------|---------|
| `__manifest__.py` | Module metadata. Depends on: `base`, `web`, `base_setup`, `auth_signup` |
| `data/auth_oauth_data.xml` | Pre-configured providers: Odoo.com, Facebook, **Google OAuth2** |
| `models/auth_oauth.py` | `auth.oauth.provider` model (provider configuration) |
| `models/res_users.py` | User model extension with OAuth fields |
| `models/res_config_settings.py` | Settings integration (Google-specific fields) |
| `controllers/main.py` | `/auth_oauth/signin` endpoint and login page extension |
| `views/auth_oauth_views.xml` | Provider list/form views |
| `views/res_config_settings_views.xml` | Settings UI for Google auth |
| `views/auth_oauth_templates.xml` | Login page button template |

### Pre-Configured Google Provider Record

Odoo ships with a Google OAuth2 provider record (`auth_oauth.provider_google`) with these defaults:

```xml
<record id="provider_google" model="auth.oauth.provider">
    <field name="name">Google OAuth2</field>
    <field name="auth_endpoint">https://accounts.google.com/o/oauth2/auth</field>
    <field name="scope">openid profile email</field>
    <field name="validation_endpoint">https://www.googleapis.com/oauth2/v3/userinfo</field>
    <field name="css_class">o_auth_oauth_provider_icon o_google_provider</field>
    <field name="body">Sign in with Google</field>
    <!-- enabled and client_id are NOT set by default -->
</record>
```

The provider is **disabled by default** and has **no Client ID** -- you must configure both in Settings.

---

## 2. Google Cloud Console Setup

### 2.1 Project Setup

1. Go to the [Google API Dashboard](https://console.developers.google.com/).
2. Select an existing project or click **Create Project**.
3. Fill out the project name (e.g., `InsightPulseAI Odoo`) and organization.
4. Click **Create**.

**Tip from Odoo docs:** Choose the company name from the dropdown if using Google Workspace.

### 2.2 OAuth Consent Screen

1. In the left menu, click **OAuth consent screen**.
2. Choose user type:

| User Type | When to Use | Limitations |
|-----------|-------------|-------------|
| **Internal** | Google Workspace organization only. Users must be in the same GWS domain. | Only available for Google Workspace accounts. No Google approval needed. |
| **External** | Personal Gmail accounts or users outside your GWS org. | Requires Google approval for production. **Testing mode limited to 100 test users.** |

**For InsightPulseAI:** If the Gmail add-on users are within a Google Workspace domain (e.g., `w9studio.net`), use **Internal**. If mixed or personal accounts, use **External** (start in testing mode, publish later).

3. Fill out required fields:
   - **App name**: `InsightPulseAI Odoo Login`
   - **User support email**: admin email
   - **App logo**: optional
   - **Authorized domains**: `insightpulseai.com`
   - **Developer contact email**: admin email

4. Click **Save and Continue**.

5. **Scopes page**: Leave as-is (Odoo uses `openid profile email` scopes, which are non-sensitive and do not require verification). Click **Save and Continue**.

6. **Test users** (External only): Add email addresses of users who will test before publishing. Click **Add Users**, then **Save and Continue**.

7. Click **Back to Dashboard**.

### 2.3 OAuth 2.0 Client ID (Credentials)

1. In the left menu, click **Credentials**.
2. Click **Create Credentials** --> **OAuth client ID**.
3. Select **Web Application** as the Application Type.

**Critical fields:**

| Field | Value |
|-------|-------|
| **Name** | `Odoo ERP Login` (or any descriptive name) |
| **Authorized JavaScript origins** | `https://erp.insightpulseai.com` |
| **Authorized redirect URIs** | `https://erp.insightpulseai.com/auth_oauth/signin` |

4. Click **Create**.

5. A dialog appears with **Client ID** and **Client Secret**. **Copy the Client ID** -- you will need it for Odoo configuration. The Client Secret is **not needed** for Odoo sign-in (implicit flow).

**Client ID format:** `<numbers>-<hash>.apps.googleusercontent.com`

### 2.4 Verification Requirements

| Mode | Approval | User Limit | Use Case |
|------|----------|------------|----------|
| **Testing** | None needed | 100 test users (must be explicitly added) | Development, staging |
| **Production (Internal)** | None needed (auto-approved for GWS org) | All org users | Google Workspace orgs |
| **Production (External)** | Google verification required | Unlimited | Public-facing apps |

For `openid`, `profile`, `email` scopes only, Google verification is typically quick (non-sensitive scopes). However, if the app requests no sensitive/restricted scopes, it may not need full verification even in production mode.

---

## 3. Odoo-Side Configuration

### 3.1 Enable OAuth Authentication Module

1. Navigate to **Settings** --> **General Settings** --> **Integrations**.
2. Enable the **OAuth Authentication** checkbox. This installs/enables the `auth_oauth` module.
3. Click **Save**.

**Note from Odoo docs:** Odoo may prompt the user to log in again after this step (module install triggers a server restart).

### 3.2 Enable Google Authentication

1. Return to **Settings** --> **General Settings** --> **Integrations**.
2. Under **OAuth Authentication**, find the **Google Authentication** section.
3. Enable it.
4. Enter the **Client ID** from the Google Cloud Console into the `Client ID` field.
   - Placeholder text: `e.g. 1234-xyz.apps.googleusercontent.com`
5. Click **Save**.

The settings UI also displays the **Server URI** (read-only), which shows the redirect URI that Google should redirect to: `https://erp.insightpulseai.com/auth_oauth/signin`.

### 3.3 How Settings Map to the Provider Record

The `res.config.settings` fields map directly to the `auth.oauth.provider` record with XML ID `auth_oauth.provider_google`:

```python
# From res_config_settings.py
def set_values(self):
    super().set_values()
    google_provider = self.env.ref('auth_oauth.provider_google', False)
    if google_provider:
        google_provider.write({
            'enabled': self.auth_oauth_google_enabled,
            'client_id': self.auth_oauth_google_client_id,
        })
```

| Settings Field | Provider Record Field | Value |
|----------------|-----------------------|-------|
| `auth_oauth_google_enabled` | `enabled` | `True` |
| `auth_oauth_google_client_id` | `client_id` | `<your-client-id>.apps.googleusercontent.com` |

### 3.4 Provider Record Fields (Advanced)

For advanced configuration, navigate to **Settings** --> **Technical** --> **OAuth Providers** (requires Developer Mode), or click the **OAuth Providers** link under OAuth Authentication.

The Google provider record has these fields:

| Field | Value | Notes |
|-------|-------|-------|
| **Provider name** | `Google OAuth2` | Display name |
| **Client ID** | `<your-id>.apps.googleusercontent.com` | From Google Cloud Console |
| **Allowed** | `True` | Enables the button on login page |
| **Login button label** | `Sign in with Google` | Text on the button |
| **CSS class** | `o_auth_oauth_provider_icon o_google_provider` | Renders Google icon |
| **Authorization URL** | `https://accounts.google.com/o/oauth2/auth` | Google's OAuth endpoint |
| **Scope** | `openid profile email` | OpenID Connect scopes |
| **UserInfo URL** | `https://www.googleapis.com/oauth2/v3/userinfo` | Token validation endpoint |
| **Data endpoint** | (empty) | Not used for Google |
| **Sequence** | `10` | Sort order on login page |

### 3.5 System Parameters

Unlike Microsoft Azure OAuth, Google OAuth does **not** require the `auth_oauth.authorization_header` system parameter. However, this parameter affects how tokens are sent to the validation endpoint:

| Parameter | Value | Effect |
|-----------|-------|--------|
| `auth_oauth.authorization_header` | `1` | Send token as `Authorization: Bearer <token>` header |
| `auth_oauth.authorization_header` | (not set / `0`) | Send token as `?access_token=<token>` query parameter |

**For Google:** Either method works. Google's userinfo endpoint accepts both `Authorization: Bearer` headers and `access_token` query parameters. However, the `Bearer` header method is more secure and is the IETF recommended approach.

**For Microsoft Azure:** The `auth_oauth.authorization_header` system parameter **must be set to `1`** (documented requirement in Odoo's Azure OAuth docs).

**Recommendation:** Set `auth_oauth.authorization_header = 1` since we run both Google and Microsoft providers. It works for both.

### 3.6 Other Relevant System Parameters

| Parameter | Purpose | Typical Value |
|-----------|---------|---------------|
| `web.base.url` | Base URL used in redirect URI calculation | `https://erp.insightpulseai.com` |
| `web.base.url.freeze` | Prevents automatic base URL detection | `True` (set this for production behind reverse proxy) |

---

## 4. User Flows

### 4.1 Existing Users -- Password Reset Requirement

**From Odoo docs:** "Existing users must reset their password to access the Reset Password page."

**Why is password reset required?**

This is a UX routing decision, not a technical one. The "Log in with Google" button appears on two pages:

1. The **Reset Password** page (`/web/reset_password`)
2. The **Signup/Invitation** page (`/web/signup`)

It does **not** appear on the main `/web/login` page in the same prominent way unless the user navigates there through password reset or invitation flows. The actual mechanism is:

1. Existing user clicks "Reset Password" on the login page.
2. Receives an email with a password reset link.
3. The reset page shows the "Log in with Google" button alongside the password form.
4. User clicks "Log in with Google" instead of setting a new password.
5. Google authenticates the user and returns the access token to Odoo.
6. Odoo matches the Google email to the existing Odoo user's email/login.
7. Odoo writes the `oauth_provider_id`, `oauth_uid`, and `oauth_access_token` to the user record.
8. Subsequent logins can use Google directly from `/web/login`.

**Important:** After the first successful Google login, the "Log in with Google" button **does** appear on the regular `/web/login` page for all users. The password reset step is only needed for the **initial linking** of an existing Odoo account to a Google identity.

**Correction/clarification:** The "Log in with Google" button actually appears on `/web/login` as soon as the Google OAuth provider is enabled. The password reset flow is the recommended way for existing users to **link** their accounts. But technically, an existing user can also click "Log in with Google" on the regular login page -- if their Odoo login email matches their Google email, the OAuth flow will attempt to find and link them.

### 4.2 How User Matching Works

From the `res_users.py` source code, the matching logic is:

```python
def _auth_oauth_signin(self, provider, validation, params):
    oauth_uid = validation['user_id']  # Google's 'sub' claim
    oauth_user = self.search([
        ("oauth_uid", "=", oauth_uid),
        ('oauth_provider_id', '=', provider)
    ])
    if not oauth_user:
        raise AccessDenied()  # Falls through to signup attempt
```

**First login:** Odoo searches for a user with matching `oauth_uid` + `oauth_provider_id`. On first Google login, no user has these fields set, so it falls through to the signup/creation path:

```python
values = self._generate_signup_values(provider, validation, params)
# values = {
#     'name': <Google display name>,
#     'login': <Google email>,
#     'email': <Google email>,
#     'oauth_provider_id': <provider_id>,
#     'oauth_uid': <Google sub>,
#     'oauth_access_token': <token>,
#     'active': True,
# }
login, _ = self.signup(values, token)
```

The `signup()` method (from `auth_signup`) will:
- If a signup token exists (from password reset or invitation): **update the existing user** with OAuth fields.
- If no token and signup is allowed: **create a new user**.
- If no token and signup is disabled: **raise AccessDenied**.

**This is why password reset matters:** The reset link generates a signup token. When the user clicks "Log in with Google" on the reset page, that token is passed through the OAuth state parameter (`state.t`). This token authorizes linking the Google identity to the existing Odoo user.

### 4.3 New Users

New users can be created through Google OAuth in two ways:

**Method 1: Admin sends invitation**
1. Admin creates a user in Odoo with the user's Google email as the login.
2. Admin sends an invitation email.
3. User clicks the invitation link, arrives at the signup page.
4. User clicks "Log in with Google" instead of setting a password.
5. The invitation token authorizes linking the Google identity.

**Method 2: Free signup (if enabled)**
1. If `auth_signup.allow_uninvited` is enabled (Settings --> General Settings --> Permissions --> Customer Account --> Free sign up).
2. User visits `/web/signup` or `/web/login`.
3. Clicks "Log in with Google".
4. Odoo creates a new portal user with Google's email and name.

**Method 3: Portal/customer access**
- Works the same as free signup if customer accounts are enabled.
- New portal users are created automatically.

### 4.4 What Gets Stored on the User Record

After successful Google OAuth login, the `res.users` record is updated with:

| Field | Value | Example |
|-------|-------|---------|
| `oauth_provider_id` | Link to Google provider | `auth_oauth.provider_google` |
| `oauth_uid` | Google's subject identifier (`sub` claim) | `117234567890123456789` |
| `oauth_access_token` | The access token from Google | (opaque token, stored with `NO_ACCESS` group) |

**SQL constraint:** `unique(oauth_provider_id, oauth_uid)` -- one Google identity can only be linked to one Odoo user.

---

## 5. Login Page Behavior

### 5.1 How the Google Button Appears

The login page template chain:

1. `web.login` -- base login form with username/password fields.
2. `web.login_oauth` -- defines the `auth_btns` list and renders OAuth buttons.
3. `auth_oauth.providers` -- injects the list of enabled providers into `auth_btns`.

The `OAuthLogin` controller extends the web login controller:

```python
class OAuthLogin(Home):
    def list_providers(self):
        providers = request.env['auth.oauth.provider'].sudo().search_read(
            [('enabled', '=', True)]
        )
        for provider in providers:
            return_url = request.httprequest.url_root + 'auth_oauth/signin'
            state = self.get_state(provider)
            params = dict(
                response_type='token',
                client_id=provider['client_id'],
                redirect_uri=return_url,
                scope=provider['scope'],
                state=json.dumps(state),
            )
            provider['auth_link'] = "%s?%s" % (
                provider['auth_endpoint'],
                werkzeug.urls.url_encode(params)
            )
        return providers
```

**Conditions for the button to appear:**
1. `auth_oauth` module is installed.
2. At least one `auth.oauth.provider` record has `enabled=True`.
3. The provider has a `client_id` set.

### 5.2 The OAuth State Parameter

The state parameter encodes:

```python
state = {
    'd': request.session.db,        # Database name
    'p': provider['id'],            # Provider record ID
    'r': redirect_url,              # Where to go after login
    't': token,                     # Signup token (if from reset/invite)
}
```

This state is JSON-encoded and passed to Google, which returns it unchanged in the callback. Odoo uses it to:
- Identify which database to authenticate against.
- Identify which OAuth provider was used.
- Redirect the user to the correct page after login.
- Carry the signup token for account linking.

### 5.3 The Callback Flow at `/auth_oauth/signin`

1. Google redirects to: `https://erp.insightpulseai.com/auth_oauth/signin#access_token=<TOKEN>&token_type=Bearer&expires_in=3600&state=<STATE>`
2. The `fragment_to_query_string` decorator serves a small HTML page with JavaScript that converts the URL fragment (`#...`) to query parameters (`?...`) and reloads.
3. On the second request, the controller has access to `access_token` and `state` as query parameters.
4. Odoo calls `res.users.auth_oauth(provider_id, params)`:
   - Validates the token against `https://www.googleapis.com/oauth2/v3/userinfo`.
   - Extracts `sub`, `email`, `name` from the userinfo response.
   - Finds or creates the user.
   - Returns `(dbname, login, access_token)`.
5. Odoo authenticates the session: `request.session.authenticate(request.env, credential)` with `type='oauth_token'`.
6. Redirects to `/odoo` or the stored redirect URL.

---

## 6. CE vs Enterprise

### 6.1 Module Availability

The `auth_oauth` module is **100% CE (Community Edition)**. It lives in `odoo/addons/auth_oauth/` in the main Odoo repository, not in the Enterprise repository.

**Proof:** The module's `__manifest__.py` lists `license: 'LGPL-3'` and depends only on `base`, `web`, `base_setup`, `auth_signup` -- all CE modules.

### 6.2 Feature Parity

There are **no Enterprise-only OAuth features**. Everything described in this document works identically on CE and Enterprise.

### 6.3 OCA Enhancements

The OCA `server-auth` repository provides:

| Module | Description | Status |
|--------|-------------|--------|
| `auth_oidc` | OpenID Connect using **authorization code flow** (more secure than implicit) | Available for 17.0, 18.0. Check 19.0 branch. |
| `auth_oauth_multi_token` | Allow multiple OAuth tokens per user | Available for 17.0 |

**`auth_oidc` is the recommended upgrade path** if you want to move from implicit flow to authorization code flow with PKCE. It adds:
- `client_secret` field to the provider model
- `token_endpoint` field (for code-to-token exchange)
- `jwks_uri` field (for JWT validation)
- Proper PKCE support

**Recommendation for InsightPulseAI:** Start with stock `auth_oauth` (implicit flow) for simplicity. Evaluate `auth_oidc` later if security audit requires authorization code flow.

---

## 7. Gmail Add-On Integration

### 7.1 Current Architecture

The InsightPulseAI Gmail add-on opens Odoo's `/web/login` page (either in a popup or via `RELOAD_ADD_ON`). The user sees the "Log in with Google" button and authenticates.

### 7.2 Session State After Google Login

After successful Google OAuth login through the browser:

1. **Odoo session cookie** (`session_id`) is set on `erp.insightpulseai.com`.
2. The user has a valid Odoo web session.
3. The `oauth_access_token` is stored on the `res.users` record.

**What the add-on sidebar gets:**
- If the add-on opens Odoo in the same browser context (iframe or popup), the session cookie persists.
- The add-on's Apps Script backend does **not** automatically get the Odoo session -- it runs server-side in Google's infrastructure.

### 7.3 Bridging Web Session to API Access

The Gmail add-on backend (Apps Script) needs to make API calls to Odoo. Options:

| Method | How | Pros | Cons |
|--------|-----|------|------|
| **API Key** | Generate an Odoo API key for the user, store in Apps Script properties | Simple, persistent | Manual setup per user |
| **Session token relay** | After OAuth login, relay the session token back to Apps Script | Automatic | Session expires, complex |
| **OAuth token reuse** | Use the Google access token stored on the user record for API auth | Leverages existing token | Odoo's JSON-RPC does not accept OAuth tokens directly |
| **Dedicated OAuth for API** | Create a separate OAuth flow (authorization code) for API access | Most correct | Requires `auth_oidc` or custom module |

**Recommended approach for v1:** Use Odoo API keys. After the user completes Google OAuth login in the browser, have them generate an API key from their Odoo profile and enter it in the add-on settings. This decouples browser auth from API auth.

### 7.4 Detecting Login Completion

The Gmail add-on can detect login completion through:

1. **`RELOAD_ADD_ON` action response** -- if the add-on triggers an authorization card that opens `/web/login`, the add-on reloads after the popup closes.
2. **Polling** -- the add-on backend can poll a health endpoint on Odoo (e.g., `/web/session/get_session_info`) with stored credentials.
3. **Webhook/callback** -- Odoo could notify a webhook after successful login (requires custom module).

---

## 8. Security and Troubleshooting

### 8.1 Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `redirect_uri_mismatch` | The redirect URI in Google Console does not exactly match what Odoo sends | Ensure `https://erp.insightpulseai.com/auth_oauth/signin` is in Authorized redirect URIs. Check trailing slashes. Check http vs https. |
| `access_denied` (oauth_error=2) | User denied consent, or Google returned an error | Check consent screen configuration. Ensure user is in test users list (if in testing mode). |
| `oauth_error=3` ("You do not have access...") | Odoo could not find or create a user for this Google identity | Check if user exists with matching email. Check if signup is allowed. Check invitation token. |
| `oauth_error=1` ("Sign up is not allowed...") | `auth_signup` module not installed | Install `auth_signup` module. |
| Redirect loop (`/web/login` <--> `/auth_oauth/signin`) | Reverse proxy misconfiguration. `web.base.url` mismatch. Missing proxy headers. | Set `web.base.url` correctly. Set `web.base.url.freeze=True`. Enable `proxy_mode=True`. Configure nginx to pass `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`. |
| `401 Unauthorized` from Google userinfo | Token expired or invalid. Network issue. | Check server clock. Check if `auth_oauth.authorization_header` parameter needs to be set. |
| `CSRF cookie not set` | Session/cookie issue behind reverse proxy | Ensure `proxy_mode=True` in Odoo config. Check nginx `proxy_set_header` directives. |
| `invalid_grant` | Token was already used or expired | This typically happens in authorization code flow, less common in implicit flow. Check for double-submission. |

### 8.2 Reverse Proxy Configuration (Azure Front Door)

Since `erp.insightpulseai.com` is behind Azure Front Door, ensure:

1. **`proxy_mode = True`** in `odoo.conf`.
2. **`web.base.url = https://erp.insightpulseai.com`** (system parameter).
3. **`web.base.url.freeze = True`** (system parameter).
4. Azure Front Door passes correct headers:
   - `X-Forwarded-For`
   - `X-Forwarded-Proto: https`
   - `X-Forwarded-Host: erp.insightpulseai.com`

### 8.3 Token Validation

Odoo validates the Google access token by calling:

```
GET https://www.googleapis.com/oauth2/v3/userinfo
Authorization: Bearer <access_token>
```

(or `?access_token=<token>` as query param if `auth_oauth.authorization_header` is not set)

Expected response:

```json
{
  "sub": "117234567890123456789",
  "name": "John Doe",
  "given_name": "John",
  "family_name": "Doe",
  "picture": "https://lh3.googleusercontent.com/...",
  "email": "john@example.com",
  "email_verified": true,
  "locale": "en"
}
```

Odoo extracts the `sub` field as the unique user identifier (`oauth_uid`).

### 8.4 CSRF/State Validation

Odoo's state parameter serves as a CSRF token. The flow:

1. Odoo generates state JSON with `d` (database), `p` (provider), `r` (redirect).
2. State is sent to Google as a query parameter.
3. Google returns it unchanged in the callback.
4. Odoo parses the state to verify the database and provider match.

**Note:** Odoo does **not** use a cryptographic nonce in the state parameter (this is a known open issue: [odoo/odoo#63750](https://github.com/odoo/odoo/issues/63750)). The state is plain JSON, not signed or encrypted.

### 8.5 Multiple OAuth Providers Coexisting

Odoo fully supports multiple OAuth providers simultaneously. Each provider is a separate `auth.oauth.provider` record. The login page renders buttons for all enabled providers.

For InsightPulseAI with both Google and Microsoft:

```
/web/login page shows:
  [Username]
  [Password]
  [Log in]
  - or -
  [Google icon] Sign in with Google
  [Windows icon] Microsoft Azure
```

Each provider has independent:
- Client ID
- Auth endpoint
- Validation endpoint
- Scope
- Enabled/disabled state

Users can be linked to **only one OAuth provider** at a time (the `oauth_provider_id` is a `Many2one` field, not `Many2many`). If a user logs in with Google, then later tries Microsoft, the `oauth_uid` and `oauth_provider_id` will be overwritten.

### 8.6 Debug Logging

Enable OAuth debug logging:

```python
# In odoo.conf or command line:
--log-handler=odoo.addons.auth_oauth:DEBUG
```

Key log messages in the controller:

- `OAuth2: access denied, redirect to main page...` -- `AccessDenied` during signin.
- `auth_signup not installed on database...` -- Missing `auth_signup` module.
- `Exception during request handling` -- Generic error during OAuth flow.

### 8.7 Token Expiry

Google access tokens expire after **1 hour** (3600 seconds). Odoo stores the access token on the user record but does **not** refresh it. The token is used:

1. Once during login to validate against Google's userinfo endpoint.
2. Subsequently to verify the session (in `_check_credentials`).

After the token expires, the user must re-authenticate via Google on their next login. This is acceptable because Odoo sessions persist via cookies -- the OAuth token is only needed during initial authentication, not for ongoing session maintenance.

---

## 9. Comparison: Google vs Microsoft OAuth in Odoo

| Aspect | Google OAuth | Microsoft Azure OAuth |
|--------|-------------|----------------------|
| **Pre-configured in Odoo** | Yes (`auth_oauth.provider_google`) | No (must create provider record manually) |
| **Settings UI** | Dedicated checkbox + Client ID field | Must use OAuth Providers form directly |
| **System parameter required** | None (optional: `auth_oauth.authorization_header`) | **Must set** `auth_oauth.authorization_header = 1` |
| **Auth endpoint** | `https://accounts.google.com/o/oauth2/auth` | `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize` |
| **Validation endpoint** | `https://www.googleapis.com/oauth2/v3/userinfo` | `https://graph.microsoft.com/oidc/userinfo` |
| **Scope** | `openid profile email` | `openid profile email` |
| **CSS class** | `o_auth_oauth_provider_icon o_google_provider` | `fa fa-fw fa-windows` |
| **Client Secret needed** | No (implicit flow) | No (implicit flow, but Azure also supports tokens in auth settings) |
| **Azure portal: Token types** | N/A | Must enable "Access tokens" and "ID tokens" in Authentication |
| **API permissions** | N/A (scopes requested in auth URL) | Must explicitly grant `User.Read` delegated permission |
| **Tenant types** | Internal (GWS) / External | Single tenant / Multi-tenant / Personal |
| **Setup complexity** | Lower (pre-configured provider) | Higher (manual provider, system parameter, Azure portal config) |
| **User matching** | By `sub` claim from userinfo | By `sub` claim from userinfo |
| **Button label** | "Sign in with Google" | Custom (e.g., "Microsoft Azure") |

**Why Microsoft Entra is primary for InsightPulseAI:**
1. Organization already uses Microsoft 365 / Entra ID as identity provider.
2. Entra provides enterprise governance (conditional access, MFA policies, group-based access).
3. All Azure infrastructure authenticates via Entra managed identities.
4. Google OAuth is secondary for users who access via Gmail add-on and may prefer Google auth.

---

## 10. Exact Configuration for InsightPulseAI

### 10.1 Google Cloud Console

| Setting | Value |
|---------|-------|
| **Project** | `insightpulseai-odoo` (or existing GCP project) |
| **OAuth consent screen type** | Internal (if GWS org) or External (testing mode) |
| **App name** | `InsightPulseAI Odoo` |
| **Authorized domains** | `insightpulseai.com` |
| **OAuth client type** | Web application |
| **Client name** | `Odoo ERP Login` |
| **Authorized JavaScript origins** | `https://erp.insightpulseai.com` |
| **Authorized redirect URIs** | `https://erp.insightpulseai.com/auth_oauth/signin` |
| **Scopes** | `openid`, `email`, `profile` (non-sensitive, auto-included) |

### 10.2 Odoo Settings

**Via Settings UI (recommended):**

1. Settings --> General Settings --> Integrations --> OAuth Authentication: **Enabled**
2. Settings --> General Settings --> Integrations --> Google Authentication: **Enabled**
3. Client ID: `<your-client-id>.apps.googleusercontent.com`
4. Save.

**Via System Parameters (if needed):**

| Key | Value |
|-----|-------|
| `web.base.url` | `https://erp.insightpulseai.com` |
| `web.base.url.freeze` | `True` |
| `auth_oauth.authorization_header` | `1` (recommended for compatibility with Azure provider) |

### 10.3 Provider Record Values (for verification)

After configuration via Settings, verify the provider record at Settings --> Technical --> OAuth Providers (Developer Mode):

| Field | Expected Value |
|-------|---------------|
| Provider name | `Google OAuth2` |
| Client ID | `<your-id>.apps.googleusercontent.com` |
| Allowed | Checked |
| Login button label | `Sign in with Google` |
| Authorization URL | `https://accounts.google.com/o/oauth2/auth` |
| Scope | `openid profile email` |
| UserInfo URL | `https://www.googleapis.com/oauth2/v3/userinfo` |

### 10.4 Verification Checklist

- [ ] Google Cloud Console: OAuth consent screen configured
- [ ] Google Cloud Console: OAuth 2.0 client created (Web application type)
- [ ] Google Cloud Console: Redirect URI set to `https://erp.insightpulseai.com/auth_oauth/signin`
- [ ] Google Cloud Console: JavaScript origin set to `https://erp.insightpulseai.com`
- [ ] Odoo: `auth_oauth` module installed (via OAuth Authentication toggle)
- [ ] Odoo: Google Authentication enabled with Client ID
- [ ] Odoo: `web.base.url` = `https://erp.insightpulseai.com`
- [ ] Odoo: `web.base.url.freeze` = `True`
- [ ] Odoo: `proxy_mode = True` in odoo.conf (behind Azure Front Door)
- [ ] Test: Navigate to `https://erp.insightpulseai.com/web/login` -- "Sign in with Google" button visible
- [ ] Test: Click button -- redirected to Google consent screen
- [ ] Test: After consent -- redirected back to Odoo, logged in
- [ ] Test: User record has `oauth_provider_id` and `oauth_uid` populated
- [ ] Test: Subsequent logins via Google work without password reset

---

## 11. Known Issues and Limitations

### 11.1 Implicit Flow (Security Concern)

Odoo's `auth_oauth` uses implicit flow (`response_type=token`), which is deprecated in OAuth 2.1. The access token is exposed in the browser URL fragment. This is a known open issue ([odoo/odoo#63965](https://github.com/odoo/odoo/issues/63965)) with no fix as of Odoo 19.

**Mitigation:** The token is short-lived (1 hour), and the `fragment_to_query_string` decorator converts it to query parameters in a client-side redirect, limiting exposure. For higher security, consider OCA's `auth_oidc` module.

### 11.2 No Nonce Validation

Odoo does not generate or validate an OIDC nonce ([odoo/odoo#63750](https://github.com/odoo/odoo/issues/63750)). This makes the flow theoretically vulnerable to token replay attacks.

### 11.3 Single Provider per User

A user can only be linked to one OAuth provider at a time (`oauth_provider_id` is Many2one). If a user first links Google, then logs in via Microsoft, the Google link is overwritten. This means a user cannot use both Google and Microsoft interchangeably.

### 11.4 Token Not Refreshed

Odoo stores the access token but never refreshes it. This is fine for login (token only needed once), but means the stored token cannot be reused for long-running API access to Google services.

### 11.5 Testing Mode User Limit

Google OAuth consent screen in External/testing mode limits to **100 test users**. Each test user must be explicitly added by email. For broader testing, publish the app (requires Google verification for external user types).

---

## 12. Sources

- [Google Sign-In Authentication -- Odoo 19.0 documentation](https://www.odoo.com/documentation/19.0/applications/general/users/google.html)
- [Microsoft Azure sign-in authentication -- Odoo 19.0 documentation](https://www.odoo.com/documentation/19.0/applications/general/users/azure.html)
- [Connect Gmail to Odoo using Google OAuth -- Odoo 19.0 documentation](https://www.odoo.com/documentation/19.0/applications/general/email_communication/google_oauth.html)
- [Odoo CE 19.0 `auth_oauth` module source](https://github.com/odoo/odoo/tree/19.0/addons/auth_oauth)
- [Odoo CE 19.0 `auth_oauth/controllers/main.py`](https://github.com/odoo/odoo/blob/19.0/addons/auth_oauth/controllers/main.py)
- [Odoo CE 19.0 `auth_oauth/models/res_users.py`](https://github.com/odoo/odoo/blob/19.0/addons/auth_oauth/models/res_users.py)
- [Odoo CE 19.0 `auth_oauth/data/auth_oauth_data.xml`](https://github.com/odoo/odoo/blob/19.0/addons/auth_oauth/data/auth_oauth_data.xml)
- [GitHub Issue #63965: auth_oauth Implicit Flow vs Authorization Code Flow](https://github.com/odoo/odoo/issues/63965)
- [GitHub Issue #63750: Implicit Flow without nonce](https://github.com/odoo/odoo/issues/63750)
- [Odoo Forum: Google OAuth redirect loop in Odoo 19](https://www.odoo.com/forum/help-1/odoo-19-google-oauth-fresh-install-still-stuck-in-redirect-loop-weblogin-auth-oauthsignin-289689)
- [Odoo Forum: OAuth client secret question](https://www.odoo.com/forum/help-1/oauth-with-odoo-where-to-enter-the-client-secret-279211)
- [OCA `auth_oidc` module (server-auth)](https://github.com/OCA/server-auth/tree/17.0/auth_oidc)
- [Google Cloud: Setting up OAuth 2.0](https://support.google.com/cloud/answer/6158849)
- [Google: OAuth 2.0 for Client-side Web Applications](https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow)
- [OAuth 2.0 Implicit Grant Type (oauth.net)](https://oauth.net/2/grant-types/implicit/)

---

*Last updated: 2026-03-27*
*Research scope: Odoo 19.0 CE, auth_oauth module, Google OAuth2 provider*

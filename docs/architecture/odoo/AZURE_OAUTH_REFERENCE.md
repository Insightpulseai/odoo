# Odoo 18 Azure OAuth (Microsoft Entra ID) -- Complete Reference

> Knowledge base for configuring Microsoft Entra ID SSO with Odoo 18 CE.
> Covers the official Odoo `auth_oauth` module, OCA `auth_oidc`, Entra app registration,
> and Gmail add-on integration implications.
>
> Last researched: 2026-03-27
> Sources: Odoo 18.0 official docs, Odoo GitHub 18.0 branch, Microsoft Learn, OCA server-auth 18.0

---

## Table of Contents

1. [Module Architecture](#1-module-architecture)
2. [Entra ID App Registration (Azure Side)](#2-entra-id-app-registration-azure-side)
3. [Odoo-Side Configuration](#3-odoo-side-configuration)
4. [OAuth Provider Record -- Exact Field Values](#4-oauth-provider-record----exact-field-values)
5. [User Experience Flows](#5-user-experience-flows)
6. [CE vs Enterprise Differences](#6-ce-vs-enterprise-differences)
7. [OCA auth_oidc -- Authorization Code Flow Alternative](#7-oca-auth_oidc----authorization-code-flow-alternative)
8. [Google OAuth Comparison](#8-google-oauth-comparison)
9. [Security Considerations](#9-security-considerations)
10. [Gmail Add-On Integration Implications](#10-gmail-add-on-integration-implications)
11. [InsightPulseAI Exact Configuration](#11-insightpulseai-exact-configuration)
12. [Troubleshooting](#12-troubleshooting)
13. [Sources](#13-sources)

---

## 1. Module Architecture

### 1.1 The `auth_oauth` Module (Odoo 18 CE -- Native)

`auth_oauth` ships with **Odoo CE** (not Enterprise-only). It is located at `addons/auth_oauth/` in the Odoo 18 source tree.

**Manifest:**
```
Name:       OAuth2 Authentication
Category:   Hidden/Tools
License:    LGPL-3
Depends:    base, web, base_setup, auth_signup
Data files: data/auth_oauth_data.xml
            views/auth_oauth_views.xml
            views/res_config_settings_views.xml
            views/auth_oauth_templates.xml
            security/ir.model.access.csv
```

**Key fact:** `auth_oauth` depends on `auth_signup`. Both are CE modules. No Enterprise dependency.

### 1.2 Model: `auth.oauth.provider`

The provider model stores OAuth2 provider configurations:

```python
class AuthOauthProvider(models.Model):
    _name = 'auth.oauth.provider'
    _description = 'OAuth2 provider'
    _order = 'sequence, name'

    name = fields.Char(string='Provider name', required=True)
    client_id = fields.Char(string='Client ID')
    auth_endpoint = fields.Char(string='Authorization URL', required=True)
    scope = fields.Char(default='openid profile email')
    validation_endpoint = fields.Char(string='UserInfo URL', required=True)
    data_endpoint = fields.Char()
    enabled = fields.Boolean(string='Allowed')
    css_class = fields.Char(string='CSS class',
                           default='fa fa-fw fa-sign-in text-primary')
    body = fields.Char(required=True, string="Login button label",
                      help='Link text in Login Dialog', translate=True)
    sequence = fields.Integer(default=10)
```

### 1.3 Default Providers (shipped with Odoo 18)

From `data/auth_oauth_data.xml`:

| Provider | Auth Endpoint | Scope | Validation Endpoint | Enabled |
|----------|--------------|-------|---------------------|---------|
| Odoo.com Accounts | `https://accounts.odoo.com/oauth2/auth` | `userinfo` | `https://accounts.odoo.com/oauth2/tokeninfo` | Yes |
| Facebook Graph | `https://www.facebook.com/dialog/oauth` | `public_profile,email` | `https://graph.facebook.com/me` | No |
| Google OAuth2 | `https://accounts.google.com/o/oauth2/auth` | `openid profile email` | `https://www.googleapis.com/oauth2/v3/userinfo` | No |

**Microsoft Azure is NOT a default provider.** It must be manually added.

### 1.4 OAuth Flow (Implicit Flow)

Odoo's native `auth_oauth` uses the **OAuth 2.0 Implicit Flow** (`response_type=token`). This is a critical architectural detail:

1. User clicks "Log in with Microsoft Azure" on `/web/login`
2. Browser redirects to `auth_endpoint?response_type=token&client_id=...&redirect_uri=...&scope=...&state=...`
3. Microsoft authenticates the user and returns the access token as a **URL fragment** (`#access_token=...`)
4. The `fragment_to_query_string` JavaScript decorator converts the fragment to a query string
5. Browser redirects to `/auth_oauth/signin?access_token=...&state=...`
6. Odoo server validates the token against the `validation_endpoint` (UserInfo URL)
7. Odoo matches the user by `oauth_uid` + `oauth_provider_id`, or creates a new user

**The `fragment_to_query_string` decorator** (in `controllers/main.py`):
When the `/auth_oauth/signin` route receives no query parameters (because the token is in the fragment), it returns an HTML page with JavaScript that moves the fragment to the query string and reloads.

```python
@http.route('/auth_oauth/signin', type='http', auth='none', readonly=False)
@fragment_to_query_string
def signin(self, **kw):
    state = json.loads(kw['state'])
    dbname = state['d']
    provider = state['p']
    _, login, key = request.env['res.users'].with_user(SUPERUSER_ID).auth_oauth(provider, kw)
    # ... authenticate session ...
```

### 1.5 Token Validation (`res_users.py`)

The `_auth_oauth_rpc` method validates tokens by calling the provider's validation endpoint:

```python
def _auth_oauth_rpc(self, endpoint, access_token):
    if self.env['ir.config_parameter'].sudo().get_param('auth_oauth.authorization_header'):
        # Send token as Authorization: Bearer header
        response = requests.get(endpoint, headers={'Authorization': 'Bearer %s' % access_token})
    else:
        # Send token as query parameter
        response = requests.get(endpoint, params={'access_token': access_token})
    return response.json()
```

### 1.6 User Matching Logic (`_auth_oauth_signin`)

1. Search for existing user by `oauth_uid` and `oauth_provider_id`
2. If found: update the `oauth_access_token` and return the login
3. If not found: create a new user via `auth_signup` (JIT provisioning)
4. The `oauth_uid` is derived from the validation response: checks `sub`, `id`, or `user_id` keys (in that order)
5. Email is taken from `email` key in the validation response

---

## 2. Entra ID App Registration (Azure Side)

### 2.1 Create the App Registration

1. Go to [Microsoft Azure Portal](https://portal.azure.com/)
2. Navigate to **Microsoft Entra ID** (formerly Azure Active Directory)
3. Click **Add (+)** > **App registration**
4. Configure:
   - **Name:** `Odoo Login OAuth` (or `InsightPulseAI Odoo Login`)
   - **Supported account types:** Choose based on use case:
     - **Accounts in this organizational directory only (Single tenant)** -- for internal workforce users
     - **Accounts in any organizational directory (Multi-tenant)** -- for cross-org access
     - **Personal Microsoft accounts only** -- for portal/customer users
   - **Redirect URI:**
     - Platform: **Web**
     - URL: `https://erp.insightpulseai.com/auth_oauth/signin`

5. Click **Register**

### 2.2 Token Configuration (Authentication)

1. Go to **Authentication** in the left menu
2. Under **Implicit grant and hybrid flows**, check:
   - [x] **Access tokens** (used for implicit flows)
   - [x] **ID tokens** (used for implicit and hybrid flows)
3. Click **Save**

These checkboxes are required because Odoo's native `auth_oauth` uses the implicit flow (`response_type=token`).

### 2.3 API Permissions

At minimum, the delegated permission **User.Read** must be granted:

1. Go to **API permissions** in the left menu
2. Click **+ Add a Permission**
3. Select **Microsoft Graph** under Commonly Used Microsoft APIs
4. Choose **Delegated Permissions**
5. Search for and select **User.Read**
6. Click **Add permissions**

`User.Read` is often added by default but must be explicitly verified.

### 2.4 Gather Credentials

From the **Overview** page:

| Credential | Where to Find | Example |
|-----------|--------------|---------|
| **Application (client) ID** | Overview page, top section | `07bd9669-1eca-4d93-8880-fd3abb87f812` |
| **Directory (tenant) ID** | Overview page | `{your-tenant-id}` |
| **OAuth 2.0 authorization endpoint (v2)** | Overview > Endpoints button | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize` |

Click **Endpoints** in the top menu and copy the **OAuth 2.0 authorization endpoint (v2)** value. This is the Authorization URL for Odoo.

### 2.5 Client Secret (Optional for Implicit Flow)

For the native `auth_oauth` implicit flow, a client secret is **not required** because the token is returned directly from the authorize endpoint without a server-side token exchange.

However, if using OCA `auth_oidc` with authorization code flow, a client secret **is required**:

1. Go to **Certificates & secrets**
2. Click **+ New client secret**
3. Add a description and expiry
4. Copy the **Value** immediately (it is only shown once)
5. Store in Azure Key Vault (secret name: `entra-odoo-login-client-secret`)

### 2.6 Supported Account Types Matrix

| Type | Audience | Tenant in URL | Use Case |
|------|---------|--------------|----------|
| Single tenant | Your org only | `{tenant-id}` | Internal workforce (recommended for InsightPulseAI) |
| Multi-tenant (orgs) | Any Azure AD org | `organizations` | Cross-company access |
| Multi-tenant + personal | Orgs + personal Microsoft | `common` | Broadest access |
| Personal only | Microsoft personal accounts | `consumers` | Portal/customer users |

### 2.7 Token Version: v1.0 vs v2.0

Odoo's official documentation specifies the **v2.0 endpoint**:
- Authorization: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize`
- Token: `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`

The v2.0 endpoint supports:
- OpenID Connect scopes (`openid`, `profile`, `email`)
- Merged Microsoft account and work/school account sign-in
- JWT tokens with `sub` claim

Do NOT use v1.0 endpoints (`/oauth2/authorize`, `/oauth2/token`).

---

## 3. Odoo-Side Configuration

### 3.1 System Parameter: `auth_oauth.authorization_header`

**This is the first and most critical step.**

1. Activate [Developer Mode](https://www.odoo.com/documentation/18.0/applications/general/developer_mode.html)
2. Go to **Settings > Technical > System Parameters**
3. Click **New**
4. Set:
   - **Key:** `auth_oauth.authorization_header`
   - **Value:** `1`
5. Click **Save**

**What this does:** When set to `1`, Odoo sends the access token as an `Authorization: Bearer` HTTP header when calling the UserInfo endpoint. Microsoft Graph's userinfo endpoint (`https://graph.microsoft.com/oidc/userinfo`) **requires** the token in the Authorization header. Without this parameter, Odoo sends the token as a query parameter, which Microsoft Graph rejects.

This parameter is **required** for Microsoft Azure OAuth. It is NOT required for Google OAuth (Google accepts query parameters).

### 3.2 Enable OAuth Authentication

1. Go to **Settings > General Settings > Integrations**
2. Enable **OAuth Authentication** checkbox
3. Click **Save** (Odoo may prompt re-login)

### 3.3 Add the Microsoft Azure Provider

1. Go to **Settings > General Settings > Integrations > OAuth Providers** (or via Settings > Technical > OAuth Providers in developer mode)
2. Click **New**
3. Fill in the fields (see Section 4 for exact values)
4. Check **Allowed** to enable
5. Click **Save**

---

## 4. OAuth Provider Record -- Exact Field Values

### 4.1 Microsoft Azure (Entra ID) Provider

| Field | Value | Notes |
|-------|-------|-------|
| **Provider name** | `Azure` | Display name in admin |
| **Client ID** | `07bd9669-1eca-4d93-8880-fd3abb87f812` | From Azure app registration Overview |
| **Authorization URL** | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize` | Replace `{tenant-id}` with your actual tenant ID |
| **UserInfo URL** | `https://graph.microsoft.com/oidc/userinfo` | Microsoft Graph OIDC userinfo endpoint |
| **Scope** | `openid profile email` | Space-separated |
| **Data Endpoint** | *(leave empty)* | Not needed for Microsoft |
| **CSS class** | `fa fa-fw fa-windows` | Shows Windows logo on login button |
| **Login button label** | `Microsoft Azure` | Text shown on the login page |
| **Allowed** | `True` (checked) | Enables the provider |
| **Sequence** | `10` | Controls display order |

### 4.2 Google OAuth2 Provider (Default -- Already Exists)

| Field | Value | Notes |
|-------|-------|-------|
| **Provider name** | `Google OAuth2` | Pre-configured in Odoo |
| **Client ID** | *(from Google API Console)* | Must be filled in |
| **Authorization URL** | `https://accounts.google.com/o/oauth2/auth` | Pre-configured |
| **UserInfo URL** | `https://www.googleapis.com/oauth2/v3/userinfo` | Pre-configured |
| **Scope** | `openid profile email` | Pre-configured |
| **CSS class** | `o_auth_oauth_provider_icon o_google_provider` | Google brand icon |
| **Login button label** | `Sign in with Google` | Pre-configured |
| **Allowed** | `False` by default | Must enable and add Client ID |

### 4.3 Key Differences: Microsoft vs Google in Odoo

| Aspect | Microsoft Azure | Google |
|--------|----------------|--------|
| System parameter required | `auth_oauth.authorization_header = 1` | Not required |
| Token delivery | Bearer header (mandatory) | Query parameter (default) |
| Provider pre-exists in Odoo | No (must create) | Yes (just enable + add Client ID) |
| UserInfo endpoint | `graph.microsoft.com/oidc/userinfo` | `googleapis.com/oauth2/v3/userinfo` |
| Client Secret needed (implicit) | No | No |
| Auth endpoint version | v2.0 | N/A |

---

## 5. User Experience Flows

### 5.1 First-Time Login (Account Linking)

**Critical requirement:** Users must be on the **Odoo password reset page** to link their Microsoft account. This is the ONLY way Odoo links an external OAuth identity to an Odoo user account.

**For existing Odoo users:**
1. Admin sends a password reset email (or user clicks "Reset Password" on login page)
2. User opens the password reset link
3. On the reset page, user clicks **"Microsoft Azure"** button (NOT "Reset Password")
4. Browser redirects to Microsoft login
5. User authenticates with Microsoft (+ MFA if enabled)
6. Microsoft redirects back to Odoo with access token
7. Odoo validates the token, matches user by email, links the accounts
8. User is logged in

**For new Odoo users (invited):**
1. Admin creates user in Odoo and sends invitation email
2. User opens the invitation link
3. User clicks **"Microsoft Azure"** button (instead of setting a password)
4. Same OAuth flow as above
5. Odoo creates the link between Microsoft identity and Odoo user

**Important:** If users set a password first, they must reset it again to reach the linking page.

### 5.2 Returning User Login

After the initial linking:
1. User navigates to `https://erp.insightpulseai.com/web/login`
2. Login page shows "Log in with Microsoft Azure" button
3. User clicks the button
4. Browser redirects to Microsoft (may auto-login if already signed in)
5. Redirects back to Odoo, session is created
6. User lands on the Odoo home page

### 5.3 The OAuth Redirect Flow (Technical)

```
Browser                    Odoo                     Microsoft
  |                         |                          |
  |-- GET /web/login ------>|                          |
  |<-- Login page + --------|                          |
  |   "Log in with Azure"   |                          |
  |                         |                          |
  |-- Click Azure link ---->|                          |
  |   (auth_link URL)       |                          |
  |                         |                          |
  |-- GET /oauth2/v2.0/authorize ---------------------->|
  |   ?response_type=token                             |
  |   &client_id=07bd9669-...                          |
  |   &redirect_uri=https://erp.../auth_oauth/signin   |
  |   &scope=openid+profile+email                      |
  |   &state={"d":"odoo","p":4,"r":"..."}              |
  |                         |                          |
  |<-- 302 Redirect -----------------------------------|
  |   https://erp.../auth_oauth/signin#access_token=... |
  |                         |                          |
  |-- GET /auth_oauth/signin (no query params) ------->|
  |<-- JS: move fragment to query string --------------|
  |                         |                          |
  |-- GET /auth_oauth/signin?access_token=...&state=...>|
  |                         |                          |
  |                         |-- GET graph.microsoft.com/oidc/userinfo
  |                         |   Authorization: Bearer <token>
  |                         |<-- {sub, email, name} ----|
  |                         |                          |
  |                         |-- Match user by oauth_uid |
  |                         |-- Create session          |
  |<-- 303 Redirect --------|                          |
  |   to /odoo (or redirect)|                          |
```

### 5.4 What Happens If No Matching User Exists

If `auth_signup` allows user creation (configured in Settings > General Settings > Customer Account):
- Odoo creates a new `res.users` record using email and name from the OAuth validation response
- The new user gets the `oauth_uid` and `oauth_provider_id` set
- Default groups are applied based on Odoo configuration

If user creation is disabled:
- The login fails with "Access Denied" error
- User sees `oauth_error=3` on the login page

### 5.5 Session State Created After Login

After successful OAuth login, Odoo creates a standard web session:
- `session_id` cookie (HttpOnly, Secure, SameSite=Lax)
- `res.users` record updated with `oauth_access_token`
- Session stored server-side in `ir.sessions` or file-based session store
- Session contains: `uid`, `login`, `db`, `context`

---

## 6. CE vs Enterprise Differences

### 6.1 `auth_oauth` Availability

**`auth_oauth` is a CE module.** It ships with Odoo Community Edition 18.0. There is NO Enterprise requirement for basic Microsoft OAuth sign-in.

The module is in `addons/auth_oauth/` in the CE repository (`github.com/odoo/odoo`), not in the Enterprise repository.

### 6.2 What Enterprise Adds

Enterprise does NOT add OAuth-specific features. The `auth_oauth` module is identical in CE and Enterprise. However:

- **Odoo.com account linking** (the default `Odoo.com Accounts` provider) is only meaningful for Odoo Online/Odoo.sh databases
- **Studio** can customize the login page (Enterprise only), but the OAuth flow itself is the same
- All OAuth providers (Microsoft, Google, Facebook) work identically in CE

### 6.3 CE Limitations

1. **Implicit Flow Only:** Native `auth_oauth` uses implicit flow (`response_type=token`). Microsoft recommends authorization code flow with PKCE instead. The implicit flow is considered less secure.
2. **No PKCE support:** The native module does not implement PKCE (Proof Key for Code Exchange)
3. **No JWT validation:** Native `auth_oauth` validates tokens by calling the UserInfo endpoint, not by verifying JWT signatures locally
4. **No group sync:** There is no native mapping from Entra security groups to Odoo groups
5. **No token refresh:** The implicit flow does not support refresh tokens. When the session expires, the user must re-authenticate.

### 6.4 OCA Alternatives

The **OCA `auth_oidc` module** (see Section 7) addresses CE limitations 1-3 above by adding:
- Authorization code flow with client secret
- JWKS-based JWT signature validation
- Proper token endpoint usage

---

## 7. OCA `auth_oidc` -- Authorization Code Flow Alternative

### 7.1 Module Status

- **Repository:** `OCA/server-auth` branch `18.0`
- **Maturity:** Beta
- **License:** AGPL-3
- **Dependency:** `python-jose` (NOT `jose` from PyPI -- they are different packages)
- **Odoo dependency:** `auth_oauth` (extends it)

### 7.2 What It Adds Over Native `auth_oauth`

| Feature | `auth_oauth` (native) | `auth_oidc` (OCA) |
|---------|----------------------|-------------------|
| Flow type | Implicit (`response_type=token`) | Authorization Code (`response_type=code`) |
| Client secret | Not used | Required |
| Token exchange | N/A | Server-side code-to-token exchange |
| JWT validation | None (calls UserInfo) | JWKS-based RS256 signature verification |
| PKCE | No | No (but code flow is still more secure than implicit) |
| Token URL field | N/A | Added to provider model |
| JWKS URL field | N/A | Added to provider model |

### 7.3 Microsoft Entra Configuration with `auth_oidc`

**Single Tenant:**

| Field | Value |
|-------|-------|
| Provider Name | `Azure AD Single Tenant` |
| Auth Flow | OpenID Connect (authorization code flow) |
| Client ID | `{application-client-id}` |
| Client Secret | `{client-secret-value}` |
| Allowed | Yes |
| Authorization URL | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize` |
| Token URL | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token` |
| JWKS URL | `https://login.microsoftonline.com/{tenant-id}/discovery/v2.0/keys` |
| Scope | `openid email profile` |

**Multi-tenant:**

Same as above, but replace `{tenant-id}` with `common` or `organizations` in all URLs.

### 7.4 Installation

```bash
pip install python-jose[cryptography]
# NOT: pip install jose (different package!)
```

The module extends the `auth.oauth.provider` model with additional fields for Token URL, JWKS URL, and Auth Flow selection.

### 7.5 Assessment for InsightPulseAI

Our SSOT (`infra/ssot/auth/oidc_clients.yaml`) specifies `authorization_code_pkce` as the target grant type and references `auth_oauth + ipai_auth_oidc`. The OCA `auth_oidc` module is at Beta maturity, which per our OCA governance rules (`.claude/rules/oca-governance.md`) means it is NOT cleared for production use (Stable minimum required).

Options:
1. **Phase 1:** Use native `auth_oauth` with implicit flow (works today, CE native, no extra deps)
2. **Phase 2:** Build `ipai_auth_oidc` extending `auth_oauth` with authorization code + PKCE support, using OCA `auth_oidc` as a reference

---

## 8. Google OAuth Comparison

### 8.1 Google API Console Setup

1. Go to [Google API Dashboard](https://console.developers.google.com/)
2. Create or select a project
3. Configure **OAuth consent screen** (Internal for Workspace, External for personal accounts)
4. Go to **Credentials** > **Create Credentials** > **OAuth client ID**
5. Application type: **Web Application**
6. Authorized redirect URI: `https://erp.insightpulseai.com/auth_oauth/signin`
7. Copy the **Client ID**

### 8.2 Odoo Setup for Google

1. Go to **Settings > General Settings > Integrations**
2. Enable **OAuth Authentication**
3. Enable **Google Authentication**
4. Paste the **Client ID**
5. Save

Google is simpler because the provider already exists in Odoo's default data. You only need to enable it and add the Client ID.

### 8.3 Key Differences from Microsoft

| Step | Microsoft | Google |
|------|----------|--------|
| System parameter | Must add `auth_oauth.authorization_header = 1` | Not needed |
| Provider creation | Must create from scratch | Already exists, just enable |
| Client secret | Not needed (implicit) | Not needed (implicit) |
| Azure token config | Must enable Access tokens + ID tokens | N/A |
| Settings UI shortcut | None (must go to OAuth Providers) | Dedicated Google Authentication toggle |
| Redirect URI format | Same: `/auth_oauth/signin` | Same: `/auth_oauth/signin` |
| User linking flow | Same: password reset page | Same: password reset page |

### 8.4 Google Provider Fields (For Reference)

Pre-configured in `auth_oauth_data.xml`:
```xml
<record id="provider_google" model="auth.oauth.provider">
    <field name="name">Google OAuth2</field>
    <field name="auth_endpoint">https://accounts.google.com/o/oauth2/auth</field>
    <field name="scope">openid profile email</field>
    <field name="validation_endpoint">https://www.googleapis.com/oauth2/v3/userinfo</field>
    <field name="css_class">o_auth_oauth_provider_icon o_google_provider</field>
    <field name="body">Sign in with Google</field>
    <field name="enabled" eval="False"/>
</record>
```

---

## 9. Security Considerations

### 9.1 Implicit Flow Risks

Odoo's native `auth_oauth` uses implicit flow, which has known security weaknesses:
- Access token exposed in browser URL fragment/history
- No client authentication (client secret not used)
- No refresh tokens -- session relies on access token validity
- Microsoft recommends authorization code flow with PKCE instead

**Mitigation:** The `fragment_to_query_string` JavaScript converts the fragment to a full page redirect, so the token is transmitted to the server and does not persist in browser history after the redirect completes.

### 9.2 State Parameter / CSRF Protection

Odoo's `auth_oauth` includes a `state` parameter in the OAuth request containing:
```json
{
  "d": "database_name",
  "p": provider_id,
  "r": "redirect_url_after_login",
  "t": "optional_signup_token",
  "c": {}
}
```

The state is JSON-serialized and passed through the OAuth flow. On callback, Odoo verifies:
- The database name (`d`) matches a valid database
- The provider ID (`p`) exists
- The redirect URL (`r`) is used for post-login navigation

**Weakness:** The state is not cryptographically signed or bound to the session. It is a JSON object, not an opaque CSRF token. A more robust implementation would include an HMAC or nonce.

### 9.3 Token Validation

Native `auth_oauth`:
- Calls the UserInfo endpoint with the access token
- Trusts the response from the UserInfo endpoint
- Does NOT verify JWT signatures locally
- Does NOT check token audience, issuer, or expiry claims

OCA `auth_oidc`:
- Downloads JWKS from the provider
- Verifies the ID token signature (RS256)
- Validates standard JWT claims

### 9.4 The `auth_oauth.authorization_header` Parameter

When set to `1`:
- Token is sent as `Authorization: Bearer <token>` header to the UserInfo endpoint
- This is the standard OAuth2 bearer token usage per RFC 6750
- Required by Microsoft Graph API
- More secure than query parameter transmission (tokens in query strings may be logged by proxies/servers)

When not set (default `0`/missing):
- Token is sent as `?access_token=<token>` query parameter
- Works for Google, Facebook, Odoo.com
- NOT supported by Microsoft Graph

### 9.5 Session Security

After OAuth login, Odoo creates a standard session:
- Session cookie: `session_id` (HttpOnly, Secure when behind HTTPS)
- Session lifetime: controlled by `session_expiry` setting
- Session is server-side (not JWT-based)
- The OAuth access token is stored on the user record (`oauth_access_token` field) but is NOT used for subsequent API calls -- Odoo uses its own session mechanism

---

## 10. Gmail Add-On Integration Implications

### 10.1 Current Architecture

The InsightPulseAI Gmail add-on needs to authenticate users against the Odoo 18 CE instance. The add-on opens `/web/login` for provider auth in a browser window.

### 10.2 Login Flow from Gmail Add-On

1. Add-on opens `https://erp.insightpulseai.com/web/login` in an authorization popup (CardService.newAuthorizationAction)
2. User sees the Odoo login page with "Log in with Microsoft Azure" button
3. User clicks the Microsoft button, authenticates via Microsoft
4. OAuth callback to `/auth_oauth/signin` creates an Odoo web session
5. The popup shows the Odoo home page (or a custom landing page)

### 10.3 Session Detection Challenge

After successful OAuth login, the add-on needs to detect that the user is authenticated. Options:

**Option A: Custom Landing Page**
- Set the OAuth redirect parameter (`r` in state) to a custom page like `/ipai/auth/success`
- This page returns a simple JSON or HTML that the add-on can detect
- The add-on's `authorizationUrl` callback can use `RELOAD_ADD_ON` action after the popup closes

**Option B: Session Cookie Inspection**
- After OAuth login, the Odoo `session_id` cookie is set for `erp.insightpulseai.com`
- The add-on can make a subsequent `UrlFetchApp.fetch` call to `/web/session/get_session_info` to verify the session
- However, the Gmail add-on runs server-side (Google Apps Script) and does NOT share cookies with the popup browser

**Option C: Token Bridge Endpoint (`/ipai/mail_plugin/provider_session`)**
- After OAuth login, the custom landing page generates a one-time token
- The add-on exchanges this token for an API credential via a bridge endpoint
- This is the most robust approach for server-side add-ons

### 10.4 Bridge Endpoint Design

The endpoint `/ipai/mail_plugin/provider_session` needs to:
1. Accept the one-time token from the add-on (generated during OAuth callback)
2. Validate the token against the Odoo session
3. Return an API key or session token that the add-on can use for subsequent Odoo API calls
4. The token should be short-lived (5-10 minutes) and single-use

### 10.5 What the Add-On Can Use After Auth

Once authenticated, the add-on can call Odoo's JSON-RPC API:
- `/web/session/get_session_info` -- verify session validity
- `/web/dataset/call_kw` -- execute Odoo model methods
- `/jsonrpc` -- general JSON-RPC endpoint
- `/mail_plugin/partner/get` -- native Odoo mail plugin endpoint (if `mail_plugin` module installed)

### 10.6 First-Time Linking Requirement

The first time a user connects the Gmail add-on with Microsoft OAuth, the user **must** be on the Odoo password reset page to link their Microsoft account. After the initial link, subsequent logins work seamlessly.

For the Gmail add-on, this means:
- New users must complete the account linking via the password reset flow BEFORE the add-on auth flow will work
- Or: the add-on's auth popup must direct to the password reset URL for first-time users

---

## 11. InsightPulseAI Exact Configuration

### 11.1 Entra App Registration

**Existing registration** (from `ssot/entra/app_registrations.azure_native.yaml`):

| Setting | Value |
|---------|-------|
| Display Name | `InsightPulseAI Odoo Login` |
| Application (client) ID | `07bd9669-1eca-4d93-8880-fd3abb87f812` |
| Supported account types | Single tenant |
| Redirect URI (Web) | `https://erp.insightpulseai.com/auth_oauth/signin` |
| Access tokens | Enabled |
| ID tokens | Enabled |
| API Permission | `User.Read` (Delegated, Microsoft Graph) |

Tenant: `ceoinsightpulseai.onmicrosoft.com` (custom domain: `insightpulseai.com`)

### 11.2 Odoo System Parameter

| Key | Value |
|-----|-------|
| `auth_oauth.authorization_header` | `1` |

### 11.3 Odoo OAuth Provider Record

| Field | Value |
|-------|-------|
| Provider name | `Azure` |
| Client ID | `07bd9669-1eca-4d93-8880-fd3abb87f812` |
| Authorization URL | `https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize` |
| UserInfo URL | `https://graph.microsoft.com/oidc/userinfo` |
| Scope | `openid profile email` |
| Data Endpoint | *(empty)* |
| CSS class | `fa fa-fw fa-windows` |
| Login button label | `Microsoft Azure` |
| Allowed | True |

Replace `{tenant-id}` with the actual Directory (tenant) ID from Azure portal.

### 11.4 Verification Steps

After configuration, verify:

1. **Login page shows button:** Navigate to `https://erp.insightpulseai.com/web/login` and confirm "Log in with Microsoft Azure" button appears
2. **OAuth redirect works:** Click the button, confirm redirect to `login.microsoftonline.com`
3. **Redirect URI matches:** After Microsoft auth, confirm redirect back to `https://erp.insightpulseai.com/auth_oauth/signin`
4. **User linking:** Test with a user who has reset their password -- they should be able to link via the Microsoft button
5. **Subsequent login:** After linking, test direct login via the Microsoft button on `/web/login`
6. **System parameter:** Verify via Settings > Technical > System Parameters that `auth_oauth.authorization_header = 1` exists

### 11.5 SSOT Cross-References

| File | What It Tracks |
|------|---------------|
| `ssot/entra/app_registrations.azure_native.yaml` | Entra app registration details, client ID, redirect URIs |
| `infra/ssot/auth/oidc_clients.yaml` | OIDC client configuration, IdP endpoints, provider settings |
| `ssot/contracts/odoo_integration.yaml` | Integration contract: `auth_oauth` module, redirect URI |
| `ssot/contracts/identity.yaml` | Identity contract: redirect URI reference |

---

## 12. Troubleshooting

### 12.1 AADSTS50011: Redirect URI Mismatch

**Error:** `AADSTS50011: The redirect URI specified in the request does not match the redirect URIs configured for the application.`

**Causes:**
- Redirect URI in Azure app registration does not exactly match what Odoo sends
- Protocol mismatch (`http://` vs `https://`)
- Trailing slash difference
- Odoo behind a reverse proxy sending `http://` instead of `https://`

**Fix:**
1. Check the exact redirect URI in the error message
2. Add that exact URI to the Azure app registration under Authentication > Redirect URIs
3. Ensure Odoo's `web.base.url` system parameter is set to `https://erp.insightpulseai.com`
4. If behind a reverse proxy (Azure Front Door), ensure `proxy_mode = True` in Odoo config or use `ipai_aca_proxy` module to fix `X-Forwarded-Proto` handling

### 12.2 "Access Denied" After OAuth Callback

**Causes:**
- No matching Odoo user for the Microsoft email
- User signup/creation is disabled
- The user has not completed the initial account linking via password reset

**Fix:**
1. Ensure the user exists in Odoo with the same email as their Microsoft account
2. Check Settings > General Settings > Customer Account for signup policy
3. Have the user go through the password reset flow first

### 12.3 Login Page Does Not Show Microsoft Button

**Causes:**
- `auth_oauth` module not installed
- OAuth provider record not marked as "Allowed"
- OAuth Authentication not enabled in Settings

**Fix:**
1. Install `auth_oauth` module: `odoo-bin -d odoo -i auth_oauth --stop-after-init`
2. Enable OAuth Authentication in Settings > Integrations
3. Verify the provider record has `enabled = True`

### 12.4 Token Validation Fails (500 Error)

**Causes:**
- `auth_oauth.authorization_header` system parameter not set to `1`
- Microsoft Graph userinfo endpoint rejects query parameter tokens
- Network connectivity issue to `graph.microsoft.com`

**Fix:**
1. Set `auth_oauth.authorization_header = 1` in system parameters
2. Verify network access from Odoo server to `graph.microsoft.com` (port 443)
3. Check Odoo logs for the exact HTTP response from Microsoft Graph

### 12.5 Token Expiry / Session Timeout

The implicit flow does not provide refresh tokens. When the access token expires:
- The user's Odoo session may still be valid (session != token lifetime)
- The `oauth_access_token` stored on `res.users` becomes stale
- This does NOT affect the Odoo web session -- only matters if something tries to reuse the stored token

Odoo session timeout is controlled by `session_expiry` configuration, independent of the OAuth token lifetime.

### 12.6 Debug Logging

Enable auth_oauth debug logging:

```python
# In odoo.conf or command line:
log_handler = odoo.addons.auth_oauth:DEBUG
```

Or set the log level via Settings > Technical > Logging (developer mode).

Key log messages:
- `OAuth2: access denied` -- authentication failed
- `auth_signup not installed on database` -- `auth_signup` module missing
- `Exception during request handling` -- generic error in OAuth callback

### 12.7 Admin Consent Required

If the Azure app requires admin consent for `User.Read`:
1. Go to Azure portal > App registrations > Your app > API permissions
2. Click "Grant admin consent for [organization]"
3. Confirm

This is typically needed only once per tenant.

---

## 13. Sources

### Official Odoo 18.0 Documentation
- [Microsoft Azure sign-in authentication](https://www.odoo.com/documentation/18.0/applications/general/users/azure.html)
- [Google Sign-In Authentication](https://www.odoo.com/documentation/18.0/applications/general/users/google.html)
- [Connect Microsoft Outlook 365 to Odoo using Azure OAuth](https://www.odoo.com/documentation/18.0/applications/general/email_communication/azure_oauth.html)

### Odoo 18.0 Source Code (GitHub)
- [auth_oauth/models/auth_oauth.py](https://github.com/odoo/odoo/blob/18.0/addons/auth_oauth/models/auth_oauth.py)
- [auth_oauth/models/res_users.py](https://github.com/odoo/odoo/blob/18.0/addons/auth_oauth/models/res_users.py)
- [auth_oauth/controllers/main.py](https://github.com/odoo/odoo/blob/18.0/addons/auth_oauth/controllers/main.py)
- [auth_oauth/data/auth_oauth_data.xml](https://github.com/odoo/odoo/blob/18.0/addons/auth_oauth/data/auth_oauth_data.xml)
- [auth_oauth/__manifest__.py](https://github.com/odoo/odoo/blob/18.0/addons/auth_oauth/__manifest__.py)

### OCA server-auth
- [auth_oidc (18.0 branch)](https://github.com/OCA/server-auth/tree/18.0/auth_oidc)
- [auth_oidc on PyPI](https://pypi.org/project/odoo-addon-auth-oidc/)

### Microsoft Learn
- [Microsoft identity platform and OAuth 2.0 authorization code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow)
- [OpenID Connect on the Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc)
- [Microsoft identity platform UserInfo endpoint](https://learn.microsoft.com/en-us/entra/identity-platform/userinfo)
- [Error AADSTS50011 troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/app-integration/error-code-aadsts50011-redirect-uri-mismatch)
- [OAuth 2.0 implicit grant flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-implicit-grant-flow)

### Odoo Community Forum
- [Azure OAuth issue](https://www.odoo.com/forum/help-1/azure-oauth-issue-245773)
- [Odoo Redirect error in Azure AD](https://www.odoo.com/forum/help-1/odoo-redirect-error-in-azure-ad-157794)

### GitHub Issues
- [OAuth2 Authentication: Implicit Flow vs Authorization Code Flow (odoo/odoo#63965)](https://github.com/odoo/odoo/issues/63965)
- [OAuth authentication uses Implicit Flow without nonce (odoo/odoo#63750)](https://github.com/odoo/odoo/issues/63750)

### InsightPulseAI SSOT
- `ssot/entra/app_registrations.azure_native.yaml` -- Entra app registration SSOT
- `infra/ssot/auth/oidc_clients.yaml` -- OIDC client configuration SSOT
- `ssot/contracts/odoo_integration.yaml` -- Integration contract
- `ssot/contracts/identity.yaml` -- Identity contract

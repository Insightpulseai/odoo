# zoho-mail-bridge — Edge Function

OAuth2 token minting + email send via Zoho Mail API.

## Deploy

```bash
supabase functions deploy zoho-mail-bridge --project-ref spdtwktxdalcfigzeqrz
```

## Required Secrets

Set these in Supabase Dashboard → Edge Functions → zoho-mail-bridge → Secrets:

| Variable | Description |
|----------|-------------|
| `ZOHO_CLIENT_ID` | OAuth2 client ID from Zoho API Console |
| `ZOHO_CLIENT_SECRET` | OAuth2 client secret |
| `ZOHO_REFRESH_TOKEN` | Long-lived refresh token (generated via auth code flow) |
| `ZOHO_ACCOUNT_ID` | Zoho Mail account ID (run `GET /api/accounts` to find) |

`SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are injected automatically by Supabase.

## Routes

### `POST /functions/v1/zoho-mail-bridge?action=mint_token`

Mints a new Zoho API access token using the stored refresh token.
Tokens are cached in memory for `expires_in - 60s`.

**Response**:
```json
{ "ok": true, "expires_at": 1708550400000 }
```

### `POST /functions/v1/zoho-mail-bridge?action=send_email`

Sends an email via Zoho Mail API.

**Request body**:
```json
{
  "from": "business@insightpulseai.com",
  "to": "recipient@example.com",
  "subject": "Hello from InsightPulse AI",
  "htmlBody": "<p>Hi there!</p>",
  "replyTo": "support@insightpulseai.com"
}
```

`to` can be a string or an array of strings.

**Response**:
```json
{ "ok": true }
```

## Audit Trail

Every `mint_token` and `send_email` call produces a row in `ops.platform_events`:

| Column | Value |
|--------|-------|
| `event_type` | `token_mint` or `email_send` |
| `actor` | `zoho-mail-bridge` |
| `target` | email address(es) or `zoho_oauth` |
| `status` | `ok` or `error` |
| `error_detail` | error message if status = error |

## Zoho OAuth2 Setup (one-time manual)

1. Go to https://api-console.zoho.com → Add Client → Server-based
2. Scopes: `ZohoMail.messages.CREATE`, `ZohoMail.accounts.READ`
3. Redirect URI: `https://erp.insightpulseai.com/oauth/callback`
4. Generate auth code, exchange for refresh token
5. Store `client_id`, `client_secret`, `refresh_token` in Supabase Vault (see `infra/supabase/vault_secrets.tf`)
6. Set as Edge Function secrets (step above)

## Get ZOHO_ACCOUNT_ID

```bash
curl -H "Authorization: Zoho-oauthtoken <access_token>" \
  https://mail.zoho.com/api/accounts
```

Returns `data[0].accountId` — use that value for `ZOHO_ACCOUNT_ID`.

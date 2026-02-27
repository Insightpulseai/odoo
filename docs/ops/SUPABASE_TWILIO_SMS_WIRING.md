# Ops: Supabase Phone OTP — Twilio SMS Wiring

> SSOT guide for wiring Twilio SMS/WhatsApp OTP into Supabase Auth.
> Last updated: 2026-02-22

---

## Environment Variables (Supabase Vault)

All values stored in Supabase Vault — never in git.

| Env Var | Format | Notes |
|---------|--------|-------|
| `TWILIO_ACCOUNT_SID` | `ACxxxxxxxx...` (34 chars) | Twilio Console → Account Info |
| `TWILIO_AUTH_TOKEN` | 32-char hex string | **Rotate immediately if exposed in plaintext** |
| `TWILIO_MESSAGE_SERVICE_SID` | `MGxxxxxxxx...` (34 chars) | See "Messaging Service" below — **required for WhatsApp** |

To set (after rotation):

```bash
supabase secrets set \
  TWILIO_ACCOUNT_SID=ACxxxxxxxx... \
  TWILIO_AUTH_TOKEN=<new_rotated_token> \
  TWILIO_MESSAGE_SERVICE_SID=MGxxxxxxxx...
```

## config.toml Stanza

This stanza **must** exist in `supabase/config.toml`. The linter must NOT remove it.
Values are env var refs — no secrets in the file.

```toml
[auth.sms.twilio]
enabled = true
account_sid = "env(TWILIO_ACCOUNT_SID)"
auth_token = "env(TWILIO_AUTH_TOKEN)"
message_service_sid = "env(TWILIO_MESSAGE_SERVICE_SID)"
```

**Protected by**: `infra/policy/auth-sms-twilio.contract.toml`

## Creating the Twilio Messaging Service

A Messaging Service SID (`MG...`) is required. The registered phone number
(`+15703545535`) must be added to the sender pool.

Steps:

1. Log in to Twilio Console
2. Messaging → Services → Create Messaging Service
3. Add `+15703545535` to the sender pool
4. Copy the SID (format: `MGxxxxxxxx...`)
5. Run: `supabase secrets set TWILIO_MESSAGE_SERVICE_SID=MG...`
6. Re-add `[auth.sms.twilio]` stanza to `supabase/config.toml` (see above)

This is a `[MANUAL_REQUIRED]` step — Twilio Console only.

## Auth Token Rotation (Required)

The Twilio Auth Token was exposed in cleartext during session 2026-02-22.
**Rotate immediately**:

1. Twilio Console → Account → Auth Tokens → Rotate Primary Auth Token
2. Copy new token
3. `supabase secrets set TWILIO_AUTH_TOKEN=<new_token>`
4. Verify Supabase Auth SMS still works with test OTP

## WhatsApp OTP

WhatsApp OTP requires the Messaging Service SID (`MG...`), not a direct phone number.
Ensure the Messaging Service has WhatsApp enabled in Twilio Console.

Client call:
```javascript
const { data, error } = await supabase.auth.signInWithOtp({
  phone: '+639XXXXXXXXX',
  options: { channel: 'whatsapp' }  // or 'sms'
})
```

## Evidence Required

After completing Twilio wiring:
- [ ] `supabase secrets list` shows all three Twilio vars present
- [ ] `config.toml` `[auth.sms.twilio]` stanza committed
- [ ] Test OTP received on `+15703545535` (or test phone)
- [ ] Evidence saved: `web/docs/evidence/<stamp>/twilio-otp/`

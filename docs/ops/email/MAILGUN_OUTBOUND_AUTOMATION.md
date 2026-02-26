# Mailgun Outbound Automation

Automate Cloudflare DNS publication and Mailgun domain verification for `mg.insightpulseai.com`.

---

## Prerequisites / Secrets

All secrets are passed as environment variables. Never commit them to git.

| Variable | Description |
|----------|-------------|
| `CF_API_TOKEN` | Cloudflare API token with `Zone:DNS:Edit` permission on `insightpulseai.com` |
| `MAILGUN_API_KEY` | Mailgun API key (Primary or domain sending key) |
| `MAILGUN_DOMAIN` | Optional. Defaults to `mg.insightpulseai.com` |

---

## Step 1: Generate DNS Artifact

```bash
bash scripts/generate-dns-artifacts.sh
```

- **SSOT source**: `infra/dns/mailgun_mg_insightpulseai_com.yaml`
- **Output**: `artifacts/dns/cloudflare_records.json`
- **Records generated**: SPF (TXT), DKIM (TXT), CNAME (mail tracking), DMARC (TXT)

---

## Step 2: Apply to Cloudflare (Idempotent)

**Dry run** (preview changes, no mutations):

```bash
CF_API_TOKEN=$CF_API_TOKEN python3 scripts/apply_dns_cloudflare.py --dry-run
```

**Apply** (create/patch records):

```bash
CF_API_TOKEN=$CF_API_TOKEN python3 scripts/apply_dns_cloudflare.py
```

Behavior:
- Creates record if missing
- Patches record if content differs
- No-ops if record already matches

---

## Step 3: Trigger Mailgun Verification

```bash
MAILGUN_API_KEY=$MAILGUN_API_KEY python3 scripts/verify_mailgun_domain.py
```

- Exits `0` when SPF + DKIM both pass AND domain status is `active`
- Use `--check-only` to inspect current state without triggering a verification cycle

---

## Re-run Behavior

All steps are idempotent. Re-running `apply_dns_cloudflare.py` when records already exist is safe. Re-running `verify_mailgun_domain.py` re-checks verification status.

---

## Expected Final State

- Mailgun dashboard shows `mg.insightpulseai.com` as **Active** / **Verified**
- Outbound email from `no-reply@mg.insightpulseai.com` delivers with DKIM pass in headers
- `artifacts/dns/cloudflare_records.json` reflects the 4 published records

---

## Odoo Mail Server Sequence

| Sequence | Server | Purpose |
|----------|--------|---------|
| 1 | Zoho API (`ipai_zoho_mail_api`) | Primary outbound |
| 2 | Mailgun SMTP (`mg.insightpulseai.com`) | Fallback / bulk |

Do **not** change these sequences. Zoho API remains the primary transport.

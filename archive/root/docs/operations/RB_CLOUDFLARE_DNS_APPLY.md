# Runbook: Cloudflare DNS SSOT Apply

> Script: `infra/cloudflare/scripts/apply_dns_from_yaml.py`
> SSOT: `infra/dns/zoho_mail_dns.yaml` (and other DNS YAML files)

## Purpose

Keep Cloudflare DNS records in sync with the committed YAML SSOT. Eliminates manual dashboard edits as the primary apply path.

## Preconditions

| Requirement | Notes |
|-------------|-------|
| `CLOUDFLARE_API_TOKEN` | Token with `Zone:DNS Records:Edit` permission for `insightpulseai.com` — see Token Scope below |
| `CLOUDFLARE_ZONE_ID` | Zone ID for `insightpulseai.com` (from Cloudflare dashboard → Zone Overview) |
| `pyyaml` installed | `pip install pyyaml` |
| Python 3.8+ | Uses `urllib` (stdlib only, no requests dependency) |

### Token Scope Requirements

Create a **Custom Token** (not a Global API Key) at
`https://dash.cloudflare.com/profile/api-tokens`:

| Setting | Value |
|---------|-------|
| **Permissions** | Zone — DNS Records — **Edit** |
| **Zone Resources** | Include — Specific zone — `insightpulseai.com` |
| **IP filtering** | Optional: restrict to CI runner IPs for extra security |

> **Why "Edit" and not "Read"**: The apply script creates and updates records.
> Read-only tokens work for `--verify` only; they will return HTTP 403 on
> create/update operations.
>
> **Least-privilege note**: `Zone:DNS Records:Edit` grants write access to ALL
> DNS record types (A, CNAME, MX, TXT, etc.) in the zone. There is no
> per-record-type permission in Cloudflare's token model. Scope to the
> specific zone (not "All zones") to minimize blast radius.
>
> **DKIM TXT records**: Cloudflare imposes a 2048-char limit on TXT record
> content. The Zoho DKIM key used here is within that limit. If you rotate to
> a larger key, verify against this limit before applying.

### Verify Token Permissions Before Apply

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  https://api.cloudflare.com/client/v4/user/tokens/verify | python3 -m json.tool
```

Expected: `"status": "active"` and permissions include `dns_records:edit`.

## Inputs

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | `infra/dns/zoho_mail_dns.yaml` | Path to DNS SSOT YAML file |
| `--dry-run` | off | Preview changes without applying |
| `--verify` | off | Read-only check that all records exist |

## Usage

```bash
# Set credentials (never commit these)
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ZONE_ID="your-zone-id"

# Preview changes (safe to run anytime)
python3 infra/cloudflare/scripts/apply_dns_from_yaml.py --dry-run

# Apply (idempotent — safe to re-run)
python3 infra/cloudflare/scripts/apply_dns_from_yaml.py

# Verify records are present
python3 infra/cloudflare/scripts/apply_dns_from_yaml.py --verify
```

## Outputs

| Status | Meaning |
|--------|---------|
| `✅ CREATED` | Record did not exist — created |
| `✅ UPDATED` | Record existed but content drifted — updated |
| `⏭  NO-OP` | Record already matches YAML — no change |
| `❌ FAILED` | Cloudflare API error — check token/zone permissions |

## Verification Checklist

After apply, confirm with DNS queries:

```bash
# MX records (should show all 3 Zoho MX entries)
dig MX insightpulseai.com +short

# SPF
dig TXT insightpulseai.com +short | grep spf

# DKIM (should return the v=DKIM1; k=rsa; p=... value)
dig TXT zoho._domainkey.insightpulseai.com +short

# DMARC
dig TXT _dmarc.insightpulseai.com +short
```

Expected outputs:
- MX: `10 mx.zoho.com`, `20 mx2.zoho.com`, `50 mx3.zoho.com`
- SPF: `v=spf1 include:zoho.com ~all`
- DKIM: `v=DKIM1; k=rsa; p=MIIBIjAN…`
- DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@…`

## Rollback Strategy

DNS changes are additive (script never deletes). To roll back:

1. Revert `infra/dns/zoho_mail_dns.yaml` to the previous committed value
2. Re-run `apply_dns_from_yaml.py` — it will update the record back to the previous content
3. Verify with `dig` commands above

## Security Notes

- `CLOUDFLARE_API_TOKEN` must be set as a GitHub Actions secret (`CLOUDFLARE_API_TOKEN`) — never committed
- `CLOUDFLARE_ZONE_ID` is not sensitive (it's in the URL) but still kept in secrets for hygiene
- The script prints only the first 40 chars of DKIM key content in logs — full key never echoed

## CI Usage (manual dispatch)

See `.github/workflows/dns-ssot-apply.yml` for GitHub Actions workflow.
Only runs on `workflow_dispatch` — never auto-triggered on push.

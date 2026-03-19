# Integration Audit Scripts

Idempotent scripts to audit DNS, Mailgun, Supabase, and Vercel integrations.

## Quick Start

```bash
# Copy and configure environment (for API-based checks)
cp scripts/audit/env.example scripts/audit/.env
# Edit .env with your credentials

# Run DNS audit (no API keys required)
bash scripts/audit/check_dns.sh

# OR use Python version with DNS-over-HTTPS (network-restricted environments)
python3 scripts/audit/check_dns_doh.py

# Run Mailgun audit (requires MAILGUN_API_KEY)
source scripts/audit/.env
bash scripts/audit/check_mailgun.sh

# Run Supabase audit (CLI or API mode)
bash scripts/audit/check_supabase.sh

# Run Vercel audit (requires VERCEL_TOKEN)
bash scripts/audit/check_vercel.sh

# Generate opportunities assessment
python3 scripts/audit/assess_opportunities.py
```

## Scripts

| Script | Purpose | Requirements |
|--------|---------|--------------|
| `check_dns.sh` | Validate DNS records against expected config | `dig` CLI |
| `check_dns_py.py` | DNS validation using dnspython | Python 3, dnspython |
| `check_dns_doh.py` | DNS validation using DNS-over-HTTPS | Python 3 |
| `check_mailgun.sh` | Audit Mailgun domain verification | MAILGUN_API_KEY |
| `check_supabase.sh` | Audit Supabase project (CLI or API) | supabase CLI or SUPABASE_ACCESS_TOKEN |
| `check_vercel.sh` | Audit Vercel projects | VERCEL_TOKEN |
| `assess_opportunities.py` | Generate opportunity backlog from audit results | Python 3 |

## Configuration

### dns_expected.yaml

Define expected DNS records:

```yaml
domain: insightpulseai.com
records:
  - { name: "@", type: "A", value: "178.128.112.214" }
  - { name: "mg", type: "TXT", value_contains: "v=spf1 include:mailgun.org" }
```

### env.example

API credentials template. Copy to `.env` and fill in values.

## Outputs

All outputs go to `out/`:

- `out/dns_audit.json` - DNS record validation results
- `out/mailgun_audit.json` - Mailgun domain verification status
- `out/supabase_audit.json` - Supabase project inventory
- `out/vercel_audit.json` - Vercel projects inventory
- `out/INTEGRATIONS_OPPORTUNITIES.md` - Generated opportunity backlog

## Network Requirements

- `check_dns.sh` requires UDP DNS (port 53) access
- `check_dns_doh.py` requires HTTPS (port 443) to Cloudflare DNS
- API scripts require HTTPS to respective service endpoints

In network-restricted environments, create placeholder JSON outputs and run full audit from a machine with network access.

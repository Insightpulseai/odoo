# Integrations & Opportunities Assessment (Automated)

_Generated: 2026-01-26T09:39:03.523822Z_

## Inputs Collected
- DNS audit: 0/14 records passing
- Mailgun audit: not run
- Supabase audit: not run
- Vercel audit: not run

## Opportunity Backlog (Ranked)
### 1. [DNS / Infrastructure] Remediate 14 failing DNS record(s)
**Why:** Missing or misconfigured DNS records affect service reachability and email deliverability.

**Evidence:** `www.insightpulseai.com (CNAME), insightpulseai.com (A), mcp.insightpulseai.com (A), n8n.insightpulseai.com (A), erp.insightpulseai.com (A)`

**Next steps (CLI):**
- Review failing records in out/dns_audit.json
- Update DNS provider with correct values
- Re-run check_dns.sh to verify


# Constitution: Cloudflare DNS IaC

## Purpose
Manage insightpulseai.com DNS records via Terraform (Cloudflare) with CI plan-on-PR and apply-on-main.

## Non-negotiables
- Cloudflare is DNS SSOT
- No secrets in repo (.env forbidden)
- Least-privilege GitHub Actions token permissions
- Apply only on main, never on PR

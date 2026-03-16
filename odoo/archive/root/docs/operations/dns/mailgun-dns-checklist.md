# Mailgun DNS Gap Analysis — mg.insightpulseai.com

> **Status**: Gap analysis only — not an action plan for re-enabling Mailgun.
> Mailgun was deprecated 2026-02-01 in favour of Zoho Mail SMTP.
> This checklist documents what records exist, what is missing, and what
> must be cleaned up to eliminate DNS drift in Cloudflare.
>
> SSOT: `infra/dns/subdomain-registry.yaml`
> Workflow: Edit YAML → run `scripts/dns/generate-dns-artifacts.sh` → commit → Terraform apply

---

## 1. What Mailgun Typically Requires

For a custom sending domain (`mg.insightpulseai.com`) Mailgun requires the
following DNS records to be present in the domain's authoritative DNS zone:

| # | Record Type | Name | Purpose | Proxied? |
|---|-------------|------|---------|---------|
| 1 | TXT | `mg` | SPF — authorises Mailgun servers to send on behalf of the domain | No |
| 2 | TXT | `mx._domainkey.mg` | DKIM signature key (primary) | No |
| 3 | TXT | `krs2._domainkey.mg` (or `pic._domainkey.mg`) | DKIM signature key (secondary / rotation) | No |
| 4 | TXT | `_dmarc.mg` | DMARC policy for the sending subdomain | No |
| 5 | CNAME | `email.mg` | Email tracking (open/click) — resolves to `mailgun.org` | No |
| 6 | MX | `mg` | Inbound mail routing (required only if using Mailgun inbound) | No |

> Mailgun Cloudflare note: All Mailgun DNS records **must not** be orange-clouded
> (Cloudflare proxy disabled). DKIM signing and tracking CNAMEs break when proxied.

---

## 2. Records Currently Present in Cloudflare

These four records are confirmed present in Cloudflare as of 2026-02-27
(source: `infra/dns/subdomain-registry.yaml` § `deprecated.mg.records_to_remove`):

| Record Type | Name | Content | Status |
|-------------|------|---------|--------|
| CNAME | `email.mg` | `mailgun.org` | Present — scheduled for removal |
| TXT | `mg` | `v=spf1 include:mailgun.org ~all` | Present — scheduled for removal |
| TXT | `mx._domainkey.mg` | `k=rsa; p=MIGfMA0...` (truncated) | Present — scheduled for removal |
| TXT | `_dmarc.mg` | `v=DMARC1; p=none; ...` (truncated) | Present — scheduled for removal |

These records have `dns_removed: false` in the SSOT — meaning Terraform has **not
yet removed them** from Cloudflare. They will be deleted on the next `terraform apply`
after the deprecated block is processed.

---

## 3. Records That Are Missing

The following records were **never provisioned** and are confirmed absent:

| Record Type | Name | Expected Value | Gap Reason |
|-------------|------|----------------|------------|
| CNAME | `email.mg` (tracking) | `<MAILGUN_TRACKING_CNAME_TARGET>` | The existing `email.mg` CNAME points to `mailgun.org` (basic delivery endpoint) — the *tracking* CNAME may require a different target. Confirm in dashboard. |
| TXT | `krs2._domainkey.mg` | `<MAILGUN_DKIM2_VALUE>` | Second DKIM key for signing rotation — never added. Mailgun may label this `krs2` or `pic` depending on account vintage. |
| MX | `mg` | `mxa.mailgun.org` / `mxb.mailgun.org` (10/10) | Only required for Mailgun inbound routing. Not provisioned because InsightPulse AI does not use Mailgun inbound. |

> **Placeholder convention**: Values wrapped in `<ANGLE_BRACKETS>` must be
> obtained from the Mailgun dashboard before any record can be activated.
> Path: Mailgun dashboard → Sending → Domains → `mg.insightpulseai.com` → DNS Records.

---

## 4. Current State Matrix

| Record | Required | Present | Missing | Action |
|--------|----------|---------|---------|--------|
| SPF TXT (`mg`) | Yes (if sending) | Yes | — | Remove (Mailgun deprecated) |
| DKIM #1 (`mx._domainkey.mg`) | Yes (if sending) | Yes | — | Remove (Mailgun deprecated) |
| DKIM #2 (`krs2._domainkey.mg`) | Yes (if sending) | No | **MISSING** | Add placeholder in SSOT; remove when Mailgun cleanup complete |
| DMARC (`_dmarc.mg`) | Recommended | Yes | — | Remove (Mailgun deprecated) |
| Tracking CNAME (`email.mg`) | Yes (if tracking) | Partial (points to delivery, not tracking) | Tracking target unverified | Confirm target in dashboard; remove when cleanup complete |
| Inbound MX (`mg`) | Only for inbound | No | N/A — not needed | No action |

---

## 5. Remediation Steps

### 5a. Clean Up (remove stale Mailgun records)

These records are already flagged in `infra/dns/subdomain-registry.yaml`
under `deprecated.mg.records_to_remove`. Execute the Terraform apply:

```
# After verifying no active Mailgun traffic:
scripts/dns/generate-dns-artifacts.sh
terraform -chdir=infra/cloudflare/envs/prod plan
terraform -chdir=infra/cloudflare/envs/prod apply
```

Expected result: 4 records deleted from Cloudflare (`email.mg`, `mg` SPF,
`mx._domainkey.mg`, `_dmarc.mg`).

### 5b. Add Missing Records (if Mailgun sending ever reinstated)

> This step is **not recommended** — Mailgun is deprecated. Document only for completeness.

1. Log in to Mailgun dashboard.
2. Navigate to Sending → Domains → `mg.insightpulseai.com` → DNS Records.
3. Copy the exact value for:
   - Second DKIM record name (e.g., `krs2._domainkey.mg`) and its TXT content.
   - Tracking CNAME target (if different from `mailgun.org`).
4. Update `infra/dns/subdomain-registry.yaml`:
   - Replace `<MAILGUN_TRACKING_CNAME_TARGET>` with the real value.
   - Replace `<MAILGUN_DKIM2_VALUE>` with the real DKIM key string.
   - Set `lifecycle: active` and `provider_claim.status: claimed` with `claimed_at`.
5. Run generator and apply Terraform.

### 5c. ops subdomain — Activated

The `ops` subdomain (`ops.insightpulseai.com`) has been activated as part of
this change set:

- `lifecycle`: `planned` → `active`
- `provider_claim.status`: `unclaimed` → `claimed`
- `provider_claim.claimed_at`: `2026-03-01`
- `provider_claim.claim_ref`: `vercel:odooops-console`

Terraform will provision the CNAME `ops.insightpulseai.com → cname.vercel-dns.com`
on next apply. Vercel will then serve the OdooOps Console at `ops.insightpulseai.com`.

---

## 6. SSOT References

| Artifact | Path |
|----------|------|
| DNS SSOT (edit this) | `infra/dns/subdomain-registry.yaml` |
| Generator script | `scripts/dns/generate-dns-artifacts.sh` |
| Terraform config | `infra/cloudflare/envs/prod/` |
| CI enforcement | `.github/workflows/dns-sync-check.yml` |
| Cloudflare DNS ops doc | `docs/ops/CLOUDFLARE_DNS_SSOT.md` |
| Outbound email routing | `docs/ops/email/OUTBOUND_ROUTING.md` |
| Mailgun automation (deprecated) | `docs/ops/email/MAILGUN_OUTBOUND_AUTOMATION.md` |

---

*Created: 2026-03-01 | Author: agent fix/dns-mailgun-ops-activation*

# Mailgun DNS Records — Placeholder Replacement

**Failure codes**: `DNS.MAILGUN.DKIM2_MISSING`, `DNS.MAILGUN.TRACKING_CNAME_MISSING`
**Severity**: medium
**CI behavior**: non-blocking
**SSOT**: `ssot/errors/failure_modes.yaml`
**Convergence kind**: `dns_placeholder`
**Targets**: `krs2._domainkey.mg.insightpulseai.com`,
             `email.mg.insightpulseai.com`

---

## What it means

Two Mailgun DNS records are still listed as planned/placeholder in
`infra/dns/subdomain-registry.yaml`. Until they are replaced with real values
and applied via Terraform, Mailgun email tracking and DKIM2 signing will not work.

Records required:
- `krs2._domainkey.mg` — TXT record (second Mailgun DKIM key)
- `email.mg` — CNAME record (Mailgun click/open tracking)

---

## Get the real values from Mailgun

1. Mailgun Dashboard → Sending → Domains → `mg.insightpulseai.com`
2. Click "DNS Records" (or "Domain Verification")
3. Locate:
   - **DKIM2**: TXT record for `krs2._domainkey.mg` — copy the full TXT value
   - **Tracking CNAME**: CNAME for `email.mg` pointing to `mailgun.org`

---

## Replace placeholders in the DNS SSOT

Edit `infra/dns/subdomain-registry.yaml`. Find the lifecycle `planned` entries for
`email.mg` and `krs2._domainkey.mg`. Replace placeholder values with actual values
from the Mailgun dashboard.

Example (replace `<PLACEHOLDER>` with real values):
```yaml
- name: email.mg
  type: CNAME
  value: "mailgun.org"      # actual value from Mailgun dashboard
  lifecycle: active         # change from planned to active

- name: krs2._domainkey.mg
  type: TXT
  value: "v=DKIM1; k=rsa; p=<actual-public-key>"   # from Mailgun dashboard
  lifecycle: active
```

---

## Regenerate DNS artifacts

```bash
bash scripts/generate-dns-artifacts.sh
```

This updates:
- `infra/cloudflare/envs/prod/subdomains.auto.tfvars`
- `docs/architecture/runtime_identifiers.json`
- `infra/dns/dns-validation-spec.json`

Do not hand-edit generated files.

---

## Commit and merge

```bash
git add infra/dns/subdomain-registry.yaml
git add infra/cloudflare/envs/prod/subdomains.auto.tfvars
git add docs/architecture/runtime_identifiers.json
git add infra/dns/dns-validation-spec.json
git commit -m "fix(dns): provision Mailgun DKIM2 and tracking CNAME records"
git push origin <branch>
```

Open a PR to main. On merge, the `dns-ssot-apply.yml` CI workflow applies via Terraform.

---

## Verify after Terraform apply

```bash
# Wait 2-5 minutes for DNS propagation, then:
dig TXT krs2._domainkey.mg.insightpulseai.com +short
dig CNAME email.mg.insightpulseai.com +short
```

Return to Mailgun Dashboard → Domain Verification → click "Verify DNS Settings".
Both records should show as verified.

---

## Related files

- `infra/dns/subdomain-registry.yaml` (edit this, not generated files)
- `scripts/generate-dns-artifacts.sh` (regenerate after editing)
- `ssot/errors/failure_modes.yaml` (entries: `DNS.MAILGUN.*`)
- `supabase/functions/ops-convergence-scan/index.ts` (dns_placeholder check)

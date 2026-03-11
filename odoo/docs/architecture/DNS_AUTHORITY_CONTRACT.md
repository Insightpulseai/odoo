# DNS Authority Contract — `insightpulseai.com`

> **Single authority. One apply path. No exceptions.**

---

## Zone Authority

| Field | Value |
|-------|-------|
| **Zone** | `insightpulseai.com` |
| **SSOT file** | `infra/dns/subdomain-registry.yaml` |
| **Generator** | `scripts/generate-dns-artifacts.sh` |
| **Apply repo** | `Insightpulseai/odoo` **only** |
| **Apply workflow** | `.github/workflows/cloudflare-dns-apply.yml` |
| **Drift detection** | `.github/workflows/cloudflare-dns-drift.yml` |

---

## Rules (Non-Negotiable)

### 1. Single claim ledger
`infra/dns/subdomain-registry.yaml` is the **only** file where DNS records for
`insightpulseai.com` are defined. No other file or repo may define, create, or
modify records for this zone.

### 2. YAML-first workflow
```
1. Edit   infra/dns/subdomain-registry.yaml
2. Run    scripts/generate-dns-artifacts.sh
3. Commit all generated artifacts together
4. PR     into main
5. CI     cloudflare-dns-apply.yml applies via Terraform on merge
```
Direct Cloudflare API calls, dashboard edits, and manual `terraform apply`
outside this workflow are **banned**.

### 3. No dual writers
Other repos **must not** contain `cloudflare_record` or `cloudflare_zone`
Terraform resources targeting `insightpulseai.com`. Violation fails CI
(`scripts/ci/check_dns_dual_writer.py`).

Permitted patterns in other repos:
- Read-only data sources (`data "cloudflare_zone"`)
- References to exported record artifacts (read-only JSON from this repo)
- PRs to this repo requesting new records

### 4. Break-glass procedure
If an emergency DNS change is required outside the normal PR flow:

1. Create a `break-glass/YYYY-MM-DD-<reason>` branch in this repo.
2. Make the minimum-scope change to `subdomain-registry.yaml`.
3. Run the generator.
4. Apply manually with a scoped token: `CF_API_TOKEN=<read-write> terraform apply`.
5. Immediately open a PR to land the change via normal path.
6. Document the break-glass in `docs/runbooks/DNS_BREAKGLASS_LOG.md`.

Break-glass tokens expire after 24h and must be rotated on next business day.

---

## Generated Artifacts (Do Not Edit By Hand)

| File | Generator |
|------|-----------|
| `infra/cloudflare/envs/prod/subdomains.auto.tfvars` | `generate-dns-artifacts.sh` |
| `docs/architecture/runtime_identifiers.json` | `generate-dns-artifacts.sh` |
| `infra/dns/dns-validation-spec.json` | `generate-dns-artifacts.sh` |
| `artifacts/dns/cloudflare_records.json` | `generate-dns-artifacts.sh` |

---

## Consumer Repos

Other repos that consume DNS records from this SSOT must read from the generated
artifact `artifacts/dns/cloudflare_records.json`. They **must not** re-implement
record definitions.

| Repo | Allowed | Forbidden |
|------|---------|-----------|
| `ipai-ops-platform` | Read exported `cloudflare_records.json` | Define `cloudflare_record` resources for `insightpulseai.com` |
| Any other | Reference domain names from `runtime_identifiers.json` | Manage the Cloudflare zone |

---

## CI Enforcement

| Check | Workflow | What it blocks |
|-------|----------|----------------|
| Provider claims | `cloudflare-authority-gate.yml` (job: provider-claims) | Merging records without confirmed claim |
| NS delegation | `cloudflare-authority-gate.yml` (job: authority-check) | Merging before NS is delegated |
| Dual-writer scan | `cloudflare-authority-gate.yml` (job: dual-writer-scan) | Other repos containing zone-write resources |
| Drift detection | `cloudflare-dns-drift.yml` | Live DNS diverging from SSOT |
| Sync check | `dns-sync-check.yml` | Generated artifacts out of sync with SSOT |

---

*Last updated: 2026-02-28 — added after ipai-ops-platform shelf record conflict identified.*

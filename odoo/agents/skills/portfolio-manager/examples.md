# Examples — portfolio-manager

## Example 1: Quarterly planning review — healthy state

**Input**: Q2-2026 planning review, 3 platform OKRs, 24 work items, 1 FTE equivalent

**Output**:
- Planning period: Q2-2026
- OKR hierarchy: VALID (3 platform OKRs cascade from 2 enterprise OKRs)
- Orphan work items: 0
- Goals without key results: 0
- Capacity status: WITHIN_LIMITS (72% utilization, 28% buffer)
- Maintenance buffer: ADEQUATE (28% > 20% minimum)
- Milestone risks: 1 low-risk
  - "Databricks first pipeline" — dependency on Azure credential provisioning (external, ETA unknown)
- Evidence: `docs/evidence/20260401-0900/portfolio/Q2-2026/`

## Example 2: Overallocated quarter with orphans

**Input**: Q1-2026 mid-quarter review, 5 platform OKRs, 41 work items, 1 FTE equivalent

**Output**:
- Planning period: Q1-2026 (mid-quarter)
- OKR hierarchy: INVALID
  - Platform OKR "Launch marketplace integrations" has no parent enterprise OKR
  - Team OKR "Build Slack bot v2" cascades from retired platform OKR
- Orphan work items: 7
  - `IPAI-234`: "Investigate Vercel edge caching" — Vercel is deprecated
  - `IPAI-267`: "Add Mattermost webhook" — Mattermost is deprecated
  - `IPAI-301`-`IPAI-305`: 5 items from cancelled project scope
- Goals without key results: 1
  - "Improve developer experience" — no quantified metric
- Capacity status: OVERALLOCATED (118% utilization)
- Maintenance buffer: INSUFFICIENT (0% — fully committed)
- Milestone risks: 2 high-risk
  - "EE parity 80%" — 12 modules behind schedule, no capacity for catch-up
  - "Azure migration complete" — blocked on DNS cutover approval
- Remediation:
  1. Archive 7 orphan work items (5 cancelled, 2 reference deprecated systems)
  2. Add parent enterprise OKR for marketplace integrations or defer to Q2
  3. Retire cascading team OKR from deleted platform goal
  4. Quantify "developer experience" — e.g. "reduce devcontainer boot time from 4min to 90s"
  5. Defer 8 work items to Q2 to bring utilization to 78%

## Example 3: Milestone gate check

**Input**: Pre-release gate for milestone "P1 MVP ERP" — 6 prerequisites defined

**Output**:
- Planning period: P1-2026 milestone gate
- Prerequisites:
  - [PASS] Core Odoo modules installed and health-checked
  - [PASS] Azure PG Flexible Server provisioned
  - [PASS] Keycloak SSO configured
  - [FAIL] BIR tax compliance module tests — 3 test failures in `test_bir_vat_compute`
  - [PASS] DNS records applied via Terraform
  - [FAIL] Backup/restore procedure validated — no evidence log found
- Gate status: BLOCKED (2 of 6 prerequisites failed)
- Milestone risk: HIGH — cannot release P1 MVP ERP
- Remediation:
  1. Fix `test_bir_vat_compute` failures (classified as `real defect` per testing policy)
  2. Execute backup/restore drill and capture evidence to `docs/evidence/{stamp}/portfolio/P1-gate/`
  3. Re-run gate check after remediation

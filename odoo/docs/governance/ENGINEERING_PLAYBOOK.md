# Engineering Execution Playbook

> This document describes how we build, verify, and improve systems at InsightPulseAI.
> It is the authoritative public statement of our engineering doctrine.

---

## Core Workflow

```
explore → plan → implement → verify → commit
```

Every non-trivial change follows this sequence. No exceptions.

---

## 1. Version Control

- **Branching**: Trunk-based with short-lived feature branches
- **Commits**: `feat|fix|refactor|docs|test|chore(scope): description` — no generic "fix" or "update"
- **History**: Preserved for traceability. Squash only when commits add noise, not information.
- **SSOT**: DNS, agent instructions, URL maps, and migrations are all version-controlled — no console-only changes

---

## 2. Spec-First Development

All significant features require a spec bundle before code is written:

```
spec/<feature-slug>/
├── constitution.md  — non-negotiable constraints (what this must never do)
├── prd.md           — what to build (user needs, acceptance criteria)
├── plan.md          — how to build it (technical approach, trade-offs)
├── tasks.md         — work breakdown (atomic, assignable units)
└── checklist.md     — quality gates (verified before ship)
```

**39 spec bundles** are active in this repo. Spec Kit is enforced by CI
(`.github/workflows/speckit-gate.yml`) — changes touching spec paths must pass completeness checks.

This discipline prevents the most common failure mode: building the wrong thing correctly.

---

## 3. Testing Strategy

- **Unit tests**: Core logic, business rules, model methods
- **Integration tests**: System boundaries — Supabase ↔ Odoo, n8n ↔ Supabase, API ↔ ERP
- **E2E**: Only where failure is expensive (finance workflows, auth flows, data sync)
- **CI gates**: 272 GitHub workflows enforce correctness before merge — not as bureaucracy, but as repeatability
- **Coverage is a tool, not a goal** — meaningful coverage over metric-chasing

---

## 4. Code Review Principles

- All non-trivial changes are reviewed before merge
- Review focus: correctness, clarity, and minimal impact — not style preferences
- Reviews surface implicit assumptions that authors miss
- Reviews are learning tools, not gatekeeping — the goal is understanding, not approval

---

## 5. CI/CD Architecture

**Pre-commit** (runs locally before every commit):
- lint, typecheck, secret scanning
- pre-commit hooks prevent bad state from ever entering the tree

**Pull Request gates**:
- Contract validation: cross-domain changes require a `docs/contracts/` entry
- SSOT drift detection: DNS, agent instructions, and URL mappings checked on every PR
- Spec Kit completeness for changes touching `spec/`
- Vendor patch verification for dependency changes

**Evidence archival** (every significant change):
- Timestamped logs in `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/`
- Never claim "tests pass" or "secure" without a log path

---

## 6. Monitoring & Observability

- Systems are observable by default — Supabase Realtime, n8n execution logs, Odoo server logs
- Infrastructure changes tracked in Terraform state (DigitalOcean, Cloudflare)
- Service health verified post-deployment via `scripts/health/` scripts, not manual browser checks
- Incidents are documented, not blamed — `docs/incidents/` for post-mortems

---

## 7. Continuous Improvement

Every correction feeds back into process — not just fixed and forgotten:

- Lessons captured when a pattern proves wrong (SSOT updated, not just one file patched)
- Architecture decisions recorded in `docs/adr/` before implementation begins
- This playbook is itself a living document — updated when doctrine evolves, not just when something breaks
- The goal is a system that improves over time, not just one that ships features

---

## 8. Security & Secrets

| Rule | Enforcement |
|------|-------------|
| Secrets: Supabase Vault + GitHub Actions secrets only | Pre-commit secret scanning |
| Never hardcode credentials in source | CI secret scanner, GHAS |
| Schema changes via migrations only — no ad-hoc SQL | SSOT rule, reviewed in PR |
| DNS changes: YAML-first, Terraform-applied, never console-direct | `infra/dns/` SSOT + CI |
| Cross-domain integration changes require a contract doc | `docs/contracts/` + CI gate |

---

## Stack

| Layer | Technology |
|-------|-----------|
| ERP | Odoo 19 Community Edition + OCA modules |
| Custom modules | 48 `ipai_*` integration bridges |
| Database | PostgreSQL 16 (self-hosted, DigitalOcean) |
| Control plane | Supabase (Auth, Vault, Edge Functions, Realtime, pgvector) |
| Automation | n8n (workflow orchestration) |
| Frontend | Next.js + TypeScript (Vercel) |
| Hosting | DigitalOcean (self-hosted services) |
| DNS/CDN | Cloudflare (YAML-SSOT → Terraform) |
| Container runtime | Docker (self-hosted) |
| IaC | Terraform |
| AI agents | Claude Code (plan-first, evidence-driven) |

---

## Anti-Patterns (What We Don't Do)

| Anti-pattern | Why |
|-------------|-----|
| Console-only infrastructure changes | No audit trail, no rollback |
| Skipping spec for "small" changes | Small changes become large incidents |
| Claiming "tests pass" without a log path | Unverifiable claims erode trust |
| Hardcoding credentials | Security baseline, non-negotiable |
| Creating modules in `addons/oca/` | OCA is read-only; use `ipai_*` overrides |
| Merging to main without CI green | CI exists to catch what humans miss |

---

*Last updated: 2026-02-26 | Maintained in `Insightpulseai/odoo`*
*Referenced from: [insightpulseai org profile](https://github.com/insightpulseai)*

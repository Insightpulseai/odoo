# TaxPulse Salvage Map

## Source

Legacy precursor repo: `jgtolentino/TaxPulse-PH-Pack`

## Classification

Packaged PH tax/compliance sub-agent system with:

- Odoo module surface (BIR forms, tax computation, agency mappings)
- PH rules pack (JSONLogic, rate tables, thresholds)
- AI review engine (scoring, rubric, protocol-driven evaluation)
- Supabase-backed review/state layer (run logs, protocol tables)

## Salvage targets

### Odoo repo (`odoo/addons/local/taxpulse_ph_pack/`)

- BIR form models and workflows
- Account-move tax computation logic
- Agency/entity tax mappings
- Security/access control
- Reporting surfaces

### Agents repo (`agents/packages/taxpulse_ph/`)

- Finance Tax Pulse review agent (`engine/`)
- Scoring/rubric logic
- Packaged skills and authority sources (`skills/`)
- Specialist compliance prompts
- Review protocol orchestration

### Platform repo (`platform/supabase/taxpulse/`)

- Supabase schema and migrations
- Review log tables
- Protocol seed data
- Edge Function contracts
- Run state persistence

### Docs/spec

- Benchmark doctrine and evaluation specs
- Compliance protocol documentation
- Migration evidence and notes
- Product/plan/task artifacts from `spec/` and `specs/`

## Benchmark mapping

Use TaxPulse-derived specialist agent as the candidate benchmark surface against AvaTax for:

- tax accuracy
- compliance control
- auditability
- AP review workflow fit

Do **not** benchmark generic Odoo Copilot against AvaTax directly.

## Current status

- Legacy repo exists as personal/public precursor
- Not yet absorbed into canonical org repos
- Salvage inventory documented separately

---

*Created: 2026-03-18*

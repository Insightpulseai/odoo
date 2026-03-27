# Architecture Documentation

> Structured reference for InsightPulse AI platform architecture.
> Cross-cutting files remain at this root level; domain-specific docs are organized into subdirectories.

## Directory Index

| Directory | Description |
|-----------|-------------|
| [`target-state/`](target-state/) | Target-state architecture documents (platform, Azure, org, finance) |
| [`agents/`](agents/) | Agent/copilot architecture, benchmarks, factory design, skills |
| [`azure/`](azure/) | Azure platform architecture, DevOps, pipelines, service mapping |
| [`odoo/`](odoo/) | Odoo ERP architecture, runtime, upstream references, copilot modules |
| [`data/`](data/) | Data platform architecture, medallion, ETL, Databricks, schema governance |
| [`tax/`](tax/) | Tax/BIR compliance architecture, TaxPulse migration |
| [`connectors/`](connectors/) | Connector onboarding standards and modes |
| [`identity/`](identity/) | Identity/Entra architecture, secrets management |
| [`integration/`](integration/) | Integration patterns (n8n, A2A, MCP, cloud) |
| [`security/`](security/) | Security architecture, runtime authority, retrieval policy |
| [`adr/`](adr/) | Architecture Decision Records |
| [`operations/`](operations/) | Operating models (reliability, DevSecOps, release, delivery) |
| [`governance/`](governance/) | Repo/org governance, file taxonomy, authority mapping |
| [`saas/`](saas/) | SaaS platform architecture, tenancy, billing, offerings |
| [`marketing/`](marketing/) | Marketing architecture, analytics, agency stack |
| [`w9-studio/`](w9-studio/) | W9 Studio project architecture (Wix audit, website) |
| [`docs-platform/`](docs-platform/) | Documentation platform architecture (Plane unified docs) |
| [`ai/`](ai/) | AI/Foundry architecture, document intelligence, landing zone |
| [`diagrams/`](diagrams/) | Architecture diagrams (pre-existing) |
| [`data-intelligence/`](data-intelligence/) | Data intelligence architecture (pre-existing) |

## Root-Level Files

Cross-cutting documents that span multiple domains remain at this level:

- `GO_LIVE_CHECKLIST.md` / `GO_LIVE_MATRIX.md` — Release gates
- `APPROVED_MICROSOFT_SAMPLES.md` / `SAMPLE_ADOPTION_POLICY.md` — Sample governance
- `CONVERGENCE_REPORT.md` — Platform convergence status
- `reference-benchmarks.md` / `target-capability-map.md` — Cross-domain references
- `diagram-conventions.md` — Diagramming standards
- `ROADMAP_FIELD_AUTHORITY.md` / `ROADMAP_INTEGRATION_DECISIONS.md` — Roadmap decisions
- `PULSER_MINIMAL_RUNTIME.md` — Pulser runtime specification
- `EVAL_ENGINE_HARDENING.md` / `TASK_ROUTER_HARDENING.md` / `RELEASE_GATES_HARDENING.md` — Hardening specs
- `WEB_DEBUGGING_ARCHITECTURE.md` — Web debugging patterns
- `CLAUDE_ALIGNMENT_REPAIR.md` / `SPEC_ALIGNMENT_REPAIR.md` — Alignment repair logs

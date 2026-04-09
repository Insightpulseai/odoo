# Constitution: Odoo Knowledge Surfaces

> Durable architecture decision. Changes require spec-level review.

---

## Purpose

Define the canonical Odoo/OCA agent knowledge architecture for the InsightPulse AI platform. This spec governs how agents discover, retrieve, reason about, and inspect Odoo 18 CE, curated OCA modules, and internal SSOT documentation -- without collapsing retrieval, judgment, and runtime operations into a single unsafe surface.

---

## Core Invariant: Three-Surface Architecture

All Odoo-domain agent knowledge flows through exactly three surfaces. Each surface has a distinct responsibility, distinct tooling, and distinct security posture.

| Surface | Name | Responsibility | V1 Posture |
|---------|------|----------------|------------|
| **A** | Odoo/OCA Docs MCP | Retrieval over curated docs corpus | Read-only retrieval |
| **B** | Odoo/OCA Skills Pack | Promptable decision playbooks | Stateless advisory |
| **C** | Odoo Runtime MCP | Live instance inspection | **Read-only** |

### Surface A: Odoo/OCA Docs MCP

Provides structured retrieval over a curated, versioned knowledge corpus. Sources include Odoo 18 official documentation, curated OCA module metadata, and internal SSOT/spec/runbook documents. This surface answers "what does the documentation say?" -- never "what is the live state?".

### Surface B: Odoo/OCA Skills Pack

Provides promptable decision playbooks for common Odoo implementation tasks. Skills encode judgment heuristics (module selection, debugging strategies, migration paths, parity decisions) and reference Surface A retrieval tools rather than hardcoding doctrine. This surface answers "what should I do?" -- never "what happened?".

### Surface C: Odoo Runtime MCP

Provides live instance inspection via Odoo RPC/ORM. Returns installed module state, model schemas, field definitions, view structures, and sample record metadata from a running Odoo instance. This surface answers "what is the live state?" -- never "what should I do?".

---

## Non-Negotiable Boundaries

1. **Docs retrieval is separate from runtime operations.** Surface A and Surface C must never share a tool namespace, execution context, or authorization scope.

2. **Skills are separate from retrieval tools.** Surface B consumes Surface A as a dependency but is not a retrieval surface itself. Skills encode judgment; retrieval returns facts.

3. **V1 runtime surface is read-only.** Surface C in V1 exposes only inspection endpoints. No `create`, `write`, `unlink`, or `execute` calls against Odoo models. This boundary is enforced by an explicit method allowlist, not by convention.

4. **Corpus must be curated, not broad OCA scraping.** Surface A indexes only modules and docs explicitly listed in the curated source manifest. Unlisted OCA repos are excluded from retrieval results.

5. **Internal SSOT docs are first-class knowledge sources.** Architecture decisions, spec bundles, runbooks, and policy documents from this repo are indexed alongside upstream Odoo/OCA docs. Internal docs take precedence for local architecture and policy questions.

6. **Retrieval, skills, and runtime ops are distinct.** An agent may compose all three surfaces in a single workflow, but each surface maintains its own tool contract, authentication, and audit boundary.

---

## Repo Ownership

| Domain | Owner | Path |
|--------|-------|------|
| Agent-facing contracts | `agents/` | `agents/contracts/odoo-knowledge-surfaces/` |
| Skills definitions | `agents/` | `agents/skills/odoo/` |
| Docs corpus config | `agents/` | `agents/knowledge/` |
| Runtime MCP server | `agents/` or `platform/` | `agents/skills/odoo_runtime/` (V1) |
| Shared ingestion/index infra | `platform/` | Deferred to post-V1 |

---

## V1 Exclusions

These capabilities are explicitly out of scope for V1. Each requires a separate spec amendment with policy gates before implementation.

| Exclusion | Rationale |
|-----------|-----------|
| Write-capable Odoo MCP actions | Safety: uncontrolled mutation of production ERP data |
| Broad autonomous record mutation | Requires maker-checker approval architecture |
| Uncurated full-OCA ingestion | Quality: most OCA repos lack 19.0 branches or stable status |
| Databricks dependency in critical path | Docs and skills retrieval must function without lakehouse availability |

---

## Amendment Process

Changes to this constitution require:
1. A PR updating this file with rationale in the commit message
2. Review by the platform owner
3. Corresponding updates to `prd.md`, `plan.md`, and `tasks.md` in this bundle

---

*Spec bundle: `spec/odoo-knowledge-surfaces/`*
*Created: 2026-03-23*

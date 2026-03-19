# Constitution — Odoo Foundry VS Code Extension

## Purpose

Define the non-negotiable design rules for the Odoo Foundry VS Code Extension.

This extension is a thin developer/operator companion for Odoo workspaces. It is not a replacement for OdooLS, not a full IDE, and not the production agent runtime.

## Principle 1 — Reuse official Odoo language intelligence

The extension must reuse existing Odoo code-intelligence surfaces rather than reimplement them.

In scope:
- detect and cooperate with OdooLS / odoo-vscode
- consume workspace facts from Odoo projects
- add copilot/operator features on top

Out of scope:
- reimplementing autocomplete
- reimplementing hover/go-to-definition
- building a competing Odoo language server

## Principle 2 — Gateway-first AI architecture

The extension must talk to a gateway service that owns orchestration, policy, tool routing, and specialist handoff.

Preferred path:
VS Code extension → Odoo Copilot gateway → Foundry project endpoint / Agent Framework / specialists

The extension must not become the production runtime for orchestration logic.

## Principle 3 — Safe-by-default behavior

The extension starts in read-heavy assisted mode.

Allowed by default:
- explain code/config
- inspect module/view/model context
- summarize findings
- propose changes
- route to specialist capabilities
- trigger safe benchmark/eval helpers

Forbidden by default:
- production writes
- autonomous business actions
- secret mutation
- direct ERP posting/finalization flows
- silent fallback on missing context or missing source support

## Principle 4 — Structured outputs over chat-only UX

Every AI response must support a typed structure, not only free-form text.

Minimum output shape:
- intent
- summary
- findings
- citations or evidence references when available
- suggested next actions
- specialist route if applicable

## Principle 5 — Minimal VS Code UX

Use standard VS Code extension surfaces first:
- commands
- tree views
- activity bar view container
- status bar items
- diagnostics / code actions where appropriate

Use webviews only where a standard surface is insufficient.

## Principle 6 — Workspace truth before prompt cleverness

The extension must prefer actual workspace context over generic prompting.

Examples:
- active file path
- module root
- manifest
- addons path
- active symbol
- XML IDs / models / views
- current repo/runtime metadata if available

## Principle 7 — Auditability and reversibility

All non-trivial actions must be observable.

The extension must support:
- request correlation IDs
- visible action summaries
- explicit approval where needed
- event/audit handoff to the backend gateway

## Principle 8 — Specialist layering, not specialist sprawl

The extension hosts one core shell and routes to specialists.

Initial specialist model:
- core precursor shell
- TaxPulse specialist later

No specialist should bypass the core routing, policy, and audit surface.

## Principle 9 — Benchmarkability

The extension must be designed so core precursor behaviors can be benchmarked against the core benchmark stack and specialist behaviors can be benchmarked separately.

Core benchmark surfaces:
- ERP/business copilot shell
- agentic workspace shell

Specialist benchmark surfaces:
- tax/compliance specialist

## Principle 10 — Cloud IDE friendliness

The extension design must remain compatible with remote/cloud IDE workflows.

No requirement should assume local-only setup if the same workflow can be mediated through the gateway and workspace metadata.

# PRD — Odoo Foundry VS Code Extension

## 1. Summary

Build a VS Code extension that acts as the primary developer/operator companion for Odoo workspaces and the desktop/client entry point for the Odoo Copilot precursor.

The extension will:
- understand Odoo workspace context
- package that context into structured requests
- send requests to the Odoo Copilot gateway
- render structured results in VS Code
- later route specialist requests such as TaxPulse

The extension is not the orchestration runtime. It is the client surface for the precursor.

## 2. Problem

Current Odoo development workflows suffer from:
- fragmented context between code, docs, runtime, and AI tools
- ad hoc prompting with weak awareness of Odoo structure
- lack of a consistent developer/operator copilot surface
- no unified path for routing Odoo-aware AI requests into Foundry-backed orchestration
- no safe, structured bridge from IDE context into future specialists like TaxPulse

Existing Odoo language-server tooling solves code intelligence, but not copilot/orchestration/operator workflows.

## 3. Goals

### Primary goals
1. Deliver a thin VS Code companion for Odoo workspaces.
2. Reuse OdooLS / odoo-vscode instead of replacing them.
3. Package active workspace context into structured requests.
4. Connect to the Odoo Copilot gateway backed by Agent Framework + Foundry.
5. Provide safe, read-heavy developer/operator assistance.
6. Create a client surface that can later route to TaxPulse and other specialists.

### Secondary goals
1. Support memory/personalization settings at the user/workspace level.
2. Support benchmark/eval trigger helpers for precursor development.
3. Support cloud/remote development patterns.

## 4. Non-Goals

1. Rebuilding OdooLS features.
2. Making the extension the production agent runtime.
3. Direct production business writes in v1.
4. Full MCP/tool orchestration inside the extension process.
5. Replacing Odoo web UI for business operations.

## 5. Users

### Primary users
- Odoo developer
- Odoo platform operator
- solution architect
- implementation engineer

### Secondary users
- AI/agent developer
- QA/evaluator
- tax/compliance specialist reviewer (later, routed specialist mode)

## 6. User stories

1. As an Odoo developer, I want the extension to identify the current addon/module and active Odoo object so AI responses are context-aware.
2. As an operator, I want to ask for explanations of current configuration or runtime artifacts without leaving VS Code.
3. As an architect, I want structured suggestions and findings, not only chat text.
4. As a future TaxPulse user, I want the extension to route tax/compliance questions to the right specialist instead of pretending the core shell knows everything.
5. As a reviewer, I want evidence-rich responses and explicit uncertainty when context is missing.

## 7. Product scope

### In scope for v1
- workspace detector
- active-file/context packer
- command palette actions
- sidebar/activity view
- structured result rendering
- gateway transport
- specialist routing stub
- optional memory/preferences page
- audit correlation metadata

### Out of scope for v1
- direct Odoo write-back
- production filing/posting actions
- full benchmark harness inside extension
- autonomous background specialists
- replacement language server

## 8. Functional requirements

### FR-001 Workspace detection
The extension shall detect:
- repo/workspace root
- addon/module root
- manifest file
- active file type
- active Odoo symbol context where inferable

### FR-002 OdooLS cooperation
The extension shall detect and coexist with official Odoo language-intelligence tooling and must not duplicate core language-server capabilities.

### FR-003 Context packaging
The extension shall build a structured context payload from the active editor/workspace.

Example fields:
- workspaceRoot
- moduleName
- filePath
- fileType
- activeSymbol
- manifestSummary
- relatedPaths
- requestIntent

### FR-004 Gateway invocation
The extension shall send structured requests to the Odoo Copilot gateway, not directly embed the full orchestration runtime.

### FR-005 Structured result contract
The extension shall render results using a structured contract including:
- intent
- summary
- findings
- evidence/citations if present
- suggested actions
- specialist route if applicable
- status/error state

### FR-006 Command surface
The extension shall provide commands for at least:
- explain active file
- explain current model/view
- review manifest
- summarize module structure
- route to specialist
- inspect current workspace context

### FR-007 Sidebar surface
The extension shall provide a sidebar or activity view showing:
- detected workspace facts
- recent requests
- recent results
- specialist availability
- connection/health state

### FR-008 Memory/preferences surface
The extension should support a lightweight personalization surface for:
- preferred response style
- default benchmark/eval mode
- preferred context priority
- preferred specialist routing behavior

### FR-009 Audit metadata
The extension shall attach correlation metadata so requests can be traced in the gateway/backend.

### FR-010 Safe default mode
The extension shall default to read-heavy, assisted behavior with no direct production mutation flow.

## 9. Non-functional requirements

### NFR-001 Low coupling to OdooLS internals
The extension must avoid brittle dependency on unstable internal APIs of upstream Odoo tooling.

### NFR-002 Thin client
The extension must keep orchestration logic out of the client and rely on a gateway.

### NFR-003 Failure clarity
Failures must be explicit:
- gateway unavailable
- missing context
- specialist unavailable
- unsupported command
- auth error

### NFR-004 Performance
Basic context extraction and local UI operations should feel near-instant.

### NFR-005 Security
No secrets may be hardcoded in extension settings or source. Auth must use approved credential flows and/or backend mediation.

### NFR-006 UX discipline
The extension should prefer native VS Code primitives over custom webview-heavy UX.

## 10. Architecture

### Client
VS Code extension in TypeScript.

### Dependencies
- official OdooLS / odoo-vscode present or optional
- backend Odoo Copilot gateway
- backend Foundry project / Agent Framework orchestration path

### Gateway responsibilities
- policy enforcement
- Foundry invocation
- specialist routing
- tool registry
- audit/event logging
- memory/session handling

### Extension responsibilities
- detect context
- package request
- invoke gateway
- render result
- manage user-facing commands/preferences

## 11. Benchmark alignment

### Core precursor benchmarks
- ERP/business copilot shell
- agentic workspace shell

### Extension relevance
The extension is not itself the benchmark target, but it must expose the precursor behaviors cleanly enough to support those benchmark surfaces.

## 12. Success metrics

### MVP success
- workspace detection works on real Odoo repos
- structured requests reach the gateway
- structured responses render correctly
- core commands are usable
- specialist routing stub is visible

### Quality success
- no attempt to replace OdooLS
- safe default mode preserved
- failures are diagnosable
- extension remains thin and maintainable

## 13. Risks

1. Overbuilding UI instead of proving the precursor contract.
2. Coupling too tightly to unstable upstream OdooLS behavior.
3. Smuggling orchestration logic into the extension.
4. Adding write-heavy behavior too early.
5. Blurring core precursor and TaxPulse responsibilities.

## 14. MVP definition

The MVP is complete when:
- the extension can detect an Odoo module context
- the user can invoke at least 5 meaningful commands
- the gateway returns structured results
- the extension renders them in commands/sidebar
- specialist handoff is stubbed but visible
- no production-write path exists

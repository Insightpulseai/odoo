# Plan — Odoo Foundry VS Code Extension

## 1. Delivery strategy

Build the extension as a thin client over the core Odoo Copilot precursor.

Do not attempt to solve:
- full language intelligence
- full orchestration
- specialist runtime
inside the extension.

## 2. Build phases

### Phase 0 — Workspace and architecture alignment
Objectives:
- confirm canonical extension name and package scope
- confirm gateway endpoint contract
- confirm Odoo workspace patterns to support first
- confirm auth flow

Outputs:
- final extension package name
- gateway API contract draft
- workspace detection rules

### Phase 1 — Extension skeleton
Objectives:
- create VS Code extension scaffold
- register commands
- add activity bar container
- add status bar entry
- add settings schema

Outputs:
- extension bootstraps in VS Code
- commands visible
- settings visible

### Phase 2 — Odoo workspace detector
Objectives:
- detect addon roots
- detect manifests
- classify active file types
- extract active context

Outputs:
- structured local context object
- context inspector command/view

### Phase 3 — Gateway integration
Objectives:
- implement request transport
- implement structured response parser
- show health/auth state
- surface backend errors cleanly

Outputs:
- explain/review commands return real gateway responses

### Phase 4 — Core UX
Objectives:
- sidebar view
- result renderer
- history/recent actions
- optional lightweight chat view if still needed

Outputs:
- operator/developer usable core interface

### Phase 5 — Specialist routing and memory surface
Objectives:
- specialist handoff stub
- memory/preferences page
- route to TaxPulse placeholder
- route metadata in result model

Outputs:
- visible precursor-to-specialist path

### Phase 6 — Hardening
Objectives:
- telemetry hooks
- request correlation IDs
- retry/backoff rules
- clear offline behavior
- package/build/test hygiene

Outputs:
- extension ready for internal pilot

## 3. Technical design

### Language
TypeScript for the extension.

### UI primitives
Preferred order:
1. commands
2. tree views
3. status bar
4. quick pick / input surfaces
5. webview only if a native surface is insufficient

### Gateway integration pattern
The extension talks to one gateway API surface.

The gateway owns:
- Agent Framework orchestration
- Foundry integration
- tool routing
- specialist routing
- audit/session logic

### Result contract
Minimum result:
- requestId
- intent
- status
- summary
- findings[]
- evidence[]
- suggestedActions[]
- specialistRoute?
- rawReference?

## 4. Dependencies

### Required
- gateway API available
- extension scaffold
- Odoo workspace available

### Optional but preferred
- OdooLS installed
- official odoo-vscode installed
- user signed into approved auth flow

## 5. Testing strategy

### Unit
- workspace detection
- context extraction
- command registration
- result parsing

### Integration
- gateway invocation
- structured result rendering
- error states
- specialist routing stub

### Pilot
- real Odoo repo
- real addon/module navigation
- real gateway response loop

## 6. Rollout

### Milestone A
Local extension skeleton + context inspection

### Milestone B
Gateway-backed explain/review commands

### Milestone C
Sidebar + structured results + specialist stub

### Milestone D
Internal pilot on active Odoo repo

## 7. Risks and mitigations

### Risk: OdooLS instability
Mitigation:
- keep coupling loose
- use workspace detection independent of internal language-server APIs

### Risk: extension becomes orchestration runtime
Mitigation:
- gateway-first contract
- no business workflow logic in client

### Risk: UI overbuild
Mitigation:
- standard VS Code primitives first
- webview only when justified

### Risk: unsafe action scope creep
Mitigation:
- read-heavy default
- no production-write paths in MVP

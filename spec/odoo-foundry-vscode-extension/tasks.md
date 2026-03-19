# Tasks — Odoo Foundry VS Code Extension

## Phase 0 — Alignment
- [ ] Confirm canonical extension slug/package name
- [ ] Confirm repo target for extension implementation
- [ ] Define gateway endpoint contract
- [ ] Define structured request payload schema
- [ ] Define structured response schema
- [ ] Confirm auth and environment assumptions

## Phase 1 — Skeleton
- [ ] Scaffold TypeScript VS Code extension
- [ ] Register extension activation events
- [ ] Add command palette commands
- [ ] Add activity bar container
- [ ] Add status bar item
- [ ] Add extension settings schema

## Phase 2 — Workspace detection
- [ ] Detect repo/workspace root
- [ ] Detect addon/module root
- [ ] Detect manifest file
- [ ] Classify active file type
- [ ] Extract active symbol/file context
- [ ] Add "inspect current Odoo context" command

## Phase 3 — Gateway integration
- [ ] Add gateway client module
- [ ] Add request correlation ID support
- [ ] Add health check / connection state
- [ ] Add explain active file command
- [ ] Add review manifest command
- [ ] Add summarize module command
- [ ] Parse structured gateway responses

## Phase 4 — Core UX
- [ ] Add sidebar tree/view model
- [ ] Add recent requests/results list
- [ ] Add result renderer for findings/evidence/actions
- [ ] Add specialist route visibility
- [ ] Add clean error state rendering

## Phase 5 — Preferences and routing
- [ ] Add user/workspace preferences surface
- [ ] Add memory/preferences payload support
- [ ] Add specialist handoff stub for TaxPulse
- [ ] Add route-aware result rendering

## Phase 6 — Hardening
- [ ] Add local tests for workspace detection
- [ ] Add local tests for result parsing
- [ ] Add integration tests for gateway invocation
- [ ] Add offline/error-path tests
- [ ] Add packaging/build verification
- [ ] Add internal pilot checklist

## Explicit exclusions for MVP
- [ ] No direct production Odoo write actions
- [ ] No autonomous posting/finalization
- [ ] No embedded orchestration runtime
- [ ] No replacement language-server features

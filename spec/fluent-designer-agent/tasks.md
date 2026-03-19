# Tasks — Fluent UI Frontend Designer Agent

## Phase 0 — Repo alignment and contracts
- [ ] Inspect existing web/apps and web/packages conventions
- [ ] Create `web/packages/fluent-designer-contract/` package
- [ ] Define DesignIntent type
- [ ] Define DesignBrief type
- [ ] Define ScreenProposal type
- [ ] Define SectionProposal type
- [ ] Define ComponentRecommendation type
- [ ] Define DesignCritique type
- [ ] Define CritiqueViolation type
- [ ] Define HandoffArtifact type
- [ ] Define DesignerAgentResponse type
- [ ] Define DesignerAgentError type
- [ ] Define DesignerAgentService adapter interface
- [ ] Define ComponentTree input type for critique
- [ ] Define RefineConstraints type
- [ ] Add schema validation for all contracts

## Phase 1 — Skeleton and theme
- [ ] Scaffold React + Fluent UI v9 app at `web/apps/fluent-designer-agent/`
- [ ] Configure Griffel styling
- [ ] Create `web/packages/fluent-designer-theme/` package
- [ ] Set up FluentProvider with theme tokens
- [ ] Define brand token extension points
- [ ] Implement app shell layout (left rail, center, right rail, bottom)

## Phase 2 — Designer workspace UI
- [ ] Implement mode tabs (Generate, Critique, Refine, Handoff)
- [ ] Implement prompt input component
- [ ] Implement saved prompts list (left rail)
- [ ] Implement brief panel (center pane, structured fields)
- [ ] Implement proposal output panel (center pane)
- [ ] Implement component recommendations panel (right rail)
- [ ] Implement rationale panel (right rail)
- [ ] Implement handoff/JSON panel (bottom pane)
- [ ] Implement mode switching state management

## Phase 3 — Prompt parsing and brief generation
- [ ] Create `web/packages/fluent-designer-prompts/` package
- [ ] Implement prompt-to-DesignBrief parser
- [ ] Define prompt templates for 5 starter use cases
- [ ] Render DesignBrief in brief panel
- [ ] Handle parse errors gracefully

## Phase 4 — Proposal engine and mock adapter
- [ ] Implement DesignerAgentService mock adapter
- [ ] Create deterministic fixture: campaign analytics dashboard
- [ ] Create deterministic fixture: enterprise settings page
- [ ] Create deterministic fixture: copilot side-panel
- [ ] Create deterministic fixture: admin list/detail workspace
- [ ] Create deterministic fixture: hero/landing section
- [ ] Implement proposal renderer (layout regions, component cards)
- [ ] Implement token guidance display
- [ ] Implement accessibility notes display
- [ ] Wire Generate mode end-to-end (prompt → brief → adapter → render)

## Phase 5 — Design rules engine and critique
- [ ] Implement rules engine core
- [ ] Add rule: layout hierarchy validation
- [ ] Add rule: whitespace/density compliance
- [ ] Add rule: component appropriateness check
- [ ] Add rule: heading/action consistency
- [ ] Add rule: accessibility basics (contrast, focus, ARIA)
- [ ] Add rule: token usage sanity
- [ ] Add rule: platform-native tone check
- [ ] Implement critique results view (violations, severity, substitutions)
- [ ] Wire Critique mode end-to-end (component tree → rules → violations → render)

## Phase 6 — Handoff generation
- [ ] Implement HandoffArtifact generator
- [ ] Generate implementation brief section
- [ ] Generate Fluent component map section
- [ ] Generate token usage recommendation section
- [ ] Generate acceptance criteria section
- [ ] Generate test checklist section
- [ ] Implement handoff renderer (bottom pane)
- [ ] Add JSON/copy export for handoff artifacts
- [ ] Wire Handoff mode end-to-end

## Phase 7 — Refinement mode
- [ ] Implement Refine mode input (existing proposal + constraints)
- [ ] Implement diff-oriented proposal improvement
- [ ] Render refinement changes with before/after
- [ ] Wire Refine mode end-to-end

## Phase 8 — Testing and hardening
- [ ] Add unit tests: contract/schema validation
- [ ] Add unit tests: design brief parsing
- [ ] Add unit tests: proposal rendering logic
- [ ] Add unit tests: critique rule evaluation
- [ ] Add unit tests: handoff artifact generation
- [ ] Add integration tests: Generate flow
- [ ] Add integration tests: Critique flow
- [ ] Add integration tests: Handoff flow
- [ ] Add integration tests: Refine flow
- [ ] Add accessibility smoke tests (keyboard, screen reader, contrast)
- [ ] Add build/package verification
- [ ] Patch docs/architecture and ssot

## Phase 9 — Backend adapter (Foundry)
- [ ] Add TypeScript Foundry backend adapter contracts
- [ ] Add Foundry client wrapper (DefaultAzureCredential + AIProjectClient)
- [ ] Add agent ensure/reuse layer (explicit ID → name search → create)
- [ ] Add conversation/response execution layer
- [ ] Add response normalization layer
- [ ] Add provider error envelope (DesignerAgentProviderError, DesignerAgentResponseParseError)
- [ ] Add DesignerAgentService service boundary
- [ ] Add Express route handler
- [ ] Add env config loader with validation
- [ ] Add tests: normalization (valid JSON, metadata injection, parse error)
- [ ] Add tests: agent reuse (explicit ID, name search, fallback create)
- [ ] Add tests: execution flow (conversation create/reuse, response normalization)
- [ ] Add tests: service delegation (correlation ID always present)
- [ ] Patch docs/architecture and ssot

## Explicit exclusions for v1
- [ ] No live backend agent runtime
- [ ] No image/screenshot generation
- [ ] No drag-and-drop visual builder
- [ ] No direct Foundry SDK import in frontend
- [ ] No custom styling outside Griffel/Fluent tokens

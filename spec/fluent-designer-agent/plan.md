# Plan — Fluent UI Frontend Designer Agent

## 1. Delivery Strategy

Build the designer agent as a Fluent UI v9 frontend workspace with typed contracts and a mock service adapter. The backend boundary is an adapter interface — swap mock for Foundry-backed later without UI changes.

Do not attempt to solve:
- full agent runtime
- image generation
- drag-and-drop visual building
inside the frontend.

## 2. Build Phases

### Phase 0 — Repo alignment and contracts
Objectives:
- inspect existing web/apps and web/packages conventions
- define typed contracts (DesignBrief, ScreenProposal, DesignCritique, HandoffArtifact, etc.)
- define service adapter interface
- confirm package naming and location

Outputs:
- `fluent-designer-contract` package with all typed contracts
- adapter interface definition
- confirmed file layout

### Phase 1 — Extension skeleton and theme
Objectives:
- scaffold React + Fluent UI v9 app
- configure Griffel styling
- set up Fluent theme provider with brand token extension points
- create `fluent-designer-theme` package

Outputs:
- app bootstraps with Fluent v9
- theme tokens active
- basic layout shell visible

### Phase 2 — Designer workspace UI
Objectives:
- implement workspace layout (left rail, center pane, right rail, bottom pane)
- implement mode tabs (Generate, Critique, Refine, Handoff)
- implement prompt input surface
- implement saved prompts list

Outputs:
- navigable designer workspace
- mode switching works
- prompt input accepts text

### Phase 3 — Prompt parsing and brief generation
Objectives:
- implement `fluent-designer-prompts` package
- parse natural-language requests into DesignBrief
- render brief panel with structured fields

Outputs:
- plain-English input → typed DesignBrief
- brief panel renders intent, constraints, page type

### Phase 4 — Proposal engine and mock adapter
Objectives:
- implement design proposal engine (frontend orchestration)
- implement mock service adapter with deterministic fixtures for 5 starter use cases
- implement proposal renderer (component recommendations, layout regions, tokens, accessibility)

Outputs:
- Generate mode produces ScreenProposal for all 5 use cases
- proposals render in center + right panels

### Phase 5 — Design rules engine and critique
Objectives:
- implement lightweight rules layer (hierarchy, density, component appropriateness, accessibility, tokens)
- implement critique mode (accept component tree → produce DesignCritique)
- implement critique results view (violations, severity, substitutions)

Outputs:
- Critique mode produces violation list with severity
- suggestions reference specific Fluent components

### Phase 6 — Handoff generation
Objectives:
- implement HandoffArtifact generator
- render handoff view (implementation brief, component map, acceptance criteria, test checklist)
- support JSON/copy export of handoff artifacts

Outputs:
- Handoff mode produces machine-parseable artifacts
- coding agents can consume output directly

### Phase 7 — Refinement mode
Objectives:
- implement Refine mode (existing proposal + new constraints → improved proposal)
- show diff-oriented changes

Outputs:
- iterative refinement loop works

### Phase 8 — Testing and hardening
Objectives:
- unit tests for contract validation, brief parsing, proposal rendering, critique, handoff
- integration tests for full mode flows
- accessibility smoke tests
- build/package verification

Outputs:
- test suite green
- accessibility audit clean

## 3. Technical Design

### Language
TypeScript + React

### UI Foundation
Fluent UI React v9 + Griffel

### Packages
| Package | Purpose |
|---------|---------|
| `fluent-designer-contract` | Typed contracts, schemas, validation |
| `fluent-designer-prompts` | Prompt templates, brief parsing |
| `fluent-designer-theme` | Fluent token extensions, brand overrides |

### App structure
```
web/apps/fluent-designer-agent/
  src/
    app/           — app shell, routing, providers
    components/    — shared UI components
    features/
      designer-agent/  — workspace layout, mode orchestration
      design-system/   — rules engine, component registry
      prompting/       — brief parsing, prompt management
    services/      — adapter interface, mock adapter
    contracts/     — re-exports from fluent-designer-contract
    state/         — state management
    theme/         — theme provider, token config
    mocks/         — deterministic fixtures for 5 use cases
```

### Typed contracts (minimum)
```typescript
DesignIntent
DesignBrief
ScreenProposal
SectionProposal
ComponentRecommendation
DesignCritique
CritiqueViolation
HandoffArtifact
DesignerAgentResponse
DesignerAgentError
```

### Service adapter interface
```typescript
interface DesignerAgentService {
  generate(brief: DesignBrief): Promise<DesignerAgentResponse>;
  critique(tree: ComponentTree): Promise<DesignerAgentResponse>;
  refine(proposal: ScreenProposal, constraints: RefineConstraints): Promise<DesignerAgentResponse>;
  handoff(proposal: ScreenProposal): Promise<DesignerAgentResponse>;
  health(): Promise<ServiceHealth>;
}
```

### Mock adapter
Returns deterministic fixtures for:
1. Campaign analytics dashboard
2. Enterprise settings page
3. Copilot side-panel
4. Admin list/detail workspace
5. Hero/landing section

### Gateway integration (later)
The adapter interface is designed so a Foundry-backed implementation can be swapped in without changing UI code. The frontend never directly imports Foundry SDK packages.

## 4. Dependencies

### Required
- Fluent UI React v9 (`@fluentui/react-components`)
- Griffel (bundled with Fluent v9)
- TypeScript
- React 18+

### Optional
- Existing repo state management convention
- Existing repo testing framework
- Existing repo linting/formatting config

## 5. Testing Strategy

### Unit
- contract/schema validation
- design brief parsing
- proposal rendering logic
- critique rule evaluation
- handoff artifact generation

### Integration
- full Generate flow (prompt → brief → proposal → render)
- full Critique flow (tree → violations → render)
- full Handoff flow (proposal → artifact → render)
- mode switching
- error states

### Accessibility
- keyboard navigation through workspace
- screen reader compatibility
- focus management
- contrast validation

## 6. Rollout

### Milestone A — Contracts and skeleton
Typed contracts + app shell + Fluent theme

### Milestone B — Generate mode
Prompt input → brief → proposal with mock adapter

### Milestone C — Critique and Handoff
Critique mode + handoff generation + rules engine

### Milestone D — Full workspace
All 4 modes + 5 use cases + tests green

## 7. Backend Adapter Boundary

The backend runtime isolates Microsoft Foundry integration behind a single adapter layer.
The service contract remains provider-neutral.

Provider implementation targets Foundry runtime concepts:
- **agent** — reusable designer agent identity
- **conversation** — session context for multi-turn interaction
- **response** — single agent response within a conversation

No web surface may depend directly on Foundry SDK APIs.

### Backend adapter location
```
platform/services/designer-agent-api/
  src/
    contracts/         — shared + foundry-specific contracts
    config/            — env loader
    adapters/foundry/  — client, agents, execute, normalize, errors
    services/          — DesignerAgentService
    routes/            — Express route handler
```

### Agent reuse strategy
1. Explicit agent ID → reuse directly
2. Name search via `listAgents` → reuse by name
3. Fallback → create new agent

## 8. Risks and Mitigations

### Risk: Visual drift from Fluent
Mitigation: Fluent-first doctrine enforced in code review; no custom styling outside Griffel/Fluent tokens

### Risk: Rules engine overengineering
Mitigation: Start with 6-8 core rules; add incrementally based on real use

### Risk: Backend coupling
Mitigation: Typed adapter interface; mock adapter proves decoupling

### Risk: Scope creep into visual builder
Mitigation: Structured proposals only; no drag-and-drop in v1

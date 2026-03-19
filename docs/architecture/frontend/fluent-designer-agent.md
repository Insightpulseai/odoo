# Architecture — Fluent UI Frontend Designer Agent

## Overview

The Fluent UI Designer Agent is a frontend workspace that helps generate, review, refine, and hand off Microsoft-native UI compositions. It uses Fluent UI React v9 as its component foundation and communicates with backend services through a typed adapter boundary.

## Position in the Platform

```
                    ┌─────────────────────────────────────┐
                    │     Fluent Designer Agent UI         │
                    │  (React + Fluent UI v9 + Griffel)    │
                    └──────────────┬──────────────────────┘
                                   │
                         DesignerAgentService
                          (typed adapter interface)
                                   │
                    ┌──────────────┴──────────────────────┐
                    │                                      │
              Mock Adapter                     Foundry Adapter (later)
           (deterministic fixtures)        (Azure AI Projects 2.x SDK)
                                                   │
                                           Foundry Agent Service
                                           Agent Framework runtime
```

## Design Doctrine

| Principle | Implication |
|-----------|-------------|
| Fluent-first | Use Fluent v9 components and tokens; no competing design systems |
| Griffel-aligned | All styling through Griffel; no CSS modules, Tailwind, or styled-components |
| Composition over chrome | Build with Fluent primitives; minimize custom visual elements |
| Microsoft-native restraint | Calm, structured, enterprise density; no flashy marketing aesthetics |
| Accessible by default | WCAG 2.1 AA minimum; focus management, ARIA, contrast |
| Deterministic outputs | Structured typed responses; no prose-only results |
| Backend-decoupled | Typed adapter interface; swap mock for Foundry without UI changes |

## Workspace Layout

```
┌─────────┬──────────────────────────────────┬──────────────────┐
│         │                                  │                  │
│  Left   │         Center Pane              │    Right Rail     │
│  Rail   │                                  │                  │
│         │  ┌────────────────────────────┐   │  Component       │
│  Mode   │  │ Prompt Input               │   │  Recommendations │
│  Switch │  └────────────────────────────┘   │                  │
│         │  ┌────────────────────────────┐   │  Token Guidance  │
│  Saved  │  │ Brief Panel                │   │                  │
│  Prompts│  └────────────────────────────┘   │  Accessibility   │
│         │  ┌────────────────────────────┐   │  Notes           │
│         │  │ Proposal / Critique Output │   │                  │
│         │  └────────────────────────────┘   │  Rationale       │
│         │                                  │                  │
├─────────┴──────────────────────────────────┴──────────────────┤
│                     Bottom Pane                                │
│  Handoff Artifact / JSON / Implementation Prompt               │
└────────────────────────────────────────────────────────────────┘
```

## Output Modes

| Mode | Input | Output |
|------|-------|--------|
| Generate | Plain-English design request | ScreenProposal with components, tokens, accessibility |
| Critique | Component tree / screen definition | DesignCritique with violations, severity, substitutions |
| Refine | Existing proposal + new constraints | Diff-oriented improved proposal |
| Handoff | Finalized proposal | HandoffArtifact (impl brief, component map, acceptance criteria) |

## Response Contract

```typescript
type DesignerAgentResponse = {
  mode: "generate" | "critique" | "refine" | "handoff";
  brief: DesignBrief;
  proposal?: ScreenProposal;
  critique?: DesignCritique;
  handoff?: HandoffArtifact;
  rationale: string[];
  warnings: string[];
};
```

## Typed Contracts

| Contract | Purpose |
|----------|---------|
| DesignIntent | What the user wants to achieve |
| DesignBrief | Structured interpretation of intent |
| ScreenProposal | Full page/screen design proposal |
| SectionProposal | Individual region/section proposal |
| ComponentRecommendation | Specific Fluent component suggestion with rationale |
| DesignCritique | Validation results against Fluent rules |
| CritiqueViolation | Individual violation with severity and fix |
| HandoffArtifact | Machine-readable implementation handoff |
| DesignerAgentError | Typed error responses |

## Design Rules Engine

Lightweight validation layer checking:

1. **Layout hierarchy** — correct nesting, clear page structure
2. **Whitespace/density** — enterprise-appropriate spacing, not too sparse or crowded
3. **Component appropriateness** — right Fluent component for the context
4. **Heading/action consistency** — predictable heading levels, action placement
5. **Accessibility basics** — contrast ratios, focus indicators, ARIA landmarks
6. **Token usage sanity** — using Fluent tokens, not hardcoded values
7. **Platform-native tone** — Microsoft-adjacent feel, not consumer/marketing drift

## Package Structure

| Package | Location | Purpose |
|---------|----------|---------|
| `fluent-designer-contract` | `web/packages/fluent-designer-contract/` | Typed contracts and schemas |
| `fluent-designer-prompts` | `web/packages/fluent-designer-prompts/` | Prompt templates and brief parsing |
| `fluent-designer-theme` | `web/packages/fluent-designer-theme/` | Fluent token extensions, brand overrides |

## App Structure

```
web/apps/fluent-designer-agent/
  src/
    app/              — shell, routing, FluentProvider
    components/       — shared Fluent-based UI components
    features/
      designer-agent/ — workspace layout, mode orchestration
      design-system/  — rules engine, component registry
      prompting/      — brief parsing, prompt management
    services/         — adapter interface, mock adapter
    contracts/        — re-exports from contract package
    state/            — state management
    theme/            — theme config, token setup
    mocks/            — deterministic fixtures (5 use cases)
```

## Theming

- Fluent tokens and theming primitives are the baseline
- Brand override only through controlled token extension points
- Microsoft-native baseline preserved even with brand tokens
- No hardcoded spacing/radius/color when Fluent token equivalents exist

## Motion/Interaction

- Subtle, purposeful, low-noise transitions
- State clarity and focus visibility prioritized
- Reduced cognitive load over visual spectacle
- No decorative animation-heavy behavior

## Starter Use Cases

1. Campaign analytics dashboard
2. Enterprise settings page
3. Copilot side-panel
4. Data-heavy admin list/detail workspace
5. Hero/landing section for Microsoft-adjacent product

## Future Backend Integration

The adapter interface is designed for Foundry Agent Service / Azure AI Projects 2.x:

```typescript
interface DesignerAgentService {
  generate(brief: DesignBrief): Promise<DesignerAgentResponse>;
  critique(tree: ComponentTree): Promise<DesignerAgentResponse>;
  refine(proposal: ScreenProposal, constraints: RefineConstraints): Promise<DesignerAgentResponse>;
  handoff(proposal: ScreenProposal): Promise<DesignerAgentResponse>;
  health(): Promise<ServiceHealth>;
}
```

Swapping `MockDesignerAgentService` for `FoundryDesignerAgentService` requires no UI changes.

## Known Limitations

- v1 uses mock adapter only; no live AI generation
- Rules engine is lightweight; not a comprehensive design linter
- No image/screenshot output
- No drag-and-drop composition
- No multi-user collaboration

## Related Specs

- `spec/fluent-designer-agent/prd.md` — product requirements
- `spec/fluent-designer-agent/plan.md` — delivery phases
- `spec/fluent-designer-agent/tasks.md` — implementation tasks
- `ssot/frontend/fluent_designer_agent.yaml` — machine-readable inventory

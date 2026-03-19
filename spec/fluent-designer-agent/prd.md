# PRD — Fluent UI Frontend Designer Agent

## 1. Summary

Build a production-grade frontend "Fluent UI Designer Agent" that helps generate, review, refine, and hand off Microsoft-native UI compositions for internal apps, copilot surfaces, dashboards, forms, admin tools, and productivity workflows.

The agent uses Fluent UI React v9 as its primary component system, produces structured design proposals from prompts/specs, critiques existing screens against Fluent principles, and outputs deterministic handoff artifacts for coding agents.

## 2. Problem

Current internal frontend design workflows suffer from:
- inconsistent application of Fluent UI patterns across surfaces
- ad hoc component selection without structured Fluent alignment
- no automated design critique against Microsoft-native standards
- no deterministic handoff path from design intent to coded implementation
- disconnect between design proposals and the Fluent component/token system
- no structured bridge from natural-language design requests to typed UI briefs

## 3. Goals

### Primary goals
1. Accept plain-English design requests and convert them into structured UI briefs.
2. Produce screen/component proposals aligned with Fluent UI React v9.
3. Critique existing component trees against Fluent alignment rules.
4. Generate deterministic handoff artifacts for coding agents.
5. Maintain a Microsoft-native enterprise feel across all outputs.
6. Keep backend integration behind a typed adapter boundary for later Foundry connection.

### Secondary goals
1. Support saved prompt/brief libraries for reuse.
2. Support brand token extension within Fluent baseline guardrails.
3. Serve as the frontend design surface for the broader copilot ecosystem.

## 4. Non-Goals

1. Replacing Fluent UI itself or forking its component library.
2. Building a full visual design tool (Figma replacement).
3. Implementing the agent backend runtime inside the frontend.
4. Generating pixel-perfect mockups or images.
5. Supporting non-Microsoft design systems.

## 5. Users

### Primary users
- Frontend developer building Microsoft-native internal apps
- Solution architect designing copilot/dashboard surfaces
- Platform operator reviewing UI consistency

### Secondary users
- Design system maintainer
- Coding agent consuming handoff artifacts
- QA engineer validating Fluent compliance

## 6. User Stories

1. As a frontend developer, I want to describe a dashboard in plain English and receive a structured Fluent component proposal.
2. As an architect, I want to paste a component tree and receive critique against Fluent hierarchy, spacing, and component choice.
3. As a developer, I want handoff artifacts that include exact Fluent components, tokens, and acceptance criteria.
4. As a platform operator, I want to verify that a screen proposal meets Microsoft-native density and accessibility standards.
5. As a coding agent, I want machine-readable handoff briefs I can implement without ambiguity.

## 7. Product Scope

### In scope for v1
- Designer workspace UI (prompt input, brief panel, proposal output, component recommendations, rationale, acceptance checklist)
- Four modes: Generate, Critique, Refine, Handoff
- Typed contracts for all data flows
- Fluent design rules engine (lightweight validation layer)
- Deterministic mock service adapter with fixtures
- Five starter use cases (dashboard, settings, copilot panel, admin list/detail, hero section)
- Test coverage for core flows

### Out of scope for v1
- Live backend agent runtime
- Image/screenshot generation
- Drag-and-drop visual builder
- Multi-user collaboration
- Production Foundry SDK integration

## 8. Functional Requirements

### FR-001 Prompt-to-brief parsing
The agent shall accept plain-English design requests and produce a typed DesignBrief.

### FR-002 Screen proposal generation
The agent shall produce a ScreenProposal containing:
- page type and objective
- information hierarchy
- layout regions (header, content, sidebar, footer)
- Fluent component recommendations per region
- token/theming guidance
- accessibility notes
- implementation notes

### FR-003 Design critique
The agent shall accept an existing component tree or screen definition and produce a DesignCritique containing:
- violations (hierarchy, spacing, component choice, contrast, focus, interaction)
- severity per violation
- suggested Fluent component substitutions
- rationale

### FR-004 Refinement
The agent shall accept an existing proposal plus new constraints and produce a diff-oriented improved proposal.

### FR-005 Handoff generation
The agent shall produce HandoffArtifact containing:
- coding-agent implementation brief
- Fluent component map
- token usage recommendation
- acceptance criteria
- test checklist

### FR-006 Design rules engine
The agent shall validate proposals against:
- layout hierarchy correctness
- whitespace/density compliance
- component appropriateness for context
- heading/action consistency
- accessibility basics (contrast, focus, ARIA)
- token usage sanity
- platform-native tone

### FR-007 Structured response contract
Every agent response shall conform to:
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

### FR-008 Designer workspace UI
The workspace shall include:
- Left rail: mode switch + saved prompts
- Center pane: prompt / brief / main response
- Right rail: Fluent component recommendations, tokens, accessibility notes
- Bottom/secondary pane: handoff artifact / JSON / implementation prompt

## 9. Non-Functional Requirements

### NFR-001 Fluent-first styling
All UI must use Fluent UI React v9 components and Griffel-compatible styling. No competing styling systems.

### NFR-002 Typed contracts
All data flows between major modules must use typed contracts. No untyped payloads.

### NFR-003 Performance
Context extraction and local UI operations must feel near-instant. Proposal rendering must complete within 2 seconds for local mock adapter.

### NFR-004 Accessibility
The designer workspace itself must meet WCAG 2.1 AA. Generated proposals must include accessibility guidance.

### NFR-005 Testability
Core flows must have unit and integration test coverage.

### NFR-006 Backend decoupling
The frontend must communicate through a typed service adapter interface. Swapping mock adapter for Foundry-backed adapter must not require UI changes.

## 10. Architecture

### Client
Next.js App Router + React 18 + Fluent UI React v9 + Griffel + TypeScript

Because Fluent UI v9 relies on React context and Griffel client-side behavior, the FluentProvider and all Fluent-heavy surfaces must live behind a `'use client'` boundary under App Router.

### Layers
```
User → Designer Workspace UI (Next.js client components)
     → Prompt/brief parser (fluent-designer-prompts)
     → Design proposal engine (frontend orchestration)
     → Typed service contract (DesignerAgentService adapter)
     → Mock adapter (v1) / Foundry adapter (later)
     → Normalized DesignerAgentResponse
```

### Key packages
- `fluent-designer-contract` — typed contracts and schemas
- `fluent-designer-prompts` — prompt templates and parsing
- `fluent-designer-theme` — Fluent token extensions and brand overrides

## 11. Design Doctrine

- Fluent-first, not custom-first
- Component composition over custom chrome
- Microsoft-native restraint over flashy marketing aesthetics
- Enterprise usability over visual novelty
- Accessible by default
- Responsive and layout-stable
- Deterministic handoff outputs
- Calm, structured, high signal-to-noise
- Restrained motion (state clarity, not spectacle)
- Pragmatic enterprise density

## 12. Starter Use Cases

1. Microsoft-style analytics dashboard for campaign performance
2. Enterprise settings page for admin configuration
3. Copilot side-panel for contextual assistance
4. Data-heavy admin list/detail workspace
5. Hero/landing section for a Microsoft-adjacent product surface

## 13. Success Metrics

### MVP success
- All 5 starter use cases produce valid structured proposals
- Critique mode identifies at least 3 violation types
- Handoff artifacts are machine-parseable
- Designer workspace renders correctly with Fluent v9

### Quality success
- No custom styling that bypasses Fluent tokens
- All contracts are schema-validatable
- Test coverage for core proposal/critique/handoff flows
- Accessibility smoke tests pass

## 14. Risks

1. Over-engineering the rules engine beyond lightweight validation.
2. Introducing visual patterns that drift from Fluent.
3. Coupling frontend logic to a specific backend implementation.
4. Building a visual builder instead of a structured proposal tool.
5. Scope creep into image generation or pixel-perfect mockups.

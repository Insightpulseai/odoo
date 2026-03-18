# App Design Lifecycle Map

**Document:** Figma Design Automation Research
**Date:** 2026-01-20

---

## Overview Diagram (Mermaid)

```mermaid
flowchart TB
    subgraph CONCEPT["1. CONCEPT PHASE"]
        C1[User Research]
        C2[Requirements]
        C3[Information Architecture]
        C1 --> C2 --> C3
    end

    subgraph WIREFRAME["2. WIREFRAME PHASE"]
        W1[Low-Fidelity Wireframes]
        W2[User Flow Diagrams]
        W3[Interaction Patterns]
        W1 --> W2 --> W3
    end

    subgraph MOCKUP["3. MOCKUP PHASE"]
        M1[High-Fidelity Mockups]
        M2[Visual Design]
        M3[Brand Application]
        M1 --> M2 --> M3
    end

    subgraph PROTOTYPE["4. PROTOTYPE PHASE"]
        P1[Interactive Prototypes]
        P2[User Testing]
        P3[Iteration Cycles]
        P1 --> P2 --> P3
    end

    subgraph DESIGN_SYSTEM["5. DESIGN SYSTEM PHASE"]
        DS1[Component Library]
        DS2[Design Tokens/Variables]
        DS3[Documentation]
        DS1 --> DS2 --> DS3
    end

    subgraph DEV_MODE["6. DEV MODE PHASE"]
        DM1[Code Inspection]
        DM2[Asset Export]
        DM3[Code Connect]
        DM4[MCP Server]
        DM1 --> DM2 --> DM3 --> DM4
    end

    subgraph CODE["7. CODE PHASE"]
        CD1[AI Code Generation]
        CD2[Component Development]
        CD3[Backend Integration]
        CD4[Testing]
        CD1 --> CD2 --> CD3 --> CD4
    end

    subgraph PRODUCTION["8. PRODUCTION PHASE"]
        PR1[CI/CD Pipeline]
        PR2[Deployment]
        PR3[Monitoring]
        PR4[Feedback Loop]
        PR1 --> PR2 --> PR3 --> PR4
    end

    CONCEPT --> WIREFRAME
    WIREFRAME --> MOCKUP
    MOCKUP --> PROTOTYPE
    PROTOTYPE --> DESIGN_SYSTEM
    DESIGN_SYSTEM --> DEV_MODE
    DEV_MODE --> CODE
    CODE --> PRODUCTION
    PRODUCTION -->|Iteration| CONCEPT
```

---

## Phase-by-Phase Breakdown

### Phase 1: Concept

| Attribute | Details |
|-----------|---------|
| **Duration** | 1-2 weeks |
| **Input Artifacts** | Business requirements, user research data, competitive analysis |
| **Output Artifacts** | PRD, user personas, journey maps, information architecture |
| **Tools** | FigJam, Miro, Notion, Google Docs |
| **Human Roles** | Product Manager, UX Researcher, Business Analyst |
| **AI Opportunities** | User research synthesis, competitive analysis, persona generation |
| **Version Control** | Notion/Confluence versioning |
| **CI/CD Gates** | Requirements sign-off |

```
User Research Data
       ↓
[AI: Research Synthesis]
       ↓
Personas + Journey Maps
       ↓
[Human: Strategy Validation]
       ↓
Approved PRD
```

---

### Phase 2: Wireframe

| Attribute | Details |
|-----------|---------|
| **Duration** | 1-2 weeks |
| **Input Artifacts** | PRD, information architecture, content inventory |
| **Output Artifacts** | Low-fidelity wireframes, user flows, navigation schema |
| **Tools** | Figma (wireframe mode), FigJam, Balsamiq |
| **Human Roles** | UX Designer, Information Architect |
| **AI Opportunities** | Layout suggestions, flow optimization, component recommendations |
| **Version Control** | Figma version history |
| **CI/CD Gates** | Stakeholder review, usability heuristics check |

```
PRD + IA
    ↓
[AI: Layout Generation]
    ↓
Draft Wireframes
    ↓
[Human: UX Refinement]
    ↓
[AI: Flow Validation]
    ↓
Approved Wireframes
```

---

### Phase 3: Mockup

| Attribute | Details |
|-----------|---------|
| **Duration** | 2-3 weeks |
| **Input Artifacts** | Approved wireframes, brand guidelines, content |
| **Output Artifacts** | High-fidelity mockups, visual design specs, responsive variants |
| **Tools** | Figma Design Mode, Adobe Creative Suite |
| **Human Roles** | Visual Designer, Brand Designer |
| **AI Opportunities** | Color harmony suggestions, typography pairing, responsive variants |
| **Version Control** | Figma branches, version history |
| **CI/CD Gates** | Brand compliance check, accessibility contrast check |

```
Wireframes + Brand Guide
          ↓
[Human: Visual Design]
          ↓
High-Fidelity Mockups
          ↓
[AI: Responsive Variant Generation]
          ↓
[AI: Accessibility Pre-Check]
          ↓
Approved Mockups
```

---

### Phase 4: Prototype

| Attribute | Details |
|-----------|---------|
| **Duration** | 1-2 weeks |
| **Input Artifacts** | High-fidelity mockups, interaction requirements |
| **Output Artifacts** | Interactive prototypes, user test recordings, iteration logs |
| **Tools** | Figma Prototyping, Figma Make, ProtoPie |
| **Human Roles** | Interaction Designer, UX Researcher |
| **AI Opportunities** | Interaction suggestions, user behavior prediction, test analysis |
| **Version Control** | Figma version history, prototype links |
| **CI/CD Gates** | Usability test pass rate (>80%) |

```
Mockups + Interaction Specs
           ↓
[Human: Interaction Design]
           ↓
Interactive Prototype
           ↓
[Human: User Testing]
           ↓
[AI: Test Analysis & Insights]
           ↓
Iteration Recommendations
           ↓
[Human: Refinement]
           ↓
Approved Prototype
```

---

### Phase 5: Design System

| Attribute | Details |
|-----------|---------|
| **Duration** | 2-4 weeks (initial), ongoing maintenance |
| **Input Artifacts** | Approved mockups, component audit, brand guidelines |
| **Output Artifacts** | Component library, design tokens (variables), documentation |
| **Tools** | Figma Variables, Tokens Studio, Storybook |
| **Human Roles** | Design Systems Designer, Design Ops |
| **AI Opportunities** | Token extraction, component generation, documentation |
| **Version Control** | Figma library versioning, Git (tokens) |
| **CI/CD Gates** | Token validation, component coverage metrics |

```
Approved Designs
       ↓
[AI: Pattern Recognition]
       ↓
Component Candidates
       ↓
[Human: System Architecture]
       ↓
Component Library
       ↓
[AI: Token Extraction]
       ↓
Design Tokens (Variables)
       ↓
[AI: Documentation Generation]
       ↓
Published Design System
```

**Design Token Flow (Detailed):**

```mermaid
flowchart LR
    subgraph FIGMA["Figma"]
        FV[Variables]
        FC[Components]
    end

    subgraph TRANSFORM["Transform Layer"]
        TS[Tokens Studio]
        SD[Style Dictionary]
    end

    subgraph OUTPUT["Output Formats"]
        CSS[CSS Custom Properties]
        SCSS[SCSS Variables]
        JS[JS/TS Constants]
        JSON[JSON Tokens]
    end

    FV --> TS
    FC --> TS
    TS --> SD
    SD --> CSS
    SD --> SCSS
    SD --> JS
    SD --> JSON
```

---

### Phase 6: Dev Mode

| Attribute | Details |
|-----------|---------|
| **Duration** | Ongoing (part of handoff) |
| **Input Artifacts** | Design system, final mockups, prototypes |
| **Output Artifacts** | Code snippets, assets, Code Connect mappings, MCP context |
| **Tools** | Figma Dev Mode, Code Connect, Figma MCP Server |
| **Human Roles** | Developer, Design Technologist |
| **AI Opportunities** | Code generation, component mapping suggestions, asset optimization |
| **Version Control** | Git (Code Connect files), Figma versions |
| **CI/CD Gates** | Code Connect coverage, asset export validation |

```
Design System + Mockups
          ↓
[Tool: Dev Mode Inspection]
          ↓
Code Snippets + Measurements
          ↓
[Human/AI: Code Connect Setup]
          ↓
Component Mappings
          ↓
[Tool: MCP Server Activation]
          ↓
AI-Accessible Design Context
          ↓
[Tool: Asset Export]
          ↓
Optimized Assets
```

**Code Connect Setup Flow:**

```mermaid
sequenceDiagram
    participant Designer
    participant Figma
    participant GitHub
    participant Developer
    participant AI Agent

    Designer->>Figma: Finalize components
    Developer->>Figma: Open Code Connect UI
    Figma->>GitHub: Connect repository
    Developer->>Figma: Map components to code
    Figma->>Figma: Generate .figma.tsx files
    AI Agent->>Figma: Query via MCP
    Figma->>AI Agent: Return design context
    AI Agent->>Developer: Generate implementation
```

---

### Phase 7: Code

| Attribute | Details |
|-----------|---------|
| **Duration** | 2-6 weeks |
| **Input Artifacts** | Code Connect mappings, design tokens, MCP context, assets |
| **Output Artifacts** | Production code, component library, backend services, tests |
| **Tools** | VS Code/Cursor, Figma MCP, Supabase, GitHub |
| **Human Roles** | Frontend Developer, Backend Developer, QA Engineer |
| **AI Opportunities** | Code generation (70-80%), test generation, backend scaffolding |
| **Version Control** | Git branches, PRs |
| **CI/CD Gates** | Lint, type check, unit tests, integration tests, visual regression |

```
MCP Context + Tokens + Assets
            ↓
[AI: Code Generation via Cursor/Copilot]
            ↓
Draft Components
            ↓
[Human: Code Review & Refinement]
            ↓
[AI: Test Generation]
            ↓
Unit + Integration Tests
            ↓
[AI: Backend Schema Generation]
            ↓
Supabase Tables + Functions
            ↓
[Human: Integration & Logic]
            ↓
Production-Ready Code
```

**AI Code Generation Flow:**

```mermaid
flowchart TB
    subgraph INPUT["Input Layer"]
        MCP[Figma MCP Server]
        TOKENS[Design Tokens]
        SPEC[Component Specs]
    end

    subgraph AI["AI Processing"]
        CURSOR[Cursor/Copilot]
        V0[Vercel v0]
        MAKE[Figma Make]
    end

    subgraph OUTPUT["Output Layer"]
        REACT[React Components]
        STYLES[CSS/Tailwind]
        TESTS[Test Files]
        DOCS[Documentation]
    end

    MCP --> CURSOR
    TOKENS --> CURSOR
    SPEC --> CURSOR

    MCP --> V0
    MCP --> MAKE

    CURSOR --> REACT
    CURSOR --> STYLES
    V0 --> REACT
    V0 --> STYLES
    MAKE --> REACT

    CURSOR --> TESTS
    CURSOR --> DOCS
```

---

### Phase 8: Production

| Attribute | Details |
|-----------|---------|
| **Duration** | Ongoing |
| **Input Artifacts** | Tested code, deployment config, monitoring setup |
| **Output Artifacts** | Live application, performance metrics, user feedback |
| **Tools** | Vercel/Netlify, GitHub Actions, Supabase, DataDog/Sentry |
| **Human Roles** | DevOps Engineer, SRE, Product Manager |
| **AI Opportunities** | Deployment automation, anomaly detection, feedback synthesis |
| **Version Control** | Git tags, release branches |
| **CI/CD Gates** | E2E tests, performance benchmarks, security scans |

```
Production Code
       ↓
[CI: Lint + Type Check + Test]
       ↓
[CI: Build]
       ↓
[CI: Preview Deployment]
       ↓
[Human: QA Validation]
       ↓
[CI: Production Deployment]
       ↓
Live Application
       ↓
[Tool: Monitoring & Alerts]
       ↓
[AI: Anomaly Detection]
       ↓
[AI: Feedback Synthesis]
       ↓
Iteration Insights → Phase 1
```

**CI/CD Pipeline (Detailed):**

```mermaid
flowchart LR
    subgraph TRIGGER["Triggers"]
        PR[Pull Request]
        MERGE[Merge to Main]
        TAG[Release Tag]
    end

    subgraph CI["CI Pipeline"]
        LINT[Lint & Format]
        TYPE[Type Check]
        UNIT[Unit Tests]
        INT[Integration Tests]
        VIS[Visual Regression]
        BUILD[Build]
    end

    subgraph CD["CD Pipeline"]
        PREVIEW[Preview Deploy]
        QA[QA Validation]
        STAGE[Staging Deploy]
        PROD[Production Deploy]
    end

    subgraph MONITOR["Monitoring"]
        HEALTH[Health Checks]
        PERF[Performance]
        ERROR[Error Tracking]
        USAGE[Usage Analytics]
    end

    PR --> LINT --> TYPE --> UNIT --> INT --> VIS --> BUILD
    BUILD --> PREVIEW --> QA

    MERGE --> BUILD
    BUILD --> STAGE --> PROD

    TAG --> PROD

    PROD --> HEALTH
    PROD --> PERF
    PROD --> ERROR
    PROD --> USAGE
```

---

## Automation Opportunity Summary

| Phase | Current Automation | Target Automation | Gap |
|-------|-------------------|-------------------|-----|
| Concept | 20% | 50% | AI research synthesis |
| Wireframe | 30% | 60% | AI layout generation |
| Mockup | 40% | 70% | AI variant generation |
| Prototype | 50% | 80% | Figma Make integration |
| Design System | 60% | 85% | Token pipelines |
| Dev Mode | 70% | 90% | Code Connect + MCP |
| Code | 50% | 80% | AI code generation |
| Production | 80% | 95% | Existing CI/CD maturity |

---

## Version Control Points

```
┌──────────────────────────────────────────────────────────────────┐
│                    VERSION CONTROL CHECKPOINTS                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [Concept]           PRD v1.0                                    │
│      ↓                                                           │
│  [Wireframe]         Figma Branch: wireframes/v1                 │
│      ↓                                                           │
│  [Mockup]            Figma Branch: visual/v1                     │
│      ↓                                                           │
│  [Prototype]         Figma: Prototype Link v1                    │
│      ↓                                                           │
│  [Design System]     Figma Library v1.0.0                        │
│      ↓               Git: tokens/v1.0.0                          │
│  [Dev Mode]          Git: code-connect/v1.0.0                    │
│      ↓                                                           │
│  [Code]              Git: feature/component-library              │
│      ↓               Git: PR #123                                │
│  [Production]        Git: release/v1.0.0                         │
│                      Git Tag: v1.0.0                             │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Feedback Loop Integration

```mermaid
flowchart TB
    PROD[Production App]
    ANALYTICS[Usage Analytics]
    FEEDBACK[User Feedback]
    ERRORS[Error Reports]

    PROD --> ANALYTICS
    PROD --> FEEDBACK
    PROD --> ERRORS

    ANALYTICS --> AI_SYNTH[AI Synthesis]
    FEEDBACK --> AI_SYNTH
    ERRORS --> AI_SYNTH

    AI_SYNTH --> INSIGHTS[Actionable Insights]

    INSIGHTS --> CONCEPT_UPDATE[Update Requirements]
    INSIGHTS --> DESIGN_UPDATE[Update Designs]
    INSIGHTS --> CODE_FIX[Bug Fixes]

    CONCEPT_UPDATE --> CONCEPT[Phase 1: Concept]
    DESIGN_UPDATE --> MOCKUP[Phase 3: Mockup]
    CODE_FIX --> CODE[Phase 7: Code]
```

---

*Document generated: 2026-01-20*
*Part of: Figma Design Automation Research*

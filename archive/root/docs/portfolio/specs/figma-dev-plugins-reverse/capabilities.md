# Figma Software Development Plugins – Capability Matrix (Reverse Spec)

## 1. Core Capability Buckets

From the Figma Software Development plugins list, we see these major buckets:

1. **Design → Code Engines**
   - Builder.io – Figma to Code & AI Apps
   - Anima / Anima-like (already covered separately)
   - Figma to Code (HTML, Tailwind, Flutter, SwiftUI)
   - Figma to HTML with Framer
   - Locofy Lightning
   - TeleportHQ
   - Figma to Webflow
   - pxCode (Figma → responsive HTML/CSS/React/Vue/Tailwind)
   - FigmaToFlutter / Figma → React Native
   - DhiWise Design (Figma → Flutter/HTML/Next/React)
   - AutoHTML | Components to Code
   - HtmlGenerator
   - Figma to HTML and CSS
   - FireJet
   - Codia AI (full-stack web/mobile)
   - Quest / Figma to React
   - Unify
   - CodeTea (multi-target)
   - Figma to WordPress
   - Figment (Figma → Website)
   - Figma to Bootstrap 5

2. **Design System & Specs / Dev Handoff**
   - Code Snippet Editor
   - Specs (anatomy, props, layout)
   - Inspect Styles (CSS)
   - Design Tokens (export to JSON/GitHub)
   - Figma Tailwindcss (export to Tailwind theme)
   - Tailwind CSS Color Generator
   - Redlines (measurements/specs)
   - Storybook Connect
   - Zeplin (handoff, multi-team)

3. **Dev Workflow & Integrations**
   - GitHub (Connect Design to Code)
   - Jira (connect designs to issues)
   - Automator (one-click workflows)
   - Google Sheets Sync
   - JSON to Figma (data→UI)
   - Search / Find and Replace

4. **Data Visualization / Components**
   - Datavizer (charts from data)

5. **Layout / Utility / Content Tools**
   - SkewDat
   - Grids Generator
   - AutoLayout (plugin version)
   - scrollbars
   - Lazy Load (skeleton screens)
   - Similayer
   - FontScanner
   - RTL PLZ
   - BackgroundCut / Removal.AI
   - Image Compressor
   - Chinese Content Filling Assistant
   - Text to Design AI UI Copilot – uidesign.ai

## 2. What *We* Should Replicate vs Integrate

### 2.1 Must-Replicate (Core Product Surface)

These are **core to our platform** and should exist natively:

1. **Repo-aware Figma→Code Engine (multi-target)**
   - React + TypeScript + Tailwind + shadcn/ui as first-class.
   - Hooks for other frameworks (React Native, Flutter, SwiftUI) later, but under same engine.
   - Output must:
     - Reuse existing design system primitives.
     - Pass `tsc` + ESLint + tests.
   - Effectively subsumes Builder.io / Locofy / TeleportHQ / pxCode / etc.

2. **Design System & Token Bridge**
   - Native support for:
     - Export/import **design tokens** (JSON, Tailwind theme, CSS vars).
     - Generate **Code Snippet Editor** equivalents: "component variants → TSX snippets".
     - "Specs" equivalent: anatomy, props, layout docs per component.
   - Our target: combine **Design Tokens + Specs + Inspect Styles + Figma Tailwindcss + Tailwind Color Generator** into a single **Design System Bridge**.

3. **Dev Handoff Layer**
   - Instead of just "handoff", we produce:
     - Component spec pages (anatomy, props, events).
     - Storybook stories skeleton.
     - Playwright/Cypress test stubs.
   - This effectively improves on Zeplin + Specs + Storybook Connect.

4. **Automation Engine**
   - Equivalent to Automator but generalized:
     - Triggers: Figma change, Git label, PR status, design token change.
     - Actions: run design→code, update specs, open PR, comment with diff summary.
   - All exposed via jobs API + Pulser SDK.

5. **Code/Design Search + Refactor**
   - Combine "Search", "Find and Replace", "Similayer", "FontScanner":
     - Search across design + code graphs.
     - Suggest/batch refactors (rename component, change typography token, etc.).
   - Agent-friendly API for bulk edits.

### 2.2 Should-Integrate (via Connectors, not Reinvented)

These we **integrate** with rather than fully rebuild:

1. **GitHub, Jira, Storybook, Webflow, WordPress**
   - Provide **connectors**:
     - Git providers (GitHub, GitLab, etc.).
     - Issue trackers (Jira).
     - Storybook (inspect + sync stories).
     - Site builders (Webflow/WordPress) as export targets, not core.

2. **Content & Asset Utilities**
   - Background removal, compression, scrollbars, grids, skeleton loaders:
     - Expose as **optional pipelines** in asset processing (image ops, placeholder generation).
     - Don't make them core features; they're modular plugins.

3. **Data Visualization**
   - Datavizer's role is very narrow.
   - For us: provide a generic **"design → chart component"** mapping:
     - Figma chart → `Chart.tsx` using your chart lib (e.g., Recharts/Chart.js/Plotly).
   - Use plugin-style integrations, not separate product.

### 2.3 Optional / Future Bets

1. **Full-stack From Figma (Codia AI, Quest, DhiWise)**
   - Our angle: front-end focus **first**; back-end scaffolding as a second layer:
     - API schema inference (OpenAPI/GraphQL).
     - CRUD view scaffolding.
   - Don't go "full-stack generator" until front-end + design system parity is solid.

2. **Prompt-to-Design (Text to Design Copilot)**
   - Can be integrated as:
     - "Generate Figma starting point" agent.
     - But it's outside core design↔code parity. Optional.

## 3. What Our Platform Becomes (In One Sentence)

> A **repo-aware, design-system-native, self-hosted Figma↔Code bridge** that replaces the fragmented plugin ecosystem (Builder.io, Locofy, TeleportHQ, Specs, Design Tokens, Automator, Zeplin, Storybook Connect) with a single AI+agent-first engine.

## 4. Capability Checklist (Replicate vs Integrate)

| Capability | Status | Type |
|------------|--------|------|
| Multi-target Figma→React/Tailwind/TSX engine | Core | Replicate |
| Design token ingestion/export | Core | Replicate |
| Component specs (anatomy, props, layout) | Core | Replicate |
| Design→Storybook stories/test stubs | Core | Replicate |
| Git/PR integration | Core | Replicate (tight coupling) |
| Jira/issue linkage | Connector | Integrate |
| Storybook Connect | Connector | Integrate (we produce stories) |
| Webflow/WordPress export | Connector | Optional |
| Automation engine | Core | Replicate (generalized) |
| Design + code search/refactor engine | Core | Replicate |
| Prompt-to-design AI | Future | Optional |
| Full stack generator | Future | Optional (phase 2+) |

## 5. Plugins Subsumed by Our Engine

This matrix maps 40+ Figma plugins to our unified engine:

### Design→Code (Subsumed by Core Engine)
- Builder.io → Our multi-target codegen
- Locofy Lightning → Our repo-aware engine
- TeleportHQ → Our component mapping
- pxCode → Our Tailwind/React output
- DhiWise Design → Our framework targets
- AutoHTML → Our HTML generation
- FireJet → Our code export
- Quest → Our React generation

### Design System (Subsumed by Token Bridge)
- Design Tokens → Our token ingestion
- Figma Tailwindcss → Our Tailwind theme export
- Tailwind Color Generator → Our color palette extraction
- Inspect Styles → Our CSS inspection
- Code Snippet Editor → Our component snippets

### Dev Handoff (Subsumed by Handoff Layer)
- Specs → Our anatomy/props docs
- Zeplin → Our spec pages
- Storybook Connect → Our story generation
- Redlines → Our measurement export

### Automation (Subsumed by Automation Engine)
- Automator → Our trigger/action system
- GitHub integration → Our Git connector
- Jira integration → Our issue connector

## 6. Implementation Note

This matrix should be kept in sync with:
- `spec/anima-reverse/prd.md` (if exists)
- `skills/user/figma-agent/SKILL.md` (the agent skill spec)
- The actual **service and SDK design** (API endpoints, job types, mapping schemas)

## 7. Architecture Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    Figma Plugin Ecosystem                        │
│  (40+ plugins: Builder.io, Locofy, Zeplin, Design Tokens, etc.) │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ Consolidated into
┌─────────────────────────────────────────────────────────────────┐
│                   Our Unified Platform                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Design→Code    │  │  Token Bridge   │  │  Dev Handoff    │  │
│  │  Engine         │  │                 │  │  Layer          │  │
│  │  (Multi-target) │  │  (Design System)│  │  (Specs+Tests)  │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │            │
│           └────────────────────┼────────────────────┘            │
│                                │                                 │
│  ┌─────────────────────────────┴─────────────────────────────┐  │
│  │                   Automation Engine                        │  │
│  │  (Triggers: Figma change, Git, PR, Token update)          │  │
│  │  (Actions: codegen, spec update, PR creation)             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Connectors Layer                        │  │
│  │  GitHub │ GitLab │ Jira │ Storybook │ Webflow │ WordPress │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 8. Job Types for Pulser Integration

Each capability bucket maps to a job type:

```typescript
type FigmaJobType =
  | 'figma:extract'      // Extract design context
  | 'figma:codegen'      // Generate code from design
  | 'figma:tokens'       // Extract/sync design tokens
  | 'figma:specs'        // Generate component specs
  | 'figma:stories'      // Generate Storybook stories
  | 'figma:tests'        // Generate test stubs
  | 'figma:search'       // Search design/code graphs
  | 'figma:refactor'     // Batch refactor operations
  | 'figma:sync'         // Full sync (all of above)
```

## 9. Version History

- **1.0.0** (2025-01): Initial capability matrix
  - Mapped 40+ Figma plugins to 5 core buckets
  - Defined replicate vs integrate strategy
  - Added architecture diagram
  - Added Pulser job type mapping

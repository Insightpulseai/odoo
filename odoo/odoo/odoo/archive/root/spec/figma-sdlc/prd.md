# Figma SDLC PRD

## Executive Summary

Establish a production-grade, Figma-driven Software Development Life Cycle (SDLC) where design tokens and components flow from Figma through CI/CD via Pull Requests, acting as an enforced supply chain for frontend engineering.

## 7-Stage Figma SDLC

0. **File + Library Operability (Organization, Readiness, Traceability)**
   Before tokens are exported, Figma files must be structured for discoverability. Components require detailed implementation metadata (repo links, code names), layers follow structured naming (BEM/HTML), and "ready for dev" states are explicit.
1. **The Source of Truth: Design Tokens**
   The foundation is managing semantic variables natively via the `figma.variables` API (or Tokens Studio).
   - **Theming at scale**: Leveraging _Extended Variable Collections_ natively to handle Base → Brand/Theme overrides efficiently.
2. **Variable Export & Adoption Scanning**
   Before export is permitted, a plugin-driven script must analyze adoption by scanning `boundVariables` across all nodes:
   - **Node-level bindings**: Ensuring fills, strokes, and layouts are explicitly bound.
   - **Segment-level bindings**: Inspecting `TextNode.getStyledTextSegments(['boundVariables'])` to enforce typography variables (fontFamily, fontWeight, letterSpacing) even within substrings.
3. **Version Control & Git Integration**
   Design updates are pushed directly to the repository via plugins, opening a Pull Request containing the updated JSON token definitions.
4. **CI/CD & The Build Pipeline**
   A token compiler pipeline (e.g., Style Dictionary, Tokens Studio transformers, or custom logic) parses the JSON into platform-specific code upon PR creation.
   4.5. **Dev Mode as the Implementation Interface (Figma Dev Mode + VS Code)**
   Dev Mode is the developer-facing surface where implementation context is consumed. It does **not** replace CI/CD; it reduces ambiguity at the point of use.
   **What Dev Mode provides (contract surface):**
   - **Inspection plugin UI (Inspect panel)** to surface implementation metadata for the current selection:
     - Code component name + canonical import path
     - Repo/PR links, docs links, ticket links
     - Token names referenced by the selection (semantic tokens, not raw values)
     - Deprecation warnings (e.g., token alias required)
   - **Codegen plugin output** in the native "Code" section (framework-specific snippets).
   - **VS Code parity** via Figma for VS Code (same plugin behaviors and responsive UI).
     **Hard constraint (enforced by design):**
   - Dev Mode plugins are treated as **read-only** with respect to design artifacts; they may annotate and report, but not mutate nodes/styles.
     **Why this exists in the SDLC:**
   - Tokens & components are versioned in Git; Dev Mode is the "last-mile" delivery layer that helps developers implement correctly and consistently.
     4.6. **Code Connect (Design ↔ Code Component Mapping Published into Dev Mode)**
     Code Connect provides the **canonical mapping** between design system components in a Figma library and their corresponding implementations in a code repository, so Dev Mode can show **real, versioned snippets** for the selected component.
     **Core concept**
   - A repository contains Code Connect mapping files that link: code component ↔ Figma component node URL, and prop/variant mappings.
   - These mappings are **published** so Dev Mode can render the snippet in the Inspect panel.
     **Contract artifact**
   - `figma.config.json` in the repo defines the project connection.
   - Code Connect mapping files follow the `component-name.figma.<framework>` convention and live in the repo.
     **Why this is SDLC-critical**
   - This is the enforceable "component handshake" layer: selection in Figma → known code component + known props + known snippet, without drift.
     4.7. **Figma Make (AI Prompt-to-Code Lane, Constrained by the Design System)**
   ### Dependency Model (Packages + Third-Party Libraries)
   Figma Make supports dependencies via:
   - `package.json` at the app/prototype root for npm packages.
   - Standard import strings for third-party libraries; Make resolves imports through esm.sh/CDN mapping automatically.
     **Policy requirement**
   - Make/Sites generation must be constrained by an allowlist of packages/libraries; any dependency outside the allowlist is non-compliant and blocks promotion to production.
5. **Developer Consumption**
   Compiled assets are published as versioned packages (e.g., npm) and consumed by developers. Storybook embeds Figma references; consistency is guaranteed by versioned packages + CI gates (not embeds alone).
6. **The Reverse Flow: Code to Design**
   Reverse sync is strictly scoped to token parity + component metadata, not arbitrary code refactors.

## Contracts & Guarantees (What CI Enforces)

- **Token schema + naming rules**: Strict taxonomy (`primitive.*`, `semantic.*`, `component.*`) with no raw hex values permitted in the semantic layer. Style names in Figma must perfectly match variable names in code.
- **API-based Export & Guardrails**: Export must yield the full JSON (Collections, Modes, Variables). Guardrails enforce that every mode has values and no raw overrides are permitted.
- **Dev Mode guarantees (point-of-use enforcement)**: For any "Ready for Dev" selection, Dev Mode must show mapped code component + import path, token references (semantic names), and deprecation guidance (aliases/replacements). Code snippets shown in Dev Mode are generated from the **same versioned token/component packages** consumed by the codebase.
- **Code Connect guarantees (mapping integrity)**: Any component marked "Ready for Dev" must have a published Code Connect mapping for each supported platform label (e.g., React/Web/SwiftUI/Compose). CI fails if: mapping files exist but are not publishable (invalid node URLs / missing config), mapped code component paths no longer resolve in-repo, or required props/variants drift from the declared mapping contract.
- **Make package guarantees (design system compliance)**: Any Make prototype intended for promotion must install the **approved design system package** and conform to its Vite + React 18+ compatibility requirements. Any Make template used org-wide must include the package + guidelines at minimum.
- **Drift & Adoption tracking**: The pipeline must produce an adoption report explicitly surfacing the percentage of components using `boundVariables` vs. raw unlinked values (including `setRangeBoundVariable` checks for text subsets).
- **Component metadata & traceability**: The contract extends beyond tokens to include component descriptions (code name, repo link, usage rules, system vs. local definition) and explicit "ready for dev" signals.
- **Branching mirrors engineering**: Design branches follow engineering naming conventions (e.g., ticket prefixes) and utilize formal review/merge workflows.
- **SemVer + deprecation policy**: Soft-deprecate aliases before removal. Major versions are strictly required for breaking changes (renames/removals or semantic meaning shifts).
- **Parity gates**: Enforced token diff reports and breaking change detection on all design PRs.
- **Visual regression gating**: Automated visual comparison (Chromatic/Loki/Playwright) triggered against consuming UI components.
- **Accessibility gating**: Strict WCAG contrast limits on semantic token pairs and focus/motion tokens.
- **Security Boundary**: Enforce restrictive branch protections. Auto-opened token PRs are limited to authorized design groups and cannot change arbitrary application code.

## Non-Goals

- Full bidirectional free-form sync of all design changes ↔ all code changes.
- Using Figma embeds as runtime truth (embeds are strictly documentation, not delivery artifacts).
- Treating Dev Mode output as the runtime source of truth (Dev Mode is an implementation aid; CI + versioned packages remain authoritative).
- Treating Make output as authoritative without passing through the versioned design system package + guidelines contract.

# Figma SDLC Implementation Plan

## Phase 0: File + Library Operability

- Implement explicit "ready for dev" signaling (dedicated pages, stickers, cover pages).
- Standardize Figma branch naming conventions to match engineering ticket systems.
- Mandate component metadata descriptions containing code names, repo links, and usage rules.
- Structure variants using nested instance swapping to avoid combinatorial explosions.

## Phase 1: Core CI and Exporters

- Implement a custom plugin or configure existing exporters to dump the full `figma.variables` dictionary (Collections, Modes, Values).
- Build the **Adoption Scanner**: a script utilizing `node.boundVariables` and `TextNode.getStyledTextSegments` to calculate the percentage of design utilizing raw values vs semantic tokens.
- Base workflow configuration: Automated PR generation from Figma environment to GitHub.
- Token compiler pipeline construction (compiling JSON into CSS custom properties and JS/TS object schemas).

## Phase 2: Token Governance & Release Channels

- Define token schema + taxonomy layers (`primitive`, `semantic`, `component`).
- Define SemVer mapping rules for design tokens (Patch for value tweaks, Minor for new tokens, Major for renames/semantic changes).
- Define `dist-tags` (e.g., `next`, `latest`) and strict environment branch mapping (`design/main` ↔ `code/main`, preview branches).

## Phase 3: Drift & Quality Gates

- Implement token diff report generation to surface exactly what tokens changed on PR.
- Implement breaking change detection pipeline over JSON token definitions.
- Set up the visual regression pipeline to run against UI components consuming the new tokens.
- Enforce accessibility checks (contrast ratios) on all semantic token maps.

## Phase 4: Dev Mode Integration (Inspect + Codegen + VS Code)

**Outcome:** Developers can implement without guessing. Dev Mode surfaces the canonical mapping from Figma selection → code component + tokens + links.

- Build an **Inspect panel plugin** that reads selection context and renders implementation metadata.
- Build a **Codegen plugin** that emits framework-specific snippets and enforces token usage in generated code.
- Ensure **VS Code compatibility** (responsive UI + manifest flags).
- Gate "Ready for Dev" artifacts on presence of mapping metadata and deprecation cleanliness.

## Phase 5: Component Contract Mapping

- Connect Figma component keys precisely to code component identities.
- Document and validate component states (hover/active/disabled/loading) and required slots (icons, badges, etc.).

## Phase 6: Code Connect Mapping & Publish Workflow

**Outcome:** Dev Mode shows authoritative snippets for mapped design-system components.

- Establish `figma.config.json` as a versioned contract for the repo↔Figma library connection.
- Generate/maintain Code Connect mapping files for core components.
- Publish mappings as part of a controlled release workflow (with labels per platform).
- Add CI validation so mapping drift is detected before merge.

## Phase 7: Figma Make Enablement (Design System Package + Guidelines)

**Outcome:** Make can generate prototypes that use our production components/tokens correctly.

- Ensure DS package meets Make requirements: React 18+, Vite-compatible, published via npm (public or org-private registry).
- Produce baseline guidelines so Make's AI uses tokens/components correctly.
- Publish a Make template (packages+guidelines only OR starter app) to standardize prototype starting points.
- Define and version a dependency allowlist for Make/Sites (npm packages + importable libraries), aligned with our security and licensing policies.

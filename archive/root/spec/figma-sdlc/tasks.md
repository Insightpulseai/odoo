# Tasks: Figma SDLC

## File + Library Operability (Figma Best Practices)

- [ ] Component descriptions include: code name, repo link, usage rules, "local vs system" flag.
- [ ] Style names match token/variable names used in code.
- [ ] "Ready for dev" convention exists (pages/stickers/cover/projects).
- [ ] Branch naming matches engineering conventions; use review/merge workflow.
- [ ] For handoff-ready components: layer naming aligns to BEM or HTML structure (as agreed with dev).
- [ ] Variants are structured to avoid explosion; nested instance swapping for icons.

## Governance & Schema

- [ ] Ensure all theming uses Figma's natively supported _Extended Variable Collections_ for base/brand inheritance.
- [ ] Implement a script to export the exact JSON contract of Local/Library Collections via `figma.variables.getLocalVariableCollectionsAsync()`.
- [ ] Define token taxonomy (`primitive`, `semantic`, `component`) and enforce via JSON schema constraints.
- [ ] Implement a standardized deprecation + rename mapping file (`token-aliases.json`).

## CI/CD Quality & Adoption Gates

- [ ] Write a Figma plugin/script to scan `node.boundVariables` to generate an adoption vs. raw drift report.
- [ ] Update the adoption scanner to inspect `TextNode.getStyledTextSegments(['boundVariables'])` to catch unlinked Typography substrings.
- [ ] Add explicit token linting in CI (naming conventions, forbid raw values in the semantic layer).
- [ ] Add CI step: automatically generate token diff reports as a PR artifact/comment.
- [ ] Add CI step: fail PR instantly on breaking token changes without an associated major SemVer bump.
- [ ] Add visual regression gate for key component stories (Chromatic/Playwright).
- [ ] Add WCAG contrast checks for paired semantic colors/tokens.
- [ ] Add robust component mapping registry (Figma component key ↔ code component name).

## Dev Mode: Implementation Interface

- [ ] Define the **mapping registry contract**:
  - Figma component key → code component name → canonical import path
  - storage location (versioned in repo; referenced by Dev Mode plugin)
- [ ] Implement Dev Mode **Inspect** plugin:
  - reads current selection
  - displays mapping info + links + token references + deprecation warnings
- [ ] Implement Dev Mode **Codegen** plugin:
  - generates framework snippets for selection
  - emits token-based styling (no raw values)
- [ ] VS Code parity:
  - declare VS Code capability in manifest
  - ensure UI works in horizontal/compact layouts
- [ ] "Ready for Dev" gate:
  - fail if selection lacks mapping metadata OR uses deprecated tokens without aliases
- [ ] Evidence:
  - screenshots or logs showing selection → mapping + codegen output + warnings

## Code Connect: Mapping Contract + Drift Gates

- [ ] Define "mapped component" criteria (what must be mapped before "Ready for Dev").
- [ ] Add/standardize `figma.config.json` in repo as the Code Connect project contract.
- [ ] Create Code Connect mapping files for Tier-1 components (naming: `component-name.figma.<framework>`).
- [ ] Add CI check: verify mapping file ↔ code component path exists and is importable/buildable.
- [ ] Add CI check: verify Figma node URLs are present/configured via the project substitutions contract.
- [ ] Define publish policy (what events trigger publish, and what labels/platforms are required).
- [ ] Evidence: Dev Mode screenshot/log showing snippet appears for a mapped component after publish.

## Figma Make: Policy-Guided Generation

- [ ] Create `policies/make-dependencies.yaml` (or equivalent) defining allowed npm packages, third-party imports, and denied categories.
- [ ] Add a "promotion gate" rule: Make/Sites code cannot move into the production repo unless dependencies are allowlisted.

## Figma Make: Design System Package Contract

- [ ] Validate DS package requirements: React 18+, builds under Vite, published as npm package (public or org-private).
- [ ] If private: document org scope and publishing prerequisites (admin-generated key workflow) as a governed release step (no secrets committed).
- [ ] Create/maintain Make guidelines so AI uses DS components/tokens as intended.
- [ ] Publish a Make template (Option A: packages+guidelines only, Option B: starter app baseline).
- [ ] Evidence: one Make prototype that installs the DS package and builds successfully (Vite) using guided components/tokens.

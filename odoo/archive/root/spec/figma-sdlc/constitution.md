# Figma SDLC Constitution

## Core Principles

- **Versioned artifacts > live embeds**: The source of truth is strictly versioned packages and CI output, not what is visually embedded in Storybook or Figma.
- **Event-sourced changes**: Every design change that matters must manifest as a Pull Request.
- **No silent drift**: Parity gates are mandatory to prevent design and code from diverging without explicit approval.
- **Traceability via component metadata**: Component descriptions must encapsulate implementation context (code names, repo links) to facilitate immediate context switching for developers.
- **Bound Variables over Raw Values**: Adoption is measured by scanning native `boundVariables` natively in Figma (including text substrings). Raw hex or raw structural tweaks in "ready" components represent technical debt.
- **Native Theming Engine**: Theming must utilize _Extended Variable Collections_ avoiding combinatorial duplication of libraries.
- **Dev Mode is point-of-use guidance**, not the authoritative source of truth.
- **Traceability**: Any "Ready for Dev" design must be traceable: selection → code component → tokens → repo artifacts.
- **Semantic preference**: Generated snippets must prefer semantic tokens and highlight deprecated usage explicitly.
- **Code Connect Principles**: Component mappings are versioned artifacts in Git, reviewed like code. "Ready for Dev" requires an explicit design↔code mapping, not inference. Dev Mode snippets must originate from published mappings.
- **Organization is part of the contract**: Teams, projects, and branching models must mirror engineering structures. Design branching follows ticket-based naming and uses formal merge reviews.
- **Backwards compatibility**: Use aliases before removals. Breaking changes to tokens must follow strict semantic versioning.
- **Tokens as SSOT**: Design tokens act as the legally binding contract between design and engineering.
- **Figma Make Principles**: Dependency policy is explicit: packages come from `package.json` (Make) and imports resolve via esm.sh mapping; only allowlisted dependencies are promotable.
- **Make + Design System Principles**: Make generation must be constrained by the **published npm design system package** (React 18+, Vite-compatible). Guidelines/templates are first-class policy artifacts for Make usage and must be versioned and reviewed.

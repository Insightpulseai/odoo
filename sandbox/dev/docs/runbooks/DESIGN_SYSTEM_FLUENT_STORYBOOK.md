# Runbook: Fluent UI + Storybook Design System (IPAI)

## ⚠️ Critical: Repository Boundary Enforcement

**This runbook is stored in `odoo-ce/sandbox/dev/docs/runbooks/` as documentation only.**

**Do NOT execute these commands in an Odoo repository.** Design system belongs in a dedicated repo.

---

## Where This Should Live

### Recommended Repository Options

1. **Option A: Create new `ipai-ui` repo** (Recommended)
   ```bash
   cd ~/Documents/GitHub
   mkdir ipai-ui && cd ipai-ui
   git init
   echo "# InsightPulseAI Design System" > README.md
   npm init -y
   git add . && git commit -m "chore: initialize ipai-ui design system repo"
   ```

2. **Option B: Use existing `ipai-workspace` repo**
   ```bash
   cd ~/Documents/GitHub/ipai-workspace
   # Add design system packages to existing monorepo
   ```

3. **Option C: Use `enterprise-catalog` repo**
   ```bash
   cd ~/Documents/GitHub/enterprise-catalog
   # If this is intended for UI components
   ```

---

## Repository Structure (SSOT)

```
ipai-ui/  (or chosen repo)
├── packages/
│   ├── tokens/          # Design tokens (@insightpulseai/tokens)
│   ├── ui/              # Fluent-wrapped components (@insightpulseai/ui)
│   └── telemetry/       # (future) Usage analytics
├── apps/
│   └── storybook/       # Living component spec
├── infra/
│   └── ci/              # CI workflows for token build + Storybook publish
├── docs/
│   └── design-principles.md
├── package.json         # Root workspace config
├── turbo.json           # (optional) Build orchestration
└── .github/workflows/   # CI gates (lint, build, a11y, visual regression)
```

---

## Technology Stack

### Core Dependencies

**Fluent UI v9** (Microsoft Design System):
```bash
npm i @fluentui/react-components
```

**Storybook** (Living Component Spec):
```bash
npx storybook@latest init --disable-telemetry
```

**Optional - Build Orchestration**:
```bash
npm i -D turbo
```

---

## Bootstrap Commands (Run in Design System Repo Only)

### 1. Initialize Repository Structure

```bash
set -euo pipefail

# Create directory structure
mkdir -p packages/{tokens,ui} apps/storybook

# Initialize root package.json if not exists
if [ ! -f package.json ]; then
  npm init -y
fi

# Install Fluent UI + build tools
npm i @fluentui/react-components
npm i -D turbo
```

### 2. Initialize Storybook

```bash
cd apps/storybook
npm init -y
npx storybook@latest init --disable-telemetry
cd ../..
```

### 3. Create Provider Wrapper

**File**: `packages/ui/src/Providers.tsx`

```tsx
import * as React from "react";
import { FluentProvider, webLightTheme } from "@fluentui/react-components";

export function IpaProvider(props: { children: React.ReactNode }) {
  return <FluentProvider theme={webLightTheme}>{props.children}</FluentProvider>;
}
```

### 4. Wire Storybook Preview

**File**: `apps/storybook/.storybook/preview.tsx`

```tsx
import * as React from "react";
import type { Preview } from "@storybook/react";
import { FluentProvider, webLightTheme } from "@fluentui/react-components";

const preview: Preview = {
  decorators: [
    (Story) => (
      <FluentProvider theme={webLightTheme}>
        <Story />
      </FluentProvider>
    ),
  ],
};

export default preview;
```

---

## Information Architecture (Copilot-Inspired)

### Top-Level Navigation Taxonomy

Following Microsoft 365 Copilot's capability taxonomy:

| Category | IPAI Equivalent | Purpose |
|----------|-----------------|---------|
| **Chat** | "Ask InsightPulse" | RAG/LLM routing, saved prompts |
| **Agents** | Pulser Hub | Agent store + policies |
| **Connectors** | Data Sources | Fivetran-like sources/destinations |
| **Notebooks** | Workspaces | Project workspaces + run logs |
| **Search** | Semantic Search | Unified search (docs/repos/data) |
| **Security & Admin** | Admin Portal | RBAC, audit, compliance, analytics |

### Namespace Model

**Org-level namespaces**:
- `ipai-*` = cross-cutting platform primitives
- `pulser-*` = agent runtime + orchestration
- `odoo-*` / `ipai_odoo_*` = Odoo/OCA work
- `scout-*` / `ces-*` = product surfaces

**Package naming**:
- NPM: `@insightpulseai/tokens`, `@insightpulseai/ui`, `@insightpulseai/telemetry`
- PyPI: `ipai_pulser`, `ipai_connectors`, `ipai_policy`

---

## "Everything as Code" Patterns

| Pattern | Artifacts | CI Enforcement |
|---------|-----------|----------------|
| **Infrastructure-as-Code** | Terraform/Pulumi, Helm, Compose | `terraform plan` + drift detection |
| **Environment-as-Code** | `.env.example`, SOPS/age, Vault refs | Secret scanning + validation |
| **Policy-as-Code** | JSON rules + validators | ORG_RULES enforcement |
| **Security-as-Code** | GitHub Actions perms, OPA/Rego, CodeQL | Permissions audit + SAST |
| **Compliance-as-Code** | CIS scripts, evidence bundles | Compliance scorecard |
| **Docs-as-Code** | `/docs`, doc linting, link check | Markdown lint + broken links |
| **Design-as-Code** | Token JSON, Storybook | Token build + visual regression |
| **API/Contract-as-Code** | OpenAPI, JSON Schema | Schema validation |
| **Data-as-Code** | dbt, Dagster, SQL migrations | Schema drift detection |
| **Agent/Prompt-as-Code** | `skills/*/skill.md`, YAML manifests | Skill validation |
| **Runbooks-as-Code** | `scripts/runbooks/*.sh` | Shellcheck + execution tests |

---

## CI/CD Pipelines (Future Implementation)

### Token Build & Publish

```yaml
name: token-build-publish

on:
  push:
    tags: ['tokens-v*']
  workflow_dispatch: {}

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build --workspace=@insightpulseai/tokens
      - run: npm publish --workspace=@insightpulseai/tokens
```

### Storybook Build & Artifact

```yaml
name: storybook-build

on:
  pull_request:
    paths: ['packages/ui/**', 'apps/storybook/**']
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run build-storybook --workspace=apps/storybook
      - uses: actions/upload-artifact@v4
        with:
          name: storybook-static
          path: apps/storybook/storybook-static/
```

### Accessibility & Visual Regression

```yaml
name: a11y-visual-regression

on:
  pull_request:
    paths: ['packages/ui/**']

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:a11y --workspace=packages/ui

  visual:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:visual --workspace=packages/ui
```

---

## Testing & Verification

### Local Development

```bash
# Start Storybook dev server
cd apps/storybook
npm run storybook

# Build for production
npm run build-storybook

# Run accessibility checks
npm run test:a11y

# Run visual regression tests
npm run test:visual
```

### Smoke Tests

```bash
# Verify Node/npm versions
node -v  # Expected: v18.x or later
npm -v   # Expected: v9.x or later

# Verify Fluent UI installation
npm list @fluentui/react-components

# Verify Storybook installation
npm list storybook
```

---

## Deployment Strategy

### Storybook Hosting Options

1. **GitHub Pages** (Recommended for open source)
   ```bash
   npm run build-storybook
   # Push storybook-static/ to gh-pages branch
   ```

2. **Vercel** (Recommended for private/commercial)
   ```bash
   vercel --prod
   # Points to apps/storybook
   ```

3. **Chromatic** (Visual regression hosting)
   ```bash
   npx chromatic --project-token=$CHROMATIC_TOKEN
   ```

---

## Integration with Odoo (Boundary Rules)

### ❌ Prohibited

- **No Node/React in Odoo repos**: Keep `odoo-ce` Python/XML only
- **No Storybook in Odoo**: Design system lives separately
- **No token imports in Odoo XML**: Use standard Odoo SCSS/CSS

### ✅ Allowed Integration Patterns

1. **Odoo → Storybook reference** (documentation links)
   ```xml
   <!-- Odoo view comment -->
   <!-- UI spec: https://storybook.insightpulseai.com/?path=/story/button -->
   ```

2. **Shared design tokens** (manual sync)
   ```bash
   # Export tokens to Odoo-compatible SCSS variables
   node scripts/tokens-to-scss.js > odoo-ce/addons/ipai_theme/static/src/scss/_tokens.scss
   ```

3. **Design review workflow**
   - Design components in Storybook first
   - Implement Odoo QWeb equivalents manually
   - Maintain parity through visual regression tests

---

## Rollback Procedures

### Revert Design System Changes

```bash
cd ~/Documents/GitHub/ipai-ui  # or chosen repo
git log --oneline | head -10   # Find commit to revert
git revert <commit-sha>
git push
```

### Rollback Storybook Deployment

```bash
# Vercel
vercel rollback <deployment-url>

# GitHub Pages
git checkout gh-pages
git revert <commit-sha>
git push
```

---

## Notes & Risks

1. **Repository Boundary**: Design system must live in separate repo from Odoo
2. **Fluent UI Versioning**: Stay on v9 (`@fluentui/react-components`), not legacy v8
3. **Storybook as Contract**: All UI components must have stories before production use
4. **Token Pipeline**: Ship scaffold first, token build pipeline second
5. **No Forking Fluent UI**: Wrap it, don't fork it - value is in patterns + product components

---

## Next Steps

1. **Choose repository**: Create `ipai-ui` or use existing `ipai-workspace`
2. **Run bootstrap**: Execute commands in design system repo (NOT in odoo-ce)
3. **Create first component**: Start with basic Button component + story
4. **Set up CI**: Implement token build + Storybook artifact pipelines
5. **Design governance**: Establish review process for new components

---

## References

- [Microsoft 365 Copilot Business](https://www.microsoft.com/en-us/microsoft-365-copilot/business)
- [Fluent UI v9 GitHub](https://github.com/microsoft/fluentui)
- [Fluent 2 Design System Docs](https://fluent2.microsoft.design/get-started/develop)
- [Storybook Documentation](https://storybook.js.org/)
- [@fluentui/react-components on npm](https://www.npmjs.com/package/@fluentui/react-components)

---

**Last Updated**: 2026-01-28
**Version**: 1.0.0
**Status**: Documentation only - awaiting proper repo creation

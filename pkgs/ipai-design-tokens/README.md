# IPAI Design Tokens

Token-driven design system for InsightPulse AI, inspired by Stripe/Supabase patterns.

## Architecture

Single source of truth: `tokens/source/tokens.json`
→ Generates: CSS variables, TypeScript exports, Tailwind preset

## Usage

### In React Components
```tsx
import { tokens } from "@ipai/design-tokens";

<button style={{ backgroundColor: tokens.color.accent.green }}>
  Click me
</button>
```

### In Tailwind
```tsx
<div className="bg-primary text-white">
  Uses token-driven Tailwind preset
</div>
```

## Workflows

### Update Tokens (Local-Source Mode)
1. Edit `tokens/source/tokens.json`
2. Run `pnpm generate:tokens`
3. Commit both tokens.json and generated files

### Sync from Figma (Enterprise)
1. Set env: `FIGMA_FILE_KEY`, `FIGMA_ACCESS_TOKEN`
2. Run `pnpm sync:figma`
3. Run `pnpm generate:tokens`
4. Commit changes

## Token Categories

- **Color**: Primary, accent, text, border, surface
- **Spacing**: Base scale (4px grid)
- **Radius**: Border radius variants
- **Shadow**: Elevation shadows
- **Typography**: Font sizes, weights, line heights (future)

## CI Validation

GitHub Actions validates:
- Generated files match source
- No hardcoded colors in components
- Token usage via ESLint

## Banking-Grade Palette

- **Primary**: Navy #0F2A44 (enterprise, banking)
- **CTA**: Green #7BC043 (primary action, ONE per viewport)
- **Secondary**: Teal #64B9CA (accents, highlights)
- **Highlight**: Amber #F6C445 (promotions, sparingly)

## Generated Files

**DO NOT edit these files manually - they are auto-generated:**

- `css-vars.css` - CSS custom properties
- `tailwind.preset.cjs` - Tailwind configuration
- `src/index.ts` - TypeScript token exports

## Installation

```bash
# Install package
pnpm add @ipai/design-tokens

# Generate tokens
cd packages/ipai-design-tokens
pnpm generate:tokens
```

## Development

```bash
# Generate tokens after editing tokens.json
pnpm generate:tokens

# Watch mode (future)
pnpm generate:tokens --watch
```

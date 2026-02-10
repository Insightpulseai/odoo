# Glass-Card Class Migration

## Problem
3+ components reference undefined "glass-card" CSS class:
- `apps/web/src/components/FeatureCard.tsx`
- `apps/web/src/components/Hero.tsx`
- `apps/web/src/components/ValueProps.tsx`

## Solution
Use new `<Card variant="glass">` component from token-driven system.

## Migration Steps

### Before
```tsx
<div className="glass-card">
  <h3>Feature Title</h3>
  <p>Feature description</p>
</div>
```

### After
```tsx
import { Card } from "@/ui/ipai/Card";

<Card variant="glass">
  <h3>Feature Title</h3>
  <p>Feature description</p>
</Card>
```

## Automated Migration
```bash
# Run codemod script (if available)
node scripts/migrate-glass-card.mjs
```

## Verification
```bash
# Search for remaining usage
grep -r "glass-card" apps/web/src/
# Should return no results
```

## Benefits

1. **Token-Driven**: Glass effect uses design tokens
2. **Type-Safe**: TypeScript props and variants
3. **Composable**: Works with other components
4. **Tested**: Unit and E2E test coverage
5. **Documented**: Clear usage examples and API

## Token Values Used

```tsx
const glassStyles = {
  backgroundColor: "rgba(255, 255, 255, 0.7)",
  backdropFilter: "blur(12px)",
  border: `1px solid ${tokens.color.border}`,
};
```

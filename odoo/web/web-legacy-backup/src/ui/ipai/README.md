# IPAI Component Library

Token-driven React components for InsightPulse AI web application.

## Components

### Button
Token-driven button component with variants: primary, secondary, ghost.

```tsx
import { Button } from "@/ui/ipai/Button";

<Button variant="primary" size="lg">Get Started</Button>
<Button variant="secondary">Learn More</Button>
```

### Card
Card component with variants: default, glass, elevated.

```tsx
import { Card } from "@/ui/ipai/Card";

<Card variant="glass">
  <h3>Glassmorphism Card</h3>
</Card>
```

### Chip
Badge/tag component for status indicators.

```tsx
import { Chip } from "@/ui/ipai/Chip";

<Chip variant="success">Active</Chip>
<Chip variant="accent">Beta</Chip>
```

### Form Components
Form primitives: Form, FormField, FormLabel, FormInput, FormMessage.

```tsx
import { Form, FormField, FormLabel, FormInput } from "@/ui/ipai/Form";

<Form>
  <FormField>
    <FormLabel>Email</FormLabel>
    <FormInput type="email" placeholder="you@example.com" />
  </FormField>
</Form>
```

### Modal
Modal component with overlay and title.

```tsx
import { Modal } from "@/ui/ipai/Modal";

<Modal open={isOpen} onClose={() => setIsOpen(false)} title="Confirm">
  <p>Modal content</p>
</Modal>
```

### Dropdown
Dropdown menu component with alignment options.

```tsx
import { Dropdown, DropdownItem } from "@/ui/ipai/Dropdown";

<Dropdown trigger={<Button>Menu</Button>} align="right">
  <DropdownItem onClick={handleAction}>Action</DropdownItem>
</Dropdown>
```

## Design Principles

1. **Token-Driven**: All colors via `tokens` import, no hardcoded values
2. **Composable**: Small primitives compose into complex UIs
3. **Type-Safe**: Full TypeScript support with prop types
4. **Accessible**: WCAG 2.1 AA compliance (keyboard nav, ARIA labels)

## Platform Kit Inspiration

Components inspired by Supabase Platform UI Kit patterns:
- Clean, minimal aesthetic
- Token-driven design system
- Banking-grade color palette
- Composable architecture

## Testing

All components tested:
- Unit tests: Component rendering, token consumption
- E2E tests: User flows (authentication, forms)

## Usage

```tsx
// Import individual components
import { Button, Card } from "@/ui/ipai";

// Or use barrel export
import { Button } from "@/ui/ipai/Button";
```

## Development

```bash
# Run component tests
pnpm test

# Run E2E tests
pnpm test:e2e

# Type check
pnpm type-check

# Lint
pnpm lint
```

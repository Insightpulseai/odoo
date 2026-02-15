# Color Palettes

## Token Roles (Semantic-First)

Design systems should use semantic color roles, not raw hex values:

| Role | Purpose | Example |
|------|---------|---------|
| `bg` | Page background | `#FFFFFF` / `#0F172A` |
| `surface` | Card/panel background | `#F8FAFC` / `#1E293B` |
| `surface-2` | Nested surface | `#F1F5F9` / `#334155` |
| `text` | Primary text | `#0F172A` (slate-900) |
| `text-muted` | Secondary text | `#475569` (slate-600) minimum |
| `primary` | Brand action color | Varies by brand |
| `primary-hover` | Hover state | 10-15% darker |
| `secondary` | Secondary actions | Neutral or complementary |
| `success` | Positive states | Green family |
| `warning` | Caution states | Amber/yellow family |
| `danger` | Error/destructive | Red family |
| `border` | Default borders | `border-gray-200` light / `border-gray-700` dark |
| `divider` | Section separators | Lighter than border |

## Contrast Rules

- Body text must meet WCAG AA (4.5:1 minimum)
- Use semantic colors only for semantic meaning (don't use `danger` for decoration)
- Avoid saturated colors for large background areas
- Test both light and dark modes before delivery

## Light/Dark Mode Specifics

| Context | Do | Don't |
|---------|----|----- |
| Glass card (light mode) | `bg-white/80` or higher opacity | `bg-white/10` (too transparent) |
| Body text (light mode) | `#0F172A` (slate-900) | `#94A3B8` (slate-400) |
| Muted text (light mode) | `#475569` (slate-600) minimum | gray-400 or lighter |
| Borders (light mode) | `border-gray-200` | `border-white/10` (invisible) |

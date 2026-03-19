# Layout & Spacing

## Grid System

| Breakpoint | Columns | Max Content Width |
|------------|---------|-------------------|
| Desktop (1024px+) | 12-col | 1140–1280px |
| Tablet (768px) | 8-col | Fluid |
| Mobile (< 768px) | 4-col | Fluid |

## Spacing Scale (Token Suggestions)

Use a consistent spacing scale: `4, 8, 12, 16, 24, 32, 48, 64`

All spacing should be multiples of 4px for pixel-perfect alignment.

## Responsive Rules

- Never rely on hover-only interactions (touch devices have no hover)
- Collapse multi-column filters into drawers on mobile
- Test at 375px, 768px, 1024px, 1440px
- Ensure no horizontal scroll on any breakpoint

## Layout-Specific Rules

| Rule | Do | Don't |
|------|----|----- |
| `viewport-meta` | `width=device-width, initial-scale=1` | Omit viewport meta tag |
| `horizontal-scroll` | Ensure content fits viewport width | Allow overflow without scroll affordance |
| `z-index-management` | Define scale (10, 20, 30, 50) | Use arbitrary z-index values |
| `floating-navbar` | Add `top-4 left-4 right-4` spacing | Stick navbar to `top-0 left-0 right-0` |
| `content-padding` | Account for fixed navbar height | Let content hide behind fixed elements |
| `consistent-max-width` | Use same `max-w-6xl` or `max-w-7xl` | Mix different container widths |

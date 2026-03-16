# Components & Patterns

## Core Components

Every application needs these baseline components:

- **Navigation** — side nav or top nav + breadcrumbs
- **Cards** — content containers with consistent padding and borders
- **Tables** — data display with sorting, filtering, pagination
- **Forms** — input groups with labels, validation, error states
- **Modals/Drawers** — overlay content for secondary actions
- **Toasts** — non-blocking status notifications
- **Empty States** — meaningful content when no data exists
- **Loading States** — skeleton screens or spinners during async operations

## Interaction Patterns

| Pattern | When to Use |
|---------|-------------|
| Progressive disclosure | Details panels, expandable rows, accordion sections |
| Primary action per screen | One clear CTA; secondary actions visually subordinate |
| Default-safe states | No blank screens; always show helpful content or guidance |
| Optimistic updates | Update UI immediately, reconcile on server response |

## Interaction Rules

| Rule | Do | Don't |
|------|----|----- |
| `cursor-pointer` | Add to all clickable/hoverable elements | Leave default cursor on interactive elements |
| `hover-feedback` | Provide visual feedback (color, shadow, border) | No indication element is interactive |
| `smooth-transitions` | Use `transition-colors duration-200` | Instant changes or too slow (>500ms) |
| `stable-hover-states` | Use color/opacity transitions | Use scale transforms that shift layout |
| `loading-buttons` | Disable button during async operations | Allow double-clicks |
| `error-feedback` | Clear error messages near the problem field | Vague errors at page top |

## Pre-Delivery Component Checklist

- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide clear visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation
- [ ] Use theme colors directly (bg-primary) not var() wrapper

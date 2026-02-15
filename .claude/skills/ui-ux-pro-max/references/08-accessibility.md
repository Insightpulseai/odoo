# Accessibility Checklist

## Contrast (WCAG AA Minimum)

| Element | Minimum Ratio | Standard |
|---------|--------------|----------|
| Normal text (< 18px) | 4.5:1 | WCAG AA |
| Large text (>= 18px bold or 24px) | 3:1 | WCAG AA |
| UI components and graphics | 3:1 | WCAG 2.1 AA |

## Keyboard Navigation

- **Focus visible** — all interactive elements must show a focus ring
- **Tab order logical** — follows visual reading order (top-left to bottom-right)
- **All controls reachable** — every interactive element accessible without mouse
- **Escape closes modals** — standard dismissal behavior
- **Skip to main content** — link for keyboard users to bypass navigation

## Forms

- **Labels exist** — every input has an associated `<label>` (not placeholder-only)
- **Error messaging linked** — use `aria-describedby` to connect error text to field
- **Required fields indicated** — mark required fields visually and with `aria-required`
- **Group related fields** — use `<fieldset>` and `<legend>` for related inputs

## Images & Media

- **Alt text** — descriptive alt for meaningful images; empty `alt=""` for decorative
- **Video captions** — provide captions or transcripts
- **`prefers-reduced-motion`** — disable/reduce animations for users who request it

## ARIA Usage

| Rule | Do | Don't |
|------|----|----- |
| `aria-labels` | Add `aria-label` to icon-only buttons | Rely on visual icon alone |
| `aria-live` | Use for dynamic content updates (toasts, counters) | Omit for auto-updating regions |
| Semantic HTML | Use `<button>`, `<nav>`, `<main>`, `<header>` | Use `<div>` for everything |
| Roles | Only add roles when no semantic element exists | Override native element semantics |

## Pre-Delivery Accessibility Checklist

- [ ] All images have alt text (descriptive or empty for decorative)
- [ ] Form inputs have `<label>` elements with `for` attribute
- [ ] Color is not the only indicator for any state
- [ ] Focus rings visible on all interactive elements
- [ ] Tab order matches visual reading order
- [ ] `prefers-reduced-motion` respected
- [ ] Minimum 4.5:1 contrast ratio for body text
- [ ] Skip-to-content link present

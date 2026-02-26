---
name: oca-owl-standards
description: Elite OWL (Odoo Web Library) development standards based on OCA 2026 training. Use for building dynamic Odoo UIs, custom widgets, and complex frontend logic.
license: AGPL-3
metadata:
  author: InsightPulseAI
  version: "1.0.0"
---

# OCA OWL 2026 Standards

Building "Enterprise-killing" Odoo CE frontends using the latest OWL (Odoo Web Library) patterns.

## Core Patterns

### 1. Component Lifecycle & Hooks

- **Reactivity**: Use `useState` for internal state and `useState(props)` for reactive props.
- **Hooks**: Prefer `onWillStart` for data fetching and `useEffect` for DOM side-effects.
- **Services**: Use `useService('rpc')`, `useService('action')`, etc., instead of legacy global objects.

### 2. Performance & Structure

- **Fragments**: Use `<t t-call="..." />` and owl fragments to keep components small.
- **Keyed Loops**: Always use `t-key` in `t-foreach` to optimize reconciliation.
- **Lazy Loading**: Use `onWillStart` to load heavy assets only when needed.

### 3. OCA Integration Patterns

- **Standard Actions**: Extend `ActionMenus` and `ControlPanel` using standard OCA patches.
- **Consistency**: Follow the OCA CSS naming convention (prefix with `o_oca_`).

## Odoo 19 + OWL 2.0+ Specifics

- **use() Hook**: Embrace the new `use()` hook for consuming providers in Odoo 19.
- **Simplified Syntax**: Use the latest Owl template syntax (e.g., self-closing tags).

## Implementation Checklist

- [ ] Is the state minimally sufficient?
- [ ] Are all external services accessed via `useService`?
- [ ] Does the component handle `onWillUpdateProps` correctly for prop-driven refreshes?
- [ ] Are sub-components properly scoped?

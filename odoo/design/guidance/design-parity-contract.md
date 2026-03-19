# Design Parity Contract

All product surfaces must implement the governed design system in `design/`.

## Source-of-truth order

1. `design/foundations/tokens/*` — color, typography, spacing, radius, elevation, shadow, motion, z-index, iconography
2. `design/components/fluent-mappings/*` — component semantics and interaction states
3. `design/assets/*` — brand, icons, illustrations, media
4. `design/guidance/*` — content style, imagery, motion principles

## Upstream reference

Fluent UI / Fluent 2 is the upstream component and interaction reference system.
Fluent governs component semantics, token categories, and accessibility defaults.
Company-specific brand tokens, assets, and guidance are repo-local — they do not live in vendor paths.

## Required parity

Every UI change must conform to:

- approved color, type, spacing, radius, elevation, and motion tokens
- approved interaction/state behavior (see `interaction-map.yaml`)
- approved iconography and imagery rules
- approved component mappings to Fluent UI semantics (see `component-map.yaml`)

## Forbidden drift

Do not introduce:

- hardcoded hex values
- one-off shadows or drop-shadows
- one-off border radii
- one-off animation curves/durations
- unregistered illustrations or brand graphics
- component variants that bypass the mapping contract

## Override rule

If a surface cannot follow Fluent UI behavior or tokens exactly, document in `design/validation/parity-overrides.yaml`:

- why (rationale)
- scope (file paths affected)
- replacement token/component rule
- approval owner
- expiry/review date

Expired overrides fail CI.

## Enforcement

CI enforces parity using `design/validation/parity-rules.yaml`.

A pull request fails when it introduces:

- hardcoded visual values outside governed token rules
- unregistered components or states
- assets outside approved roots
- undocumented design exceptions
- expired overrides

Any exception must be recorded in `design/validation/parity-overrides.yaml`.

## Cross-references

- `design/validation/parity-rules.yaml` — machine-readable enforcement rules
- `design/components/fluent-mappings/component-map.yaml` — component registry
- `design/components/fluent-mappings/interaction-map.yaml` — interaction state contract
- `design/validation/parity-overrides.yaml` — exception registry
- `design/README.md` — extraction pipeline and token resolution

---

*Last updated: 2026-03-17*

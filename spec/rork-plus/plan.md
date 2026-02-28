# Plan — Rork Plus

## Phase 0 — Foundations (2–3 weeks)
- Define Spec Graph schema (`app/spec/app.json`)
- Implement deterministic run metadata:
  - generator_version, model_id, prompt_hash, dependency_lock_hash
- Establish repo layout + protected "escape hatch" folders

## Phase 1 — Git-first workflow (2–4 weeks)
- Default "Generate" creates a branch + PR
- PR template includes:
  - prompt transcript (redacted)
  - spec diff
  - code diff
  - verify report

## Phase 2 — Verification pipeline (3–5 weeks)
- Hosted runners: lint/typecheck/tests/build
- Artifact upload + retention policy
- "Release Candidate" gating

## Phase 3 — Integrations marketplace (4–6 weeks)
- Typed integration interface
- Ship 3 "golden path" integrations:
  - paywall (Superwall or RevenueCat)
  - auth (Supabase)
  - analytics (PostHog)
- Formalize existing paywall setup guides into typed adapters

## Phase 4 — Publishing automation (ongoing)
- App Store/Play metadata generators
- Preflight compliance checks
- Signing key vault flows

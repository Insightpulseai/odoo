# PRD — Rork Plus (Improved Rork)

## Context
Rork is positioned as a browser-based platform that generates mobile apps from plain language and manages design + builds + store readiness, with docs covering GitHub sync and monetization integrations.
Rork Plus upgrades that experience for **teams and serious builders** by making generation **deterministic, Git-native, testable, and enterprise-safe**.

## Problem
AI app builders often fail for serious use because:
- Generated code is hard to maintain or reproduce (non-deterministic diffs).
- Hosting/build pipelines are opaque; debugging is painful.
- Secrets and integrations become ad-hoc.
- "Ship fast" conflicts with App Store readiness, QA, and compliance.

## Goals
1. **Git-first projects**: every app is a repo with structured commits per change-set.
2. **Deterministic generation**: pinned generator versions + replayable prompts.
3. **One-click verified release**: build + tests + store artifacts produced by CI runners.
4. **Pluggable integrations**: payments, analytics, auth, storage via typed adapters (no hardcoding).
5. **Team-grade governance**: roles, environments, audit logs, and review workflows.

## Non-goals
- Replacing App Store / Play Console requirements.
- Becoming a general web app builder (mobile-first remains the wedge).
- Hosting every possible backend (support "bring your own backend").

## Users
- **Solo maker**: wants speed + monetization templates.
- **Indie studio**: needs GitHub flow, CI builds, test gating.
- **Enterprise team**: needs SSO, auditability, environment separation, policy gates.

## Solution Alignment

Rork Plus solves these problems by inserting a **Spec Graph** intermediary between natural language and generated code, enforcing Git-first workflows, mandatory verification gates, and typed integration adapters. Every generation run is deterministic, auditable, and reproducible.

---

## Core experience
### 1) Prompt → Spec Graph (new)
Instead of directly generating code, convert chat into a **versioned Spec Graph**:
- Screens, navigation, state, data models, integrations, permissions, analytics events.
- Stored as `app/spec/app.json` + `app/spec/decisions.md`.

### 2) Spec Graph → Code (improved)
Generate code with:
- Strict module boundaries (ui/, domain/, data/, integrations/, tests/).
- Typed contracts for integrations.
- "Escape hatch" zones where user code is never overwritten.

### 3) Verify (mandatory)
Every generation run produces:
- unit tests scaffold + snapshot tests
- lint/typecheck
- build artifacts
- a "release candidate" report with blocking issues

### 4) Publish (safer)
Rork Plus adds:
- Environment staging (dev/stage/prod)
- Signing key handling via vault
- Preflight checklist automation (permissions, privacy strings, screenshots, metadata)

## Key features
### A. GitHub-native by default
Every run opens a PR. GitHub sync is the default, not optional.
- Branch per "intent"
- PR contains: prompt transcript → spec diff → code diff → verification artifacts

### B. Deterministic generator
- Pin generator version + model version + dependency lockfiles
- Cache builds; reproduce any prior build exactly

### C. Integration Marketplace (typed)
Integrations installable as **typed packages**:
- Payments: RevenueCat/Superwall adapters
- Auth: Supabase / custom OAuth
- Analytics: PostHog/GA/Amplitude adapters

### D. "Rork Max" parity but transparent
Premium quality with full transparency:
- clear diffs (what changed, why)
- no hidden layers (everything committed)

### E. Hosted "Preview on Device" pipeline
Fast iteration without local Xcode/Android Studio:
- ephemeral preview builds
- QR install links
- crash logs + session replays

## Data & architecture
- **Project store**: Spec Graph + build events + artifacts + audit logs
- **Artifact store**: build outputs, screenshots, logs
- **Secrets store**: signing keys, API keys, tokens (policy-enforced)
- **Runners**: isolated containers per build

## Metrics (success criteria)
- Time-to-first-running-app < 15 minutes for simple apps
- 95% of runs produce buildable output on first attempt (template cohort)
- 99% reproducibility for tagged releases
- <1% secrets-policy violations in CI

## Risks
- Determinism vs model creativity tradeoff
- Store policy drift (Apple/Google requirements change)
- Cost control for hosted builds (needs quotas + caching)

## Open questions (tracked, not blocking)
- Default stack: Swift vs React Native/Expo as primary

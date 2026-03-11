# Constitution — Rork Plus (Improved Rork)

## Mission
Enable anyone to ship **maintainable, auditable, and secure** mobile apps from natural language, without trapping teams in a proprietary build/runtime.

## Non-negotiables
1. **Source is the product**: every app is a real repo (Git-first), not a black-box project. (Rork already emphasizes browser workflow; Rork Plus makes Git the default.)
2. **Deterministic builds**: same input spec + same versioned toolchain → same output artifacts.
3. **No secret leakage**: secrets never appear in client bundles; managed via a vault + environment bindings.
4. **Debuggable by design**: any generated code must be runnable locally, testable, and inspectable.
5. **Progressive disclosure**: novices can ship; experts can override (escape hatches are first-class).

## Product principles
- **Spec → Code → Verify loop**: generation is incomplete unless validated by tests/lints/build.
- **Separation of concerns**: UI, domain, data access, and integrations are modular.
- **Composable backends**: generated apps can attach to Supabase, Firebase, or custom APIs; no lock-in.
- **Observable automation**: every agent action emits traceable events (prompts, diffs, build logs).

## Guardrails
- Disallow "magic" edits that can't be replayed (no untracked manual patching in hosted runners).
- Enforce security gates on publication steps (App Store/Play Store).

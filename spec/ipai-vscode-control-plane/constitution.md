# IPAI VS Code Control Plane — Constitution

## 1. Non-Negotiables

- **Spec Kit is the SSOT**
  No operation may execute without a complete spec bundle.

- **No manual UI operations**
  All actions must be reproducible via code, CLI, or agent execution.

- **Diff-first execution only**
  No mutation without a previewable diff.

- **Evidence is mandatory**
  Every mutation must generate an evidence bundle.

- **Read-only by default**
  Mutations require explicit, scoped confirmation.

- **No hallucinated AI behavior**
  AI may only operate through constrained, named commands.

---

## 2. Architectural Invariants

- VS Code extension contains **zero business logic**
- All logic lives in:
  - deterministic scripts
  - validators
  - control-plane APIs
- VS Code is a **surface**, not the system

---

## 3. AI Governance Rules

AI MUST:
1. Read specs
2. Generate patch-only diffs
3. Run validators
4. Emit evidence
5. Await confirmation

AI MUST NOT:
- mutate files directly
- invent modules, paths, or schemas
- bypass validation gates

---

## 4. Security Rules

- No secrets stored in extension
- Credentials resolved via:
  - environment
  - Supabase Vault
  - OS keychain
- All actions logged

---

## 5. Failure Policy

If any invariant is violated:
- execution is blocked
- error is surfaced in VS Code
- no partial state is allowed

# Copilot-Optimized Work Item Template (Azure Boards → GitHub Copilot)

> Template for Azure Boards work items that launch GitHub Copilot Coding Agent.
> Path: Azure Boards work item → Start with Copilot → GitHub branch + draft PR.
> Applies to: PBI, Bug, Task, User Story, Issue. **Not Azure Repos** (GitHub only).
> Canonical merge gate is **Azure Pipelines** (per CLAUDE.md authority matrix);
> GHA validation is scoped exception per `ssot/governance/gha-scoped-exception.yaml`.

---

## 1. What Copilot receives as prompt context

Only these fields are shared with GitHub Copilot:

- **Title**
- **Description** (rich text)
- **Acceptance Criteria** (rich text)
- **Comments**
- Link back to the work item

Therefore: treat these fields as **prompt content**. Vague → vague code. Structured → structured code.

## 2. Sizing rule

A Copilot-ready work item is:

- **One bounded implementation slice** (not an umbrella epic)
- **Completable in a single PR** (no cross-item dependency)
- **Testable on a single GitHub repo** (one repo per work item)
- **Unambiguous scope** (what is in, what is out)

Microsoft's limitations:
- ❌ Dependencies between work items not supported
- ❌ Multiple concurrent Copilot ops across work items not supported
- ❌ Overly verbose descriptions reduce effectiveness

Break larger Epics into slices that meet the above.

---

## 3. Canonical work item structure

```markdown
Title:
  [verb-first, specific, ≤80 chars]
  Examples:
    ✅ "Add 2307 release blocker when final certificate PDF missing"
    ✅ "Fix Entra Agent ID missing scope for pulser-finance"
    ❌ "Improve finance module" (too vague)
    ❌ "Refactor everything" (too broad)

Description:
  ## Context
  [1-3 sentences: why this matters, which IPAI layer is affected]

  ## Business rule / behavior
  [precise, testable statement of expected behavior]

  ## Scope
  - In scope: [explicit list]
  - Out of scope: [what NOT to touch]

  ## Files and paths to touch
  - addons/ipai/<module>/models/<file>.py
  - addons/ipai/<module>/views/<file>.xml
  - addons/ipai/<module>/tests/<file>.py
  [do NOT include documentation-only or unrelated paths]

  ## Target GitHub repo
  - Insightpulseai/<repo>
  - Branch base: main

  ## Technical constraints
  - [relevant invariants from CLAUDE.md, e.g., "Managed Identity only"]
  - [existing patterns to follow, e.g., "Mirror OCA module structure"]

Acceptance criteria:
  [numbered list of testable conditions]
  1. [state after]
  2. [observable behavior]
  3. [test file exists + passes]
  4. [specific edge case handled]
  5. [no regression in X]

Comments (optional):
  [clarifications as they come up during implementation]

Labels/tags:
  [wave-1|wave-2|wave-3|platform|marketplace|security|...]
```

---

## 4. IPAI-specific examples

### Example A — Finance ops PBI (BIR compliance)

```
Title:
  Add 2307 release blocker when final certificate PDF missing

Description:
  ## Context
  Philippine BIR requires Form 2307 (Certificate of Creditable Tax Withheld) before
  vendor invoice release. Current flow allows release without the PDF attached.

  ## Business rule
  When a vendor invoice has tax_type=creditable_withholding AND no attachment
  matching pattern "2307*.pdf" OR "*_2307.pdf", block state transition from
  draft to posted. Display findings on the form header.

  ## Scope
  - In scope:
    - addons/ipai/ipai_bir_compliance/models/account_move.py
    - Field: `has_2307_certificate` (boolean, computed)
    - Override: `action_post()`
    - View: header banner when findings present
  - Out of scope:
    - Database migration (add field via `_auto_init`)
    - BIR API integration (out of scope for this item)
    - Historical data backfill (separate item)

  ## Files to touch
  - addons/ipai/ipai_bir_compliance/models/account_move.py
  - addons/ipai/ipai_bir_compliance/views/account_move_form.xml
  - addons/ipai/ipai_bir_compliance/tests/test_2307_blocker.py

  ## Target GitHub repo
  - Insightpulseai/odoo
  - Branch base: main

  ## Technical constraints
  - Must use `@api.constrains` decorator (no override of create/write)
  - Use Odoo's `UserError` for blocking message
  - Follow OCA module layout
  - Test must use TransactionCase with disposable test DB

Acceptance criteria:
  1. Posting a vendor invoice with tax_type=creditable_withholding and no 2307
     PDF raises UserError with message "Form 2307 required before posting"
  2. Posting succeeds when 2307 PDF is attached matching naming pattern
  3. Form header banner displays "Missing Form 2307" in red when condition is met
  4. Test file `test_2307_blocker.py` covers: (a) posting blocked, (b) posting
     allowed, (c) banner visible, (d) banner hidden after attachment
  5. Module installs cleanly on fresh DB; no migration errors

Labels: finance, bir-compliance, pulser, wave-1
```

### Example B — Agent platform security

```
Title:
  Fix Entra Agent ID missing scope for pulser-finance

Description:
  ## Context
  pulser-finance agent was registered as Entra app 49aceaad-554d-4cd9-89d6-7d5cb388a508
  on 2026-04-15 but lacks required scope for calling Pulser API.

  ## Business rule
  Agent token must include scope `api://ipai-copilot-gateway/.default` to
  authenticate calls to pulser-api. Currently failing with 401.

  ## Scope
  - In scope:
    - Entra admin portal: add API permission on app 49aceaad
    - Grant admin consent
    - Update `agents/pulser-surface/appPackage/manifest.json` with scope
    - Verify smoke test
  - Out of scope:
    - pulser-ops and pulser-research (separate work items)
    - API gateway changes (already correctly configured)

  ## Files to touch
  - agents/pulser-surface/appPackage/manifest.json
  - agents/evals/judges/pulser-finance-auth.md

  ## Target GitHub repo
  - Insightpulseai/agents

  ## Technical constraints
  - Must use managed identity; no client secrets
  - Admin consent required (only Jake can grant)
  - Scope must be read-only: no write permissions

Acceptance criteria:
  1. pulser-finance agent token includes api://ipai-copilot-gateway/.default scope
  2. Smoke test `GET /api/pulser/health` returns 200 from pulser-finance identity
  3. Manifest updated in agents repo; new version committed
  4. Admin consent granted in Entra admin center (evidence: screenshot in docs/evidence/)

Labels: security, entra, pulser-agent, wave-1
```

---

## 5. Anti-patterns (don't do these)

| Anti-pattern | Why it fails Copilot |
|---|---|
| "Refactor finance module" | No bounded scope — Copilot sprays changes |
| "Improve performance" | No measurable criterion |
| "Add AI to accounting" | Too abstract — no concrete files/behavior |
| 2-page description | Exceeds useful prompt budget; Copilot loses focus |
| Multiple acceptance criteria across different features | Breaks the "single PR" constraint |
| Dependency on another work item | Integration explicitly unsupported |

---

## 6. Post-Copilot PR review gate

Even though Copilot launches from Azure Boards, every PR still goes through:

1. **Author self-review** — did Copilot match scope?
2. **Test execution** — Azure Pipelines runs canonical gate (authority matrix)
3. **Human reviewer** — at least one approver
4. **Merge via Azure Pipelines** — not GHA

Copilot generates drafts. Humans (and Azure Pipelines) decide what merges.

---

## 7. Decision tree — when to use Copilot launch

```
Is the work item bounded, specific, single-repo?
├── Yes → Launch Copilot from Boards. Track draft PR. Review.
└── No
    ├── Multi-repo? → Break into per-repo slices.
    ├── Ambiguous? → Write spec bundle first (`spec/<feature>/`).
    └── Has dependencies? → Sequence: resolve deps first, then launch.
```

---

## 8. Integration with IPAI spec-kit workflow

Recommended flow:

```
1. spec/<feature>/ bundle exists (constitution + PRD + plan + tasks)
2. Break tasks.md checkboxes into Copilot-ready work items
3. Each work item references spec bundle path
4. Copilot launch produces draft PR
5. PR merges → mark task [x] in spec/<feature>/tasks.md
```

Spec bundles are the **source of scope truth**. Work items are the **execution unit**. Copilot is the **implementer**. Azure Pipelines is the **gate**.

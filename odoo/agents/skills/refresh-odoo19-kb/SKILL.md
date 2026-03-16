# SKILL: Refresh Odoo 19 Knowledge Base (Vendored, Pinned, Indexed)

## Skill ID

refresh-odoo19-kb

## Skill Type

Procedural (Deterministic)

## Risk Level

LOW

## Requires Approval

false

## Supported Odoo Versions

- 19.0 CE

## Scope

- Documentation only
- No runtime, DB, or environment mutations

---

## Purpose

Refresh the **Odoo 19 documentation knowledge base** in a reproducible,
auditable, and CI-verifiable way by:

1. Vendoring upstream docs from `odoo/documentation` (branch 19.0)
2. Pinning to an immutable upstream commit
3. Verifying pin integrity
4. Indexing content into structured KB artifacts
5. Producing evidence for traceability

This skill is the **only permitted mechanism** to update `docs/kb/odoo19/`.

---

## Preconditions (MUST ALL BE TRUE)

1. Repository is clean (no uncommitted changes under `docs/kb/odoo19/`)
2. Git is available in PATH
3. Network access to `https://github.com/odoo/documentation`
4. `scripts/kb/vendor_odoo_docs.py` exists
5. `scripts/kb/verify_odoo_docs_pin.py` exists
6. `scripts/kb/index_odoo_docs.py` exists

If any precondition fails → **abort immediately**.

---

## Inputs

```yaml
odoo_version: "19.0"
upstream_repo: "https://github.com/odoo/documentation"
branch: "19.0"
commit: optional string # explicit SHA; if omitted, latest origin/19.0 is used
```

---

## Hard Rules (NON-NEGOTIABLE)

- ❌ NEVER index live upstream content without vendoring
- ❌ NEVER index without pin verification
- ❌ NEVER mutate existing KB files in-place
- ❌ NEVER skip evidence generation
- ❌ NEVER allow partial success

Violation of any rule → **FAIL SKILL**

---

## Execution Steps (ORDER IS MANDATORY)

### Step 1 — Create Evidence Run

Create directory:

```
docs/evidence/<YYYY-MM-DD>/kb/refresh/<run_id>/
```

Record:

- input parameters
- invocation timestamp (UTC)
- git HEAD of this repo

---

### Step 2 — Vendor Upstream Documentation

Execute:

```text
python3 scripts/kb/vendor_odoo_docs.py \
  --upstream-url=https://github.com/odoo/documentation \
  --branch=19.0 \
  [--commit=<commit>]
```

Expected outputs:

- `docs/kb/odoo19/upstream/`
- `docs/kb/odoo19/UPSTREAM_REV.txt`
- Updated `docs/kb/odoo19/UPSTREAM_PIN.json`

Fail if:

- git clone/fetch fails
- upstream snapshot is empty
- pinned_commit remains placeholder

---

### Step 3 — Verify Upstream Pin Integrity

Execute:

```text
python3 scripts/kb/verify_odoo_docs_pin.py
```

Verification logic:

- If upstream is git checkout → compare HEAD
- If directory snapshot → compare UPSTREAM_REV.txt
- Must match `UPSTREAM_PIN.json.pinned_commit`

Any mismatch → **FAIL SKILL**

---

### Step 4 — Index Content (Upstream + Stack + Overrides)

Execute:

```text
python3 scripts/kb/index_odoo_docs.py
```

This produces **canonical machine-readable artifacts**:

- `docs/kb/odoo19/manifest.json` (Global manifest of all layers)
- `docs/kb/odoo19/sections.json`
- `docs/kb/odoo19/topics.json`
- `docs/kb/odoo19/skills_coverage.json`
- `docs/kb/odoo19/nav.json` (Navigation tree)
- `docs/kb/odoo19/index.json` (Search index)

Fail if:

- any index file missing
- any index file is empty
- indexer raises error

---

### Step 5 — Post-Index Validation

Validate:

- All index JSON files parse correctly
- All include `source_commit == pinned_commit` (implicit via determinism)
- No index references files outside `upstream/`

---

### Step 6 — Record Evidence

Write into evidence directory:

- `inputs.json`
- `upstream_pin.json` (copy of UPSTREAM_PIN.json)
- `upstream_rev.txt`
- `index_manifest.json` (list + checksums of index outputs)
- `final_status.json`

Missing evidence → **FAIL SKILL**

---

### Step 7 — Finalize Skill

If all steps succeed:

- Mark skill run as `success`
  Else:
- Mark skill run as `failed`

No partial success allowed.

---

## Allowed LLM Routing (Cost-Controlled)

Local SLMs **MAY** be used for:

- Document classification
- Section tagging
- Index validation summaries
- Log parsing

Local SLMs **MUST NOT** be used for:

- Vendoring
- Git operations
- Pin verification
- Index generation control flow

Remote LLMs are optional but not required.

---

## Failure Modes

| Failure              | Result |
| -------------------- | ------ |
| Upstream unreachable | Abort  |
| Pin mismatch         | Abort  |
| Index missing        | Abort  |
| Evidence incomplete  | Abort  |
| Script error         | Abort  |

No retries unless explicitly re-run.

---

## Postconditions

On success:

- KB snapshot is immutable and pinned
- Index artifacts are deterministic
- Evidence exists for audit & CI
- Agents may safely rely on KB

---

## Notes for Agents

- Do NOT infer missing inputs
- Do NOT auto-update pins without vendoring
- Do NOT modify upstream filters
- Treat KB as read-only outside this skill

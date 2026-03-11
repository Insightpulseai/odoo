# spec/continue-plus/prd.md

## 1. Product summary

**Continue+** is an improved "docs → code" agentic development platform built on top of Continue's IDE-native workflow, adding **spec-kit enforcement**, **deterministic multi-agent orchestration**, and **CI-aware execution** so agent-generated work reliably ships in repos with heavy CI (e.g., OCA/Odoo, monorepos) without noisy failures.

Continue+ keeps the strengths of Continue (local, IDE-first, repo-aware) while fixing the core production pain points:

* agents change infra/docs → CI explodes
* rules drift across repos
* no standard "plan → implement → verify" contract
* lack of PR-grade accountability (evidence, checks, traceability)

## 2. Problem statement

Teams using IDE agents frequently hit predictable failure modes:

1. **CI mismatch**

* agent makes non-code changes but triggers full pipelines (e.g., OCA matrix)
* PRs go red, slowing merges and lowering trust

2. **Non-deterministic behavior**

* "agent" behavior varies by prompt/ruleset; hard to reproduce or audit

3. **No execution contract**

* planning, implementation, verification are mixed
* output is not reliably review-ready

4. **No repo-standard governance**

* rules live in inconsistent formats across `.continue/`, `CLAUDE.md`, READMEs
* missing enforcement that specs exist and are non-placeholder

## 3. Goals

* Make "docs → code" **repeatable** and **mergeable**
* Enforce a **single execution contract** across repos
* Keep the experience **IDE-native** and fast
* Reduce CI noise by making agents **CI-aware**
* Produce PR-ready outputs with evidence: checks, diffs, summaries

## 4. Non-goals

* Autonomous long-running agents
* Replacing CI systems or Git providers
* Hosting proprietary model infrastructure
* Full SCM management (Continue+ integrates; it doesn't replace GitHub/GitLab)

## 5. Target users

* **Founders / solo engineers** shipping fast with IDE agents
* **Platform/DevEx** teams standardizing agent behavior across repos
* **Teams with heavy CI** (monorepos, OCA/Odoo, regulated workflows)

## 6. Core user stories

1. As a dev, I want to run **/plan** and get a file-level change plan without edits.
2. As a dev, I want **/implement** to only execute the plan and keep diffs minimal.
3. As a dev, I want **/verify** to run checks and loop until green.
4. As a reviewer, I want PR summaries that include **what changed**, **why**, and **verification evidence**.
5. As a platform owner, I want **Spec Kit enforcement** so every repo has constitution/prd/plan/tasks and no placeholders.
6. As a CI owner, I want agent changes to **skip irrelevant pipelines** when only docs/spec/agent config changed.

## 7. Requirements

### 7.1 Spec Kit enforcement

**R1. Spec bundle presence**

* Continue+ must detect `spec/<slug>/{constitution,prd,plan,tasks}.md`
* It must block "ship" actions if the bundle is missing.

**R2. Spec quality checks**

* Must flag placeholders (TODO/TBD/LOREM)
* Must enforce minimum substantive content per file

**R3. Spec ↔ PR traceability**

* PR description must reference spec slug and tasks checklist

### 7.2 Deterministic multi-agent orchestration

**R4. Role separation**

* Provide three deterministic roles:

  * Planner (no edits)
  * Implementer (edits only)
  * Verifier (runs checks, fixes, reruns)

**R5. Standard commands**

* `/plan`, `/implement`, `/verify`, `/ship`
* Each command has a stable output format (headings + required sections)

**R6. Artifacted reasoning**

* No hidden "magic" state: outputs are written to repo docs (e.g., spec plan/tasks updates) or PR summary blocks

### 7.3 CI-aware execution

**R7. Diff classification**

* Continue+ must classify changed files into categories:

  * code paths
  * docs/spec paths
  * infra/workflows
  * tests
* The classification must be used to recommend or apply CI short-circuit logic.

**R8. CI gating templates**

* Provide drop-in workflow snippets:

  * `paths-ignore` for docs-only changes
  * a "preflight classify" job to gate heavy jobs

**R9. Repo policy integration**

* When repo has a rule like "infra changes must not trigger heavy CI", Continue+ must enforce it during `/ship`.

### 7.4 PR-grade outputs

**R10. Verification evidence**

* `/verify` must end with pass/fail plus command outputs summary
* `/ship` must include what was run and what passed

**R11. Minimal diffs**

* Implementer must prefer smallest patch that satisfies plan

**R12. Safety & tool allowlists**

* Continue+ must respect repo allowlists (shell commands, file ops)
* Must not run non-allowlisted commands

## 8. UX and workflow

### 8.1 IDE workflow

* A command palette or chat panel supports:

  * `/plan <request>`
  * `/implement <request or plan ref>`
  * `/verify`
  * `/ship`

### 8.2 Required output formats

**/plan output**

* Scope
* Assumptions
* Files to change (explicit list)
* Risks/rollback
* Verification commands
* Tasks checklist (copy into `spec/<slug>/tasks.md`)

**/implement output**

* Files changed
* Summary per file
* Notes on deviations from plan (must be explicit)

**/verify output**

* Commands executed
* Failures and fixes
* Final status

**/ship output**

* PR description block (ready to paste)
* Spec references
* Verification evidence

## 9. Architecture

### 9.1 Local-first core

* Continues to run in IDE
* Uses repo files for policy and state:

  * `CLAUDE.md` and/or `.continue/rules/*.md`
  * `spec/<slug>/*`

### 9.2 Orchestrator layer

* A thin orchestrator interprets commands and enforces:

  * role boundaries
  * spec presence/quality
  * CI classification logic
  * output formatting guarantees

### 9.3 CI templates library

* Ships a template set under:

  * `infra/ci/continue-plus/`
* Includes:

  * `spec-kit-enforce.yml`
  * `agent-preflight.yml`
  * "skip-heavy-ci" patterns for common ecosystems

## 10. Data model

* Repo state is file-based; no required external DB.
* Optional telemetry (opt-in):

  * command success rate
  * verification pass rate
  * PR merge time impact

## 11. Security and compliance

* Default deny tool execution beyond allowlists
* No secret echoing
* CI templates should avoid leaking env in logs

## 12. Metrics

* % PRs green on first run
* Median time from `/plan` to merge
* CI minutes saved due to correct gating
* Reviewer interventions per PR

## 13. Rollout plan

### Phase 1: Spec kit + role commands

* Add enforcement + command definitions
* Standardize output formats

### Phase 2: CI-aware classification + templates

* Add diff classifier
* Add recommended CI patches

### Phase 3: PR evidence automation

* Auto-generate PR description block
* Add verification evidence snippets

## 14. Open questions

* Should spec enforcement be "warn" vs "block" by default?
* How to detect "heavy CI" per repo (heuristics vs config)?
* Where should CI templates live (repo vs centralized starter kit)?

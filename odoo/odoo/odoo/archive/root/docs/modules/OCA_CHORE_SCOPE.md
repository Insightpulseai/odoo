# OCA-style "chore" Scope Conventions

Use **Conventional Commits + OCA hygiene + deterministic outputs**.

---

## 1. When to Use Each Chore Scope

| Scope | When to Use |
|-------|-------------|
| `chore(oca):` | OCA layer management: `oca/` submodules, `oca.lock.json`, `oca-aggregate.yml`, OCA addon list/pins/vendor sync, OCA compliance doc updates |
| `chore(repo):` | Repo-wide maintenance not specific to OCA (docs regen, tree/sitemap, formatting, housekeeping) |
| `chore(ci):` | Workflows, gating, pre-commit, drift checks |
| `chore(deps):` | Python/Node deps, devcontainer, toolchain pins |
| `chore(deploy):` | DO compose, caddy/nginx, env templates, infra docs |

---

## 2. Scope Rules (OCA Convention)

Prefer narrow scopes that map to folders:

- `chore(oca): ...` — global OCA operations
- `chore(oca-sync): ...` — sync/update/pin operations
- `chore(addons): ...` — non-OCA module movement only
- `chore(docs): ...` — documentation updates
- `chore(scripts): ...` — script maintenance
- `chore(deploy): ...` — deployment configuration

---

## 3. OCA-style Branch + PR Pattern

### Branch Naming

```
chore/oca-<short-slug>
```

### PR Title Format

```
chore(oca): <imperative summary>
```

### PR Body Requirements

PR body must include:

1. **Why** — what was broken / what changed upstream
2. **What** changed — pins, submodules, manifests
3. **Verification** — commands + `git diff --exit-code …` checks

---

## 4. Deterministic Gates (Run Before Shipping)

Run these exact drift checks locally (or in cloud IDE) before shipping a chore PR:

```bash
# 1) Pre-commit / lint (whatever your repo uses)
pre-commit run -a || true

# 2) Data model drift (if the chore touches models/docs)
python scripts/generate_odoo_dbml.py
git diff --exit-code docs/data-model/

# 3) Seed drift (if seed generator/seed artifacts touched)
python scripts/seed_finance_close_from_xlsx.py
git diff --exit-code addons/ipai_finance_close_seed

# 4) Repo structure docs drift (TREE/SITEMAP generators)
# (run your repo's script if present; else rely on CI auto-update)
git diff --exit-code SITEMAP.md TREE.md || true
```

---

## 5. Chore Implementation for OCA Submodules/Pins

When updating OCA repos / pin revisions / sync, use a single atomic commit:

**Commit 1:** `chore(oca): bump oca pins (repo list/lock)`

- Edits: `oca.lock.json`, `oca-aggregate.yml`, `.gitmodules` (if needed), `oca/` pointers

**Commit 2 (optional):** `chore(oca): regen docs + pass drift checks`

- Edits: `docs/`, `SITEMAP.md`, `TREE.md` if pipeline expects regeneration

---

## 6. PR Checklist Template

Paste this into every `chore(oca)` PR:

```markdown
### Why
- (reason for OCA maintenance)

### What changed
- oca.lock.json: (pins bumped)
- oca/: (submodule refs updated)
- oca-aggregate.yml: (repos/modules list updated)

### Verification
- [ ] pre-commit run -a
- [ ] python scripts/generate_odoo_dbml.py && git diff --exit-code docs/data-model/
- [ ] (if applicable) python scripts/seed_finance_close_from_xlsx.py && git diff --exit-code addons/ipai_finance_close_seed
- [ ] CI green
```

---

## Minimal Examples

### Example A: OCA Pin Bump

```bash
git checkout -b chore/oca-pin-bump-20260110

# edit oca.lock.json / oca-aggregate.yml / submodule refs as needed

git add oca.lock.json oca-aggregate.yml .gitmodules oca/
git commit -m "chore(oca): bump OCA pins"

# optional regen if it changes outputs
python scripts/generate_odoo_dbml.py
git add docs/data-model/ || true
git commit -m "chore(docs): regen canonical data-model artifacts" || true

git push -u origin chore/oca-pin-bump-20260110
```

### Example B: Repo Hygiene (not OCA)

```bash
git checkout -b chore/repo-hygiene-20260110
# formatting/docs/cleanup
git commit -am "chore(repo): housekeeping (docs/scripts formatting)"
git push -u origin chore/repo-hygiene-20260110
```

---

## Hard Rule

If a chore changes anything that affects deterministic outputs (docs/data-model, seed modules, TREE/SITEMAP), **regen in the same PR** and ensure `git diff --exit-code` passes.

---

*See also: [CONTRIBUTING.md](../CONTRIBUTING.md) | [CLAUDE.md](../CLAUDE.md)*

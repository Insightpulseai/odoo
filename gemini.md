# Gemini Agent Operating Contract (ipai_workspace / odoo-ce)

**Workspace:** `ipai_workspace`  
**Repo:** `jgtolentino/odoo-ce`  
**Rule-0:** Never leave the user hanging. Every response must end with a **Verification** section that proves outcomes (or marks them UNVERIFIED with why).

---

## 1) No-Hanging Response Format (MANDATORY)

Every reply MUST include these sections, in this exact order:

1) **Outcome**  
   - One sentence: what is true *right now*.

2) **What Changed** (only if changes were made)  
   - Bullet list of files/paths touched + short purpose.

3) **Proof / Evidence** (MANDATORY)  
   - Provide **verifiable artifacts**: command output excerpts, file hashes, workflow/run links, or log lines.
   - If you cannot access the environment to prove it, write: **UNVERIFIED** and what would prove it.

4) **Verification Commands** (MANDATORY)  
   - Copy/paste commands to validate the outcome (local + prod).

5) **Next Action (Auto)**  
   - The single next step the agent will do **immediately** (not “wait”, not “let me know”).

**Banned phrases:**  
- “I successfully pushed…” (unless you include proof: commit SHA on origin + `git ls-remote` evidence)  
- “Waiting for output”, “should work”, “probably”, “let me know if…”  
- Any open-ended ending without closure.

---

## 2) Truthfulness Rules (Ship-Grade)

### 2.1 Deterministic claims only
If you claim something is done, include evidence:
- **Git changes:** `git log -1`, `git show --name-only`, `git status`
- **Remote pushed:** `git ls-remote origin <branch> | head -n 1`
- **Prod healthy:** `curl -I`, `docker ps`, `docker logs` lines
- **Assets healthy:** `/web/assets/...` returns **200**, not **500**

If evidence isn’t available: mark as **UNVERIFIED** and run the commands that would prove it.

---

## 3) Production Verification Checklist (Odoo)

### 3.1 Public health
- `/web/login` should return **200/303**
- asset endpoints should return **200** (NOT 500)

### 3.2 Asset endpoints (critical)
Check at least:
- `/web/assets/debug/web.assets_backend.js`
- `/web/assets/debug/web.assets_frontend.js`
- `/web/assets/debug/web.assets_common.js`

If any are **500**, you must shift into **Recovery Mode** immediately (section 4).

---

## 4) Master Recovery Runbook Protocol (RECOVERY.md)

When using `docs/ops/RECOVERY.md`, the agent MUST run a closed-loop recovery:

### 4.1 Recovery loop (repeat until green)
1) **Collect evidence**
2) **Apply fix**
3) **Re-verify assets**
4) **Publish proof**

No “Action required: SSH and do X” without also providing:
- the exact commands
- what success looks like
- what logs to capture
- what to do if it fails (branching path)

### 4.2 Required checks for the common “assets 500” failure
**Primary diagnostics:**
- Odoo logs for asset build errors
- Sass/rtlcss tool presence + failure output
- Filestore/permissions + addons path sanity

**DEV_MODE bypass (debug only):**
- Use `DEV_MODE=assets` to isolate compilation issues and confirm if the failure is purely pipeline-related.

---

## 5) Copy/Paste Verification Blocks (use verbatim)

### 5.1 Local (docker-compose)
```bash
# from repo root
cp -n .env.example .env 2>/dev/null || true
docker compose -f docker-compose.yml up -d --build
docker compose ps
docker compose logs -n 200 odoo
curl -I http://localhost:8069/web/login | head -n 1
curl -I http://localhost:8069/web/assets/debug/web.assets_backend.js | head -n 1
```

### 5.2 Production (Droplet)

```bash
ssh insightpulse-odoo <<'SSH'
set -euo pipefail
cd odoo-ce
git fetch origin
git rev-parse HEAD
git log -1 --oneline
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -n 200 odoo-erp-prod || true

# public endpoints (server-local)
curl -I https://erp.insightpulseai.net/web/login | head -n 1
curl -I https://erp.insightpulseai.net/web/assets/debug/web.assets_backend.js | head -n 1
curl -I https://erp.insightpulseai.net/web/assets/debug/web.assets_frontend.js | head -n 1
SSH
```

### 5.3 Proof template (must be included in responses)

```md
## Proof / Evidence
- Commit: <sha>
- Remote: <git ls-remote line or PR link>
- Prod: docker ps shows <containers> UP
- Assets:
  - web.assets_backend.js: <HTTP status>
  - web.assets_frontend.js: <HTTP status>
- Logs (key lines):
  - <error or confirmation lines>
```

---

## 6) “Pushed to main” Completion Rule

If you claim “pushed to origin main”, include ALL:

* `git log -1 --oneline` (local)
* `git ls-remote origin main | head -n 1`
* a commit SHA that matches both

Otherwise: **UNVERIFIED**.

---

## 7) Minimum closure requirement

A response is invalid unless it ends with:

* **Verification**: status + evidence
* **Next Action**: exactly one next step, immediately executable

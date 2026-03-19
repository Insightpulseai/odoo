# 🔄 GitHub-First Runbook Pattern

**Based on Figma's workflow:** GitHub as source of truth + embedded CI status + innersource defaults

---

## Core Pattern

Every runbook that touches code should end with:

1. **Pull Request** (artifact + link)
2. **GitHub Actions** (artifact + link to CI run)
3. **CI Gates** (pending → pass/fail tracking)

This matches how Figma uses GitHub: PRs as collaboration surface, Actions for automation, embedded CI results for immediate feedback.

---

## What We've Built

### 1. Gates Table (`ops.run_gates`)

Tracks CI/CD checkpoints:

```sql
create table ops.run_gates (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  name text not null,
  status text not null check (status in ('pending','pass','fail','skipped')),
  url text null,
  details jsonb null
);
```

**Purpose:** Show users what CI checks are running and their status inline in the log viewer.

### 2. GitHub-First Runbooks

**Spec Generator** (`kind: spec`):
- Generates spec-kit (constitution, prd, plan, tasks)
- Opens PR with spec files
- Creates gates: "CI: Tests", "CI: Lint"
- User sees pending checks in UI

**Incident Triage** (`kind: incident`):
- Fetches logs from Vercel
- Analyzes errors
- Generates fix PR
- Creates gates: "CI: Tests", "CI: Security Scan"
- User sees checks running in UI

### 3. Always Include Artifacts

Every GitHub runbook writes:

```typescript
// PR link
this.artifacts.push({ 
  kind: "link", 
  title: "Pull Request", 
  value: pr.url 
});

// Actions link
this.artifacts.push({ 
  kind: "link", 
  title: "GitHub Actions", 
  value: pr.actionsUrl || `${pr.url}/checks` 
});
```

**Why:** Users never have to leave the Ops Control Room to see what's happening.

### 4. Gate Creation Pattern

```typescript
await this.createGate(
  "CI: Tests",           // Gate name
  "pending",             // Initial status
  pr.actionsUrl,         // Link to checks
  { pr_number: pr.number } // Additional context
);
```

**Status lifecycle:**
1. `pending` - Check is running
2. `pass` - Check succeeded
3. `fail` - Check failed  
4. `skipped` - Check was not required

---

## UI Integration (LogViewer)

### Display Pattern

```
┌─────────────────────────────────────────────┐
│  Log Stream                                 │
│  ✓ Phase 0: Validate                       │
│  ✓ Phase 1: Preflight                      │
│  ✓ Phase 2: Execute action                 │
│  ✓ PR created                               │
│  ⏳ Waiting for CI checks...               │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  CI Gates                                   │
│  ⏳ CI: Tests              pending           │
│  ⏳ CI: Lint               pending           │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Artifacts                                  │
│  🔗 Pull Request    →  github.com/...       │
│  🔗 GitHub Actions  →  github.com/...       │
└─────────────────────────────────────────────┘
```

**Key features:**
- CI gates update in real-time (via Supabase Realtime)
- Clicking a gate opens the Actions run
- Visual status indicators (⏳ pending, ✓ pass, ✗ fail)

---

## Innersource Pattern

### Reusable Artifacts

Every runbook generates reusable components:

**Spec runbooks:**
```
spec/<slug>/
  constitution.md  # System principles
  prd.md          # Product requirements
  plan.md         # Implementation plan
  tasks.md        # Concrete tasks
```

**Deployment scripts:**
```
scripts/
  healthcheck.ts   # Reusable health checks
  deploy.ts        # Reusable deploy logic
  rollback.ts      # Reusable rollback
```

**Reusable workflows:**
```
.github/workflows/
  ops-control-room.yml  # Triggered by runbooks
  ci.yml               # Standard CI checks
  security.yml         # Security scans
```

**Why:** Teams can reuse these instead of reinventing. Mirrors Figma's "reusable components" approach.

---

## Risk-Based Automation

### Auto-Open for Low-Risk

```typescript
if (risk.level === 'low') {
  // Automatically open PR
  await github_open_pr({...});
  
  // Create gates (pending)
  await this.createGate("CI: Tests", "pending", ...);
  
  // Complete run
  await this.complete("success");
}
```

**Examples:**
- Spec generation (docs only)
- Schema diagram generation
- Health check reports

### Require Approval for High-Risk

```typescript
if (risk.level === 'high' && env === 'prod') {
  // Show warning in UI
  await this.emit("warn", "System", "⚠️ High-risk operation requires manual approval");
  
  // Create approval gate
  await this.createGate("Manual Approval", "pending", null, {
    risk: 'high',
    env: 'prod',
    requires_approval: true
  });
  
  // Don't auto-execute
  // User must click "Run Anyway" in UI
}
```

**Examples:**
- Production deployments
- Database migrations
- Incident fixes touching core services

---

## Security Pattern (Dependabot-inspired)

### Auto-Triage Split

**Low-effort fixes → Auto-PR:**
```typescript
if (fix.confidence === 'high' && fix.scope === 'dependencies') {
  // Auto-open PR for dependency updates
  await github_open_pr({
    title: `chore: update ${dependency} to ${version}`,
    body: `Automated security patch.\nCVE: ${cve}`,
    files: [{ path: 'package.json', content: updated }]
  });
  
  // Gates: security scan + tests
  await this.createGate("CI: Security Scan", "pending", ...);
  await this.createGate("CI: Tests", "pending", ...);
}
```

**High-effort fixes → Manual triage:**
```typescript
if (fix.confidence === 'low' || fix.scope === 'breaking') {
  // Create incident report
  await this.emit("warn", "Security", `Manual triage required: ${issue}`);
  
  // Create gate requiring human review
  await this.createGate("Security Review", "pending", null, {
    severity: 'high',
    requires_manual_review: true
  });
}
```

---

## Implementation Guide

### Step 1: Update Frontend (LogViewer)

Add gates panel to LogViewer:

```typescript
// Subscribe to gates table
const gatesChannel = supabase
  .channel(`run_gates:${runId}`)
  .on(
    "postgres_changes",
    { 
      event: "INSERT", 
      schema: "ops", 
      table: "run_gates", 
      filter: `run_id=eq.${runId}` 
    },
    (payload) => addGate(payload.new)
  )
  .on(
    "postgres_changes",
    { 
      event: "UPDATE", 
      schema: "ops", 
      table: "run_gates", 
      filter: `run_id=eq.${runId}` 
    },
    (payload) => updateGate(payload.new)
  )
  .subscribe();
```

Display gates:

```tsx
<div className="gates-panel">
  <h3>CI Gates</h3>
  {gates.map(gate => (
    <div key={gate.id} className="gate">
      <StatusIcon status={gate.status} />
      <span>{gate.name}</span>
      <span>{gate.status}</span>
      {gate.url && <a href={gate.url}>View →</a>}
    </div>
  ))}
</div>
```

### Step 2: Update GitHub Adapters

Replace stubs with real API calls:

```typescript
async function github_open_pr(args: any) {
  const token = Deno.env.get("GITHUB_TOKEN");
  
  // 1. Create branch
  const ref = await fetch(`https://api.github.com/repos/${args.repo}/git/refs`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github.v3+json"
    },
    body: JSON.stringify({
      ref: `refs/heads/${args.head}`,
      sha: baseSha
    })
  });
  
  // 2. Create commits
  for (const file of args.files) {
    await github_create_or_update_file(args.repo, file.path, file.content, args.head);
  }
  
  // 3. Open PR
  const pr = await fetch(`https://api.github.com/repos/${args.repo}/pulls`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github.v3+json"
    },
    body: JSON.stringify({
      title: args.title,
      body: args.body,
      head: args.head,
      base: args.base
    })
  });
  
  const prData = await pr.json();
  
  return {
    url: prData.html_url,
    number: prData.number,
    head: args.head,
    actionsUrl: `${prData.html_url}/checks`
  };
}
```

### Step 3: Add CI Status Polling (Optional)

For real-time gate updates:

```typescript
// Poll GitHub Actions API for status changes
async function pollCIStatus(prNumber: number, runId: string) {
  const token = Deno.env.get("GITHUB_TOKEN");
  
  const checks = await fetch(
    `https://api.github.com/repos/${repo}/commits/${sha}/check-runs`,
    { headers: { "Authorization": `Bearer ${token}` } }
  );
  
  const data = await checks.json();
  
  for (const check of data.check_runs) {
    // Map GitHub status to our gate status
    const status = check.status === "completed"
      ? (check.conclusion === "success" ? "pass" : "fail")
      : "pending";
    
    // Update gate in database
    await supabase
      .from("ops.run_gates")
      .update({ 
        status,
        updated_at: new Date().toISOString() 
      })
      .eq("run_id", runId)
      .eq("name", `CI: ${check.name}`);
  }
}
```

---

## Testing the Pattern

### Test 1: Spec Generation

```
1. Type: "generate spec for payment processing"
2. Click Run
3. Watch log viewer:
   ✓ Phase 0-4 complete
   ✓ PR created
   ⏳ CI: Tests (pending)
   ⏳ CI: Lint (pending)
4. Check artifacts:
   🔗 Pull Request
   🔗 GitHub Actions
5. Wait for CI (external)
6. Gates update automatically:
   ✓ CI: Tests (pass)
   ✓ CI: Lint (pass)
```

### Test 2: Incident Triage

```
1. Type: "fix error in auth service"
2. Click Run
3. Watch logs:
   ⚠️ Found 10 error entries
   ℹ️ Root cause: Token expiration
   ✓ Fix PR created
   ⏳ CI: Tests (pending)
   ⏳ CI: Security Scan (pending)
4. Gates show pending checks
5. Click "GitHub Actions" artifact
6. Review CI run in GitHub
7. Merge when green
```

---

## Benefits

### 1. GitHub as Source of Truth
- All changes go through PRs
- Full review + approval workflow
- Audit trail in Git history

### 2. Embedded CI Status
- Users see check results inline
- No need to open GitHub separately
- Real-time updates via Supabase Realtime

### 3. Innersource by Default
- Spec-kits are reusable
- Scripts in `scripts/`
- Workflows in `.github/workflows/`
- Teams can copy and adapt

### 4. Security Automation
- Low-risk → auto-PR
- High-risk → manual approval
- Clear risk markers in UI
- Dependabot-like split

---

## Next Steps

1. **Deploy the updated migration**
   - Includes `ops.run_gates` table
   - Already configured for realtime

2. **Update LogViewer component**
   - Add gates panel
   - Subscribe to `ops.run_gates`
   - Display status + links

3. **Replace GitHub adapter stubs**
   - Implement real PR creation
   - Add CI status polling
   - Handle rate limits

4. **Test with real repos**
   - Connect to your GitHub repos
   - Set `GITHUB_TOKEN` in Figma Make secrets
   - Run spec + incident runbooks

5. **Add manual approval UI**
   - For high-risk operations
   - "Run Anyway" button
   - Requires explanation text

---

## Reference

**Inspired by:** [Figma's use of GitHub](https://github.com/customer-stories/figma)

**Key patterns adopted:**
- GitHub as workflow backbone
- PR-first collaboration
- Embedded CI results
- Automation + manual triage split
- Innersource components

**Figma Make docs:** [Add a backend guide](https://help.figma.com/hc/en-us/articles/32640822050199)

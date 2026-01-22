# 🔧 Developer Guide: Adding New Runbook Types

This guide shows you how to extend Ops Control Room with custom runbook types.

---

## Example: Adding a "Backup" Runbook

Let's add a new runbook type that creates database backups.

### Step 1: Add the type to core types

**File:** `/src/core/types.ts`

```typescript
// Add "backup" to the union type
export type RunbookKind = "deploy" | "healthcheck" | "spec" | "incident" | "schema_sync" | "backup";
```

### Step 2: Create the runbook template

**File:** `/src/core/runbooks.ts`

```typescript
function makeBackupPlan(opts: { env: Env }): RunbookPlan {
  return {
    id: `backup_${Date.now()}`,
    kind: "backup",
    title: "Create Database Backup",
    summary: `Create and store a backup of the ${opts.env} database.`,
    inputs: [
      { 
        key: "env", 
        label: "Environment", 
        type: "select", 
        options: ["prod", "staging", "dev"], 
        value: opts.env 
      },
      { 
        key: "target", 
        label: "Storage Target", 
        type: "select", 
        options: ["s3", "gcs", "local"], 
        value: "s3" 
      },
      { 
        key: "retention", 
        label: "Retention (days)", 
        type: "text", 
        value: "30" 
      }
    ],
    risks: opts.env === "prod" 
      ? [{ 
          level: "warn", 
          code: "PROD_BACKUP", 
          message: "Creating a production backup may impact database performance." 
        }]
      : [{ 
          level: "info", 
          code: "SAFE_BACKUP", 
          message: "Backup is read-only and safe to run." 
        }],
    integrations: ["Supabase"]
  };
}

// Add to the makePlan function
export function makePlan(kind: RunbookKind, opts: PlanOptions): RunbookPlan {
  switch (kind) {
    case "deploy": return makeDeployPlan(opts);
    case "healthcheck": return makeHealthcheckPlan(opts);
    case "spec": return makeSpecPlan(opts);
    case "incident": return makeIncidentPlan(opts);
    case "schema_sync": return makeSchemaSyncPlan(opts);
    case "backup": return makeBackupPlan(opts); // NEW
    default: return makeHealthcheckPlan(opts);
  }
}
```

### Step 3: Add parsing logic

**File:** `/src/core/parse.ts`

```typescript
export function planFromPrompt(prompt: string): RunbookPlan {
  const p = prompt.toLowerCase().trim();
  const env = pickEnv(p);

  // ... existing conditions ...

  // NEW: Add backup detection
  if (p.includes("backup") || p.includes("snapshot")) {
    return makePlan("backup", { env });
  }

  // default: healthcheck
  return makePlan("healthcheck", { env });
}
```

### Step 4: Add executor logic (local - optional)

**File:** `/src/core/execute.ts`

```typescript
export async function* executeRunbook(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  // ... existing code ...

  // Kind-specific execution
  if (plan.kind === "deploy") {
    yield* executeDeploy(plan);
  } else if (plan.kind === "healthcheck") {
    yield* executeHealthcheck(plan);
  } else if (plan.kind === "spec") {
    yield* executeSpec(plan);
  } else if (plan.kind === "incident") {
    yield* executeIncident(plan);
  } else if (plan.kind === "schema_sync") {
    yield* executeSchemaSync(plan);
  } else if (plan.kind === "backup") {
    yield* executeBackup(plan); // NEW
  }

  // ... rest of code ...
}

// NEW: Add backup executor
async function* executeBackup(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Supabase",
    message: "Initiating database backup...",
  };

  await new Promise(resolve => setTimeout(resolve, 2000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Supabase",
    message: "Creating snapshot of tables...",
  };

  await new Promise(resolve => setTimeout(resolve, 3000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "Supabase",
    message: "✓ Backup completed (42.3 MB)",
    data: {
      size: "42.3 MB",
      location: "s3://backups/prod-2026-01-03.sql.gz",
      retention: "30 days"
    },
  };
}
```

### Step 5: Add Edge Function executor logic

**File:** `/supabase/functions/ops-executor/index.ts`

```typescript
async runAction() {
  const plan = this.run.plan;

  if (plan.kind === "deploy") {
    await this.executeDeploy();
  } else if (plan.kind === "spec") {
    await this.executeSpec();
  } else if (plan.kind === "incident") {
    await this.executeIncident();
  } else if (plan.kind === "healthcheck") {
    await this.emit("info", "System", "Healthcheck complete (read-only)");
  } else if (plan.kind === "schema_sync") {
    await this.executeSchemaSync();
  } else if (plan.kind === "backup") {
    await this.executeBackup(); // NEW
  }
}

// NEW: Add backup executor method
async executeBackup() {
  await this.emit("info", "Supabase", "Initiating database backup...");
  await this.sleep(2000);

  // Call Supabase Management API to create backup
  const backupResult = await supabase_create_backup(this.run.env);
  
  await this.emit("success", "Supabase", "✓ Backup completed", backupResult);
  
  this.artifacts.push({
    kind: "link",
    title: "Backup File",
    value: backupResult.url,
  });
}
```

### Step 6: Implement the adapter

**File:** `/supabase/functions/ops-executor/index.ts` (bottom)

```typescript
// NEW: Backup adapter
async function supabase_create_backup(env: string) {
  // TODO: Call Supabase Management API
  // https://supabase.com/docs/reference/api/management-api
  
  // Stub for now
  return {
    url: "https://s3.amazonaws.com/backups/prod-backup.sql.gz",
    size: "42.3 MB",
    timestamp: new Date().toISOString(),
  };
}
```

### Step 7: Update database schema (if needed)

**File:** `/supabase/schema.sql`

```sql
-- If you added "backup" to the kind enum, update the check constraint:
alter table ops.runs 
  drop constraint if exists runs_kind_check;

alter table ops.runs 
  add constraint runs_kind_check 
  check (kind in ('deploy','healthcheck','spec','incident','schema_sync','backup'));
```

### Step 8: Test it!

```bash
# Start dev server
pnpm run dev

# Try the command
> backup prod database
```

You should see:
1. A runbook card with "Create Database Backup" title
2. Inputs for env, storage target, retention
3. Risk warning if prod
4. Run button that triggers execution
5. Log viewer with backup progress

---

## Advanced: Adding Custom Input Types

### Example: Date picker input

**File:** `/src/core/types.ts`

```typescript
export type RunbookInputField =
  | { key: "env"; label: "Environment"; type: "select"; options: Env[]; value?: Env }
  | { key: string; label: string; type: "text"; value?: string }
  | { key: string; label: string; type: "boolean"; value?: boolean }
  | { key: string; label: string; type: "date"; value?: string }; // NEW
```

**File:** `/src/app/components/RunbookCard.tsx`

Update the rendering logic to handle date inputs:

```typescript
{input.type === "date" ? (
  <input
    type="date"
    value={input.value || ""}
    className="..."
  />
) : input.type === "text" ? (
  // ... existing text input
) : null}
```

---

## Advanced: Adding Custom Integrations

### Example: Slack integration

**1. Add to types:**

```typescript
export type Integration = 
  | "Supabase" 
  | "Vercel" 
  | "GitHub" 
  | "DigitalOcean" 
  | "Kubernetes"
  | "Slack"; // NEW
```

**2. Add runbook that uses it:**

```typescript
function makeNotifyPlan(opts: { env: Env }): RunbookPlan {
  return {
    id: `notify_${Date.now()}`,
    kind: "notify",
    title: "Send Slack Notification",
    summary: "Post a message to Slack channel",
    inputs: [
      { key: "channel", label: "Channel", type: "text", value: "#ops" },
      { key: "message", label: "Message", type: "text", value: "Deployment complete!" }
    ],
    risks: [{ level: "info", code: "NOTIFICATION", message: "Posts to Slack only" }],
    integrations: ["Slack"]
  };
}
```

**3. Add executor:**

```typescript
async executeNotify() {
  const channel = this.run.plan.inputs.find((i: any) => i.key === "channel")?.value;
  const message = this.run.plan.inputs.find((i: any) => i.key === "message")?.value;
  
  await this.emit("info", "Slack", `Posting to ${channel}...`);
  
  const result = await slack_post_message(channel, message);
  
  await this.emit("success", "Slack", "✓ Message posted", result);
}
```

**4. Add adapter:**

```typescript
async function slack_post_message(channel: string, message: string) {
  const token = Deno.env.get("SLACK_TOKEN");
  
  const response = await fetch("https://slack.com/api/chat.postMessage", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ channel, text: message }),
  });
  
  return await response.json();
}
```

**5. Set secret:**

```bash
supabase secrets set SLACK_TOKEN=xoxb-your-token
```

---

## Testing Strategy

### 1. Unit Tests (Local Executor)

```typescript
// tests/runbooks.test.ts
import { makePlan } from "../src/core/runbooks";

test("backup plan has correct structure", () => {
  const plan = makePlan("backup", { env: "prod" });
  
  expect(plan.kind).toBe("backup");
  expect(plan.integrations).toContain("Supabase");
  expect(plan.risks[0].level).toBe("warn");
});
```

### 2. Integration Tests (Edge Function)

```typescript
// Test Edge Function locally
Deno.test("backup executor writes events", async () => {
  const executor = new RunbookExecutor(supabase, mockBackupRun);
  await executor.execute();
  
  // Verify events were written
  const { data: events } = await supabase
    .from("ops.run_events")
    .select("*")
    .eq("run_id", mockBackupRun.id);
  
  expect(events.length).toBeGreaterThan(0);
});
```

### 3. E2E Tests (UI)

```typescript
// tests/e2e/backup.spec.ts
test("backup runbook creates card and executes", async ({ page }) => {
  await page.goto("http://localhost:5173");
  
  await page.fill("input[placeholder='Type a command...']", "backup prod");
  await page.keyboard.press("Enter");
  
  // Wait for runbook card
  await page.waitForSelector("text=Create Database Backup");
  
  // Click Run
  await page.click("button:has-text('Run')");
  
  // Wait for log viewer
  await page.waitForSelector("text=Execution Log");
  
  // Verify events appear
  await page.waitForSelector("text=Backup completed");
});
```

---

## Best Practices

### 1. Runbook Design
- ✅ Keep runbooks focused (single responsibility)
- ✅ Add clear risk warnings
- ✅ Provide sensible defaults
- ✅ Make inputs self-documenting
- ❌ Don't create runbooks that require manual intervention

### 2. Executor Implementation
- ✅ Use phases (validate → preflight → action → verify → summarize)
- ✅ Emit frequent progress events
- ✅ Handle errors gracefully
- ✅ Add retry logic for transient failures
- ❌ Don't block for long periods without emitting events

### 3. Adapter Implementation
- ✅ Use environment variables for secrets
- ✅ Add timeouts to API calls
- ✅ Return structured data
- ✅ Log errors with context
- ❌ Don't hard-code credentials

### 4. Testing
- ✅ Test parsing logic (input → plan)
- ✅ Test executor phases
- ✅ Test adapter error handling
- ✅ Test UI rendering
- ❌ Don't skip edge cases (empty inputs, API failures)

---

## Checklist for New Runbook Types

- [ ] Add type to `RunbookKind` union
- [ ] Create plan template in `runbooks.ts`
- [ ] Add parsing logic in `parse.ts`
- [ ] Implement local executor (optional, for demo)
- [ ] Implement Edge Function executor
- [ ] Implement required adapters
- [ ] Update database schema if needed
- [ ] Set required secrets
- [ ] Write tests
- [ ] Update documentation

---

## Examples in the Wild

Check existing runbook types for reference:

- **deploy** - Complex multi-phase workflow
- **healthcheck** - Read-only checks
- **spec** - File generation + PR
- **incident** - Log analysis + fix proposal
- **schema_sync** - Comparison + diff generation

---

## Need Help?

- **Ask in discussions:** Share your use case
- **Check existing code:** See how other runbooks work
- **Read adapter docs:** External API documentation

Happy coding! 🚀

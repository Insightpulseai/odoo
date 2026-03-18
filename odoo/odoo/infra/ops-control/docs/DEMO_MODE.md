# Demo Mode (No Supabase Required)

If you want to test the UI without setting up Supabase first, you can run in **demo mode** which uses the local in-memory executor.

## Steps

1. Create a `.env` file with dummy values (or none):

```env
# These can be fake values for demo mode
VITE_SUPABASE_URL=https://demo.supabase.co
VITE_SUPABASE_ANON_KEY=demo-key
```

2. Temporarily modify `/src/app/App.tsx` to use the local executor:

```typescript
// At the top of App.tsx, add this import
import { executeRunbook as localExecuteRunbook } from "../core/execute";

// Replace the handleRunPlan function with this demo version:
const handleRunPlan = async (plan: RunbookPlan) => {
  setCurrentPlanTitle(plan.title);
  setCurrentEvents([]);
  setCurrentArtifacts([]);
  setShowLogViewer(true);

  // Use local executor instead of Supabase
  try {
    for await (const event of localExecuteRunbook(plan)) {
      setCurrentEvents(prev => [...prev, event]);
    }
    toast.success('Runbook completed successfully');
  } catch (error) {
    console.error("Execution error:", error);
    toast.error('Runbook execution failed');
  }
};
```

3. Start the dev server:

```bash
pnpm run dev
```

4. Try commands:
   - "deploy prod"
   - "check staging status"
   - "generate spec for dashboard"
   - "fix production error"

The UI will show simulated execution with streaming logs, but no data is saved to a database.

---

## Switching to Production Mode

When you're ready to use Supabase:

1. Follow [SETUP.md](../SETUP.md) to set up Supabase
2. Revert the `App.tsx` changes (use the Supabase version)
3. Update `.env` with real Supabase credentials
4. Deploy the Edge Function executor

Now your runbooks will be queued, executed server-side, and logged to the database with real-time streaming!

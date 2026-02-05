# Final Working Structure

This is the **standalone web demo** version. The monorepo structure in `/packages` and `/apps` is preserved for reference, but the working app uses local imports.

## 🎯 Current Structure (Working)

```
/src
├── core/                      # Business logic
│   ├── types.ts               # RunbookPlan, RunEvent, etc.
│   ├── parse.ts               # planFromPrompt()
│   ├── runbooks.ts            # makePlan()
│   ├── execute.ts             # executeRunbook()
│   └── index.ts               # Re-exports
└── app/
    ├── components/
    │   ├── AppShell.tsx       # Header + status
    │   ├── CommandBar.tsx     # Input + quick commands
    │   ├── RunbookCard.tsx    # Inline runbook card
    │   ├── LogViewer.tsx      # Fullscreen log viewer
    │   └── ui/                # shadcn components
    └── App.tsx                # Main app (uses ../core imports)
```

## ✅ What Works

- **Natural language parsing**: `"Deploy prod"` → `RunbookPlan`
- **5 runbook types**: deploy, healthcheck, spec, incident, schema_sync
- **Risk assessment**: Automatic risk flags per runbook + environment
- **Mock execution**: Realistic streaming execution with delays
- **Fullscreen logs**: Stats, filtering, export to .txt
- **Inline cards**: Inputs, risks, integrations, Run/Edit actions

## 🚀 Try It Now

Type these commands:
- `Deploy prod`
- `Check prod status`
- `Generate spec for dashboard`
- `Fix production error`
- `Run schema sync`

## 📦 Monorepo Structure (Reference)

The `/packages` and `/apps` directories contain the **production monorepo structure** for when you want to:
1. Deploy as a ChatGPT App (MCP server in `/apps/mcp-server`)
2. Share code between web demo and ChatGPT widget
3. Wire real integrations (Vercel, Supabase, GitHub examples included)

**To use the monorepo:**
1. Copy `/packages` and `/apps` to a separate repo
2. Run `pnpm install` from root
3. Build MCP server: `cd apps/mcp-server && pnpm build`
4. Deploy to Railway/Fly.io/Vercel
5. Connect to ChatGPT

## 📚 Documentation Files

- `/README.md` — Full architecture overview
- `/QUICKSTART.md` — 2-minute demo → 10-minute deploy guide
- `/COMMANDS.md` — All natural language commands
- `/apps/mcp-server/README.md` — Deployment guide
- Integration examples:
  - `/apps/mcp-server/src/integrations/vercel.example.ts`
  - `/apps/mcp-server/src/integrations/supabase.example.ts`
  - `/apps/mcp-server/src/integrations/github.example.ts`

## 🔧 How to Extend

### Add a new runbook type:

1. **Update types** (`/src/core/types.ts`):
   ```ts
   export type RunbookKind = "deploy" | ... | "your_new_type";
   ```

2. **Add parser rule** (`/src/core/parse.ts`):
   ```ts
   if (p.includes("your_keyword")) return makePlan("your_new_type", { env });
   ```

3. **Define runbook** (`/src/core/runbooks.ts`):
   ```ts
   if (kind === "your_new_type") {
     return { ...base, title: "...", inputs: [...], ... };
   }
   ```

4. **Add execution** (`/src/core/execute.ts`):
   ```ts
   async function* executeYourType(plan: RunbookPlan) {
     yield { ts: "...", level: "info", source: "System", message: "..." };
   }
   ```

### Wire real integrations:

Replace mock execution in `/src/core/execute.ts` with real API calls.

See examples in `/apps/mcp-server/src/integrations/`:
- `vercel.example.ts` — Real Vercel deployments
- `supabase.example.ts` — Health checks + migrations
- `github.example.ts` — PR creation + Actions

## 🎨 UI Customization

All components use Tailwind CSS. Key classes:
- Risk levels: `bg-blue-50` (info), `bg-amber-50` (warn), `bg-red-50` (block)
- Integration badges: `bg-black` (Vercel), `bg-emerald-600` (Supabase), etc.
- Status indicators: `bg-green-500` (operational), `bg-amber-500` (degraded)

## 🐛 Known Limitations

1. **Edit mode**: Currently just shows a message. In production, would open a modal with form inputs.
2. **Mock execution**: All integrations are mocked. Wire real APIs per examples.
3. **No persistence**: Runbook history isn't saved. Add localStorage/DB as needed.
4. **No authentication**: No API keys, user auth, or approval workflows.

## 🎓 Next Steps

1. **Wire real integrations** (Vercel, Supabase, GitHub)
2. **Add input editing modal** (replace mock Edit action)
3. **Add runbook history** (localStorage or database)
4. **Deploy MCP server** (for ChatGPT integration)
5. **Add authentication** (API keys or OAuth)
6. **Add approval workflows** (for high-risk runbooks)

---

**Everything works!** Type a command and watch the magic happen. 🚀

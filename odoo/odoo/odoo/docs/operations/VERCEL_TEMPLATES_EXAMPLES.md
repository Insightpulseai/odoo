# Vercel Templates & Examples — Adoption Contract

> How we evaluate, adopt, and govern Vercel official templates and examples
> in the ops-console and any future Vercel-hosted app in this monorepo.

---

## What Vercel templates are

Vercel templates (`vercel.com/templates`) are starter apps that encode Vercel platform best practices:
- Framework integration (Next.js, Remix, SvelteKit, etc.)
- Edge/middleware patterns
- Incremental Static Regeneration (ISR) and caching strategies
- Authentication patterns (Clerk, NextAuth, Supabase Auth)
- Database integrations (Supabase, Planetscale, Neon, Upstash)
- AI / streaming patterns (Vercel AI SDK)

Templates are **reference implementations** — we harvest specific patterns, not fork entire repos.

---

## Adoption rules

### Do: harvest minimal slices

| Pattern | What to copy | What to skip |
|---------|-------------|--------------|
| Auth flow | `middleware.ts`, `lib/supabase/server.ts`, `app/(auth)/` routes | Full template repo, unrelated pages |
| Streaming AI response | `app/api/chat/route.ts`, `components/stream-output.tsx` | Template UI theme, global styles |
| ISR page | `revalidate` export, `generateStaticParams` | Template navigation, layout |
| Supabase Storage upload | `lib/storage.ts`, upload route | Everything else |

### Do not: fork templates wholesale

Forking an entire Vercel template into ops-console creates:
- Dependency drift between template updates and our customizations
- Conflicting global styles and component hierarchies
- Unclear ownership of template-originated files

### Do not: introduce new framework dependencies via templates

If a template uses a library we don't have (e.g., `@clerk/nextjs`), evaluate that library
separately via a PR. Don't slip it in via template adoption.

---

## Current adopted patterns

| Pattern | Source template | Where we use it | Adopted date |
|---------|----------------|-----------------|--------------|
| Supabase SSR session | `nextjs-with-supabase` | `middleware.ts`, `lib/supabase/` | 2026-02 |
| Skip-unaffected builds | Vercel monorepo guide | `apps/ops-console/vercel.json` | 2026-02 |
| Streaming markdown | `ai-sdk` template | `components/MarkdownStream.tsx` | 2026-02 |

---

## How to propose a new pattern adoption

1. Open a PR with: `docs(ops): adopt <pattern-name> from <template-slug>`
2. Reference the template URL in the PR description
3. Include only the minimal slice in the diff — nothing else from the template
4. Update the "Current adopted patterns" table above
5. Verify the pattern works: `pnpm --filter odooops-console build`

---

## Vercel Examples (GitHub)

`vercel/next.js` and `vercel/examples` repos contain smaller, focused examples.
These are preferred over large templates for targeted pattern adoption.

Useful examples for ops-console:

| Example | Pattern |
|---------|---------|
| `with-supabase` | Supabase Auth + server components |
| `ai-chatbot` | Streaming AI responses + persistence |
| `middleware-auth` | Edge middleware session guard |
| `edge-config` | Feature flags via Edge Config |
| `with-opentelemetry` | OTel + Vercel observability |

---

## Template vs. example vs. scaffold

| Term | Definition | Governed by |
|------|------------|-------------|
| **Template** | Full starter app on vercel.com/templates | This doc (harvest patterns only) |
| **Example** | Focused pattern in vercel/examples repo | This doc (harvest patterns only) |
| **Scaffold** | Placeholder page we created (e.g., `/platform`, `/metrics`) | See page source comments |
| **Component** | shadcn/ui or Supabase UI component | See `SUPABASE_EXAMPLES_UI_ADOPTION.md` |

---

## Related

| File | Purpose |
|------|---------|
| `docs/ops/VERCEL_MONOREPO.md` | ops-console Vercel project configuration |
| `docs/ops/SUPABASE_VERCEL.md` | Supabase↔Vercel env var sync |
| `docs/ops/SUPABASE_EXAMPLES_UI_ADOPTION.md` | Supabase UI and examples governance |
| `docs/platform/GOLDEN_PATH.md` | Monorepo release gates and boundaries |

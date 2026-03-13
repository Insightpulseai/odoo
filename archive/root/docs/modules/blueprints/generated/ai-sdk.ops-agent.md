<!-- AUTO-GENERATED from blueprints/ai-sdk.ops-agent.blueprint.yaml — do not edit directly -->
<!-- Run: python3 scripts/catalog/build_blueprints.py -->

# Blueprint: AI SDK Ops Agent (Vercel AI SDK + streaming tools + Supabase persistence)

**ID**: `ai-sdk.ops-agent`  
**Category**: `ai-ops-agent`  
**Target**: `apps/ops-console`

---

## Sources

- **vercel-example** — [https://github.com/vercel/ai-chatbot](https://github.com/vercel/ai-chatbot) (catalog id: `ai-chatbot`)
- **vercel-template** — [https://vercel.com/templates/next.js/ai-sdk-internal-tool](https://vercel.com/templates/next.js/ai-sdk-internal-tool) (catalog id: `ai-sdk-internal-tools`)

---

## Required Variables

**Required**:

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_BASE_URL` | Vercel AI Gateway URL | `https://ai-gateway.vercel.sh` |
| `ANTHROPIC_AUTH_TOKEN` | Vercel AI Gateway API key (server-only) | `sk-ant-...` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL for chat persistence | `https://spdtwktxdalcfigzeqrz.supabase.co` |

**Optional**:

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Leave empty — gateway authenticates | `` |

---

## Automation Steps

### Step 1: add_chat_route

Add streaming chat API route with tool support

**Agent instruction**:

```
Create apps/ops-console/app/api/ai/chat/route.ts:
- Use streamText from ai package
- Use Anthropic provider (anthropic('claude-sonnet-4-6'))
- Include maxSteps: 5 for multi-step tool loops
- Define at least 2 tools using zod schema:
  * getDropletStatus: calls /api/observability/do/droplets
  * querySupabaseLogs: calls /api/supabase-proxy/v1/projects/.../analytics/...
- Wire ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN from env (not ANTHROPIC_API_KEY)
- Return StreamingTextResponse or toDataStreamResponse()
```

### Step 2: add_chat_page

Add /ai route with chat UI

**Agent instruction**:

```
Create apps/ops-console/app/ai/page.tsx as a client component.
Use the useChat hook from ai/react.
Display messages with streaming markdown (MarkdownStream component if available,
or simple prose div otherwise).
Show tool invocation results in a collapsible detail block.
Add a text input with submit button.
No authentication bypass — use existing session from middleware.
```

### Step 3: add_persistence

Add Supabase chat history persistence

**Agent instruction**:

```
Create a server action or API route to:
- Save chat messages to a Supabase table (chat_sessions + chat_messages)
- Table schema: id (uuid), session_id (uuid), role (user|assistant), content (text), created_at
- Only store messages after successful response (not during stream)
- RLS: user can only read their own messages (auth.uid() = user_id)
Do not create the table via ad-hoc SQL — create a migration:
supabase migration new add_chat_history
```

---

## Verification

**Required CI checks:**

- `ops-console-check`
- `golden-path-summary`

**Preview expectations:**

- chat-route-returns-200-with-streaming-headers
- tool-invocation-visible-in-response
- messages-persisted-to-supabase

---

## Rollback

**Strategy**: `revert_pr`

Chat history table migration must be reverted separately via supabase db reset on DEV branch.

---

## Minor Customization (manual steps after agent applies blueprint)

- Set ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN in Vercel project env vars (server-only, no NEXT_PUBLIC_)
- Create DEV branch in Supabase before running migration (supabase branches create dev-ai-chat)
- Merge DEV branch after testing (supabase branches merge)

---

## Agent Relay Template

Paste this prompt to apply this blueprint:

```text
Apply blueprint `ai-sdk.ops-agent` from docs/catalog/blueprints/ai-sdk.ops-agent.blueprint.yaml.

Variables to set before running:
  ANTHROPIC_BASE_URL: <value>
  ANTHROPIC_AUTH_TOKEN: <value>
  NEXT_PUBLIC_SUPABASE_URL: <value>

Steps to execute in order:
  1. add_chat_route: Add streaming chat API route with tool support
  2. add_chat_page: Add /ai route with chat UI
  3. add_persistence: Add Supabase chat history persistence

After completing all steps:
  - Verify required checks pass: ops-console-check, golden-path-summary
  - Complete minor_customization items (see blueprint notes)
  - Open PR with title: feat({category}): apply {bp_id} blueprint
```

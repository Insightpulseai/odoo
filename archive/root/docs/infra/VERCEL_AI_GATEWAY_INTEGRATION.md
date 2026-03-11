# Vercel AI Gateway Integration Strategy

**Purpose**: Leverage Vercel AI Gateway for unified AI model access across MCP Jobs, infrastructure discovery, and observability systems

**Last Updated**: 2026-01-20
**Status**: Planning Phase

---

## Overview

Vercel AI Gateway provides a centralized API layer for accessing multiple AI models through a single, unified interface. This eliminates the need to manage separate API keys and SDKs for each provider.

**Key Benefits**:
- **Unified API endpoint** - One consistent surface for all supported AI models
- **Multi-provider support** - Route requests to OpenAI, Anthropic, xAI/Grok, Claude, etc.
- **Automatic key management** - Vercel handles provider authentication
- **Failover and load balancing** - Automatic fallback when providers are down
- **OpenAI-Compatible API** - Works with existing tooling and client libraries

---

## Current AI Usage Across Stack

### 1. MCP Jobs System
**Current State**: Manual job processing with custom workers
**AI Opportunities**:
- Job classification and routing (which worker should handle this job?)
- Failure analysis (why did this job fail? suggest fixes)
- Dead letter queue triage (which failures are worth retrying?)
- Job payload validation (is this job definition correct?)

### 2. Infrastructure Discovery
**Current State**: 5 discovery scripts generating JSON knowledge graph
**AI Opportunities**:
- Semantic relationship extraction (find implicit dependencies)
- Anomaly detection (unusual infrastructure patterns)
- Documentation generation (LLM-facing memory docs)
- Query optimization (natural language → graph queries)

### 3. Observability & Monitoring
**Current State**: Manual log analysis, metric aggregation
**AI Opportunities**:
- Log summarization (reduce 10K lines → actionable insights)
- Incident prediction (detect patterns before failures)
- Alert triage (which alerts require immediate action?)
- Root cause analysis (correlate events across services)

---

## AI Gateway Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vercel AI Gateway                             │
│  https://ai-gateway.vercel.sh/v1 (OpenAI-compatible endpoint)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Provider Pool (automatic failover + load balancing):           │
│  ├── OpenAI (GPT-4o, GPT-4o-mini)                              │
│  ├── Anthropic (Claude Sonnet 4.5, Claude Haiku)               │
│  ├── xAI (Grok-3)                                               │
│  ├── Groq (fast Llama inference)                               │
│  └── [Other providers via integration marketplace]             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            ▲
                            │ Unified API calls
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐   ┌────────▼────────┐   ┌─────▼─────────┐
│ MCP Jobs     │   │ Discovery       │   │ Observability │
│ Workers      │   │ Scripts         │   │ Functions     │
│              │   │                 │   │               │
│ - Job triage │   │ - Relationship  │   │ - Log summary │
│ - Failure    │   │   extraction    │   │ - Incident    │
│   analysis   │   │ - Doc gen       │   │   prediction  │
└──────────────┘   └─────────────────┘   └───────────────┘
```

---

## Integration Points

### 1. MCP Jobs: AI-Powered Job Orchestration

**Use Cases**:

#### A. Intelligent Job Routing
```typescript
// lib/ai/jobRouter.ts
import { generateText } from 'ai'

export async function classifyJobType(payload: unknown): Promise<JobType> {
  const result = await generateText({
    model: 'openai/gpt-4o-mini',  // Fast, cheap classification
    prompt: `Classify this job payload into one of: discovery, sync, report, bir_filing, month_end_close

    Payload: ${JSON.stringify(payload, null, 2)}

    Return only the job type, no explanation.`
  })

  return result.text.trim() as JobType
}
```

#### B. Failure Analysis & Auto-Retry Decision
```typescript
// lib/ai/failureAnalysis.ts
export async function analyzeJobFailure(
  job: Job,
  error: string,
  retryCount: number
): Promise<{ shouldRetry: boolean; reason: string; suggestedFix?: string }> {
  const result = await generateObject({
    model: 'anthropic/claude-sonnet-4.5',  // Better reasoning for complex errors
    schema: z.object({
      shouldRetry: z.boolean(),
      reason: z.string(),
      suggestedFix: z.string().optional()
    }),
    prompt: `Analyze this job failure and determine if retry is worthwhile:

    Job Type: ${job.job_type}
    Retry Count: ${retryCount} / ${job.max_retries}
    Error: ${error}
    Last Run Stack: ${job.error_stack}

    Consider:
    - Is this a transient error (network, timeout) or permanent (validation, logic)?
    - Will retrying likely succeed or just waste resources?
    - Can you suggest a fix for the payload or configuration?`
  })

  return result.object
}
```

#### C. Dead Letter Queue Triage
```typescript
// Edge Function: supabase/functions/dlq-triage/index.ts
export async function triageDeadLetterQueue(): Promise<DLQTriageReport> {
  const dlqItems = await supabaseJobs
    .from('dead_letter_queue')
    .select('*')
    .eq('resolved', false)
    .order('created_at', { ascending: false })
    .limit(50)

  const result = await generateObject({
    model: 'xai/grok-3',  // Multi-model comparison for critical decisions
    schema: DLQTriageSchema,
    prompt: `Analyze these failed jobs and prioritize triage:

    ${JSON.stringify(dlqItems.data, null, 2)}

    For each job, determine:
    1. Severity (critical, high, medium, low)
    2. Root cause category (infra, code, data, external)
    3. Recommended action (manual_fix, redeploy, ignore)
    4. Priority score (1-10)

    Return sorted by priority (highest first).`
  })

  return result.object
}
```

---

### 2. Discovery Scripts: AI-Enhanced Knowledge Graph

**Use Cases**:

#### A. Semantic Relationship Extraction
```python
# scripts/discover_vercel_infra.py (enhanced)
import openai  # OpenAI-compatible client

# Point to AI Gateway instead of api.openai.com
client = openai.OpenAI(
    base_url="https://ai-gateway.vercel.sh/v1",
    api_key=os.getenv("VERCEL_GATEWAY_TOKEN")
)

def extract_implicit_dependencies(nodes: list, edges: list) -> list:
    """Use LLM to find dependencies not explicit in API responses."""
    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.5",
        messages=[{
            "role": "user",
            "content": f"""Given this infrastructure graph, identify implicit dependencies:

            Nodes: {json.dumps(nodes[:100], indent=2)}
            Edges: {json.dumps(edges[:50], indent=2)}

            Find relationships like:
            - "Project X uses Integration Y" (even if not explicitly linked)
            - "Service A depends on Database B" (inferred from env vars)
            - "Function F calls API G" (detected from code patterns)

            Return JSON array of new edges: [{{"from_id": "...", "to_id": "...", "type": "...", "confidence": 0.0-1.0}}]
            """
        }]
    )

    return json.loads(response.choices[0].message.content)
```

#### B. LLM-Facing Documentation Generation
```python
# scripts/generate_llm_docs.py (enhanced with AI Gateway)
def generate_narrative_docs(graph_data: dict) -> str:
    """Convert graph JSON into prose documentation for LLM context."""
    response = client.chat.completions.create(
        model="openai/gpt-4o",  # Good at structured → narrative conversion
        messages=[{
            "role": "system",
            "content": "You are a technical writer creating documentation for AI agents."
        }, {
            "role": "user",
            "content": f"""Convert this infrastructure graph into clear, concise documentation:

            {json.dumps(graph_data, indent=2)}

            Format as markdown with sections:
            - Overview (2-3 sentences)
            - Key Components (bullet list)
            - Dependencies (network diagram in mermaid)
            - Critical Paths (what relies on what)
            """
        }]
    )

    return response.choices[0].message.content
```

---

### 3. Observability: AI-Powered Monitoring

**Use Cases**:

#### A. Intelligent Log Summarization
```typescript
// Edge Function: supabase/functions/log-summary/index.ts
export async function summarizeLogs(
  source: string,
  timeRange: { start: Date; end: Date }
): Promise<LogSummary> {
  // Fetch logs from Supabase
  const logs = await supabase
    .from('job_events')
    .select('*')
    .eq('source', source)
    .gte('created_at', timeRange.start.toISOString())
    .lte('created_at', timeRange.end.toISOString())

  // Use AI Gateway to summarize
  const result = await generateObject({
    model: 'groq/llama-3.1-70b',  // Fast, cost-effective summarization
    schema: LogSummarySchema,
    prompt: `Summarize these ${logs.data.length} log events:

    ${JSON.stringify(logs.data, null, 2)}

    Provide:
    - High-level summary (2-3 sentences)
    - Error patterns (group similar errors)
    - Performance trends (timing anomalies)
    - Recommended actions (what to investigate)
    `
  })

  return result.object
}
```

#### B. Incident Prediction
```typescript
// Scheduled job: predict incidents before they happen
export async function predictIncidents(): Promise<IncidentPrediction[]> {
  // Get recent metrics and events
  const metrics = await supabase.from('metrics').select('*').order('created_at', { ascending: false }).limit(1000)
  const events = await supabase.from('job_events').select('*').order('created_at', { ascending: false }).limit(500)

  const result = await generateObject({
    model: 'anthropic/claude-sonnet-4.5',  // Strong pattern recognition
    schema: IncidentPredictionSchema,
    prompt: `Analyze these metrics and events for incident patterns:

    Metrics: ${JSON.stringify(metrics.data)}
    Events: ${JSON.stringify(events.data)}

    Identify:
    1. Degrading trends (error rates increasing, latency climbing)
    2. Anomalous patterns (unusual job failures, queue depth growth)
    3. Correlated events (multiple services failing together)
    4. Time-to-incident estimate (how soon will this become critical?)

    Return predictions sorted by urgency.`
  })

  return result.object.predictions
}
```

---

## Implementation Plan

### Phase 1: AI Gateway Setup (Week 1)

**Prerequisites**:
- [ ] Access Vercel AI dashboard: https://vercel.com/tbwa/~/ai
- [ ] Enable AI Gateway for mcp-jobs project
- [ ] Generate gateway API key or configure OIDC token
- [ ] Add `VERCEL_GATEWAY_TOKEN` to Vercel environment variables

**Tasks**:
1. Install Vercel AI SDK in mcp-jobs:
   ```bash
   cd mcp/servers/mcp-jobs
   pnpm add ai @ai-sdk/openai @ai-sdk/anthropic
   ```

2. Configure AI Gateway client:
   ```typescript
   // lib/ai/gateway.ts
   import { openai } from '@ai-sdk/openai'
   import { anthropic } from '@ai-sdk/anthropic'

   export const ai = {
     openai: openai.provider({
       baseURL: 'https://ai-gateway.vercel.sh/v1'
     }),
     anthropic: anthropic.provider({
       baseURL: 'https://ai-gateway.vercel.sh/v1'
     })
   }
   ```

3. Test unified model access:
   ```typescript
   // Test all providers work through gateway
   const models = [
     'openai/gpt-4o-mini',
     'anthropic/claude-sonnet-4.5',
     'xai/grok-3',
     'groq/llama-3.1-70b'
   ]

   for (const model of models) {
     const result = await generateText({
       model,
       prompt: 'Return "OK" if you can read this.'
     })
     console.log(`${model}: ${result.text}`)
   }
   ```

---

### Phase 2: MCP Jobs AI Integration (Week 2)

**Tasks**:
1. Implement job classification endpoint:
   ```typescript
   // app/api/jobs/classify/route.ts
   export async function POST(req: Request) {
     const { payload } = await req.json()
     const jobType = await classifyJobType(payload)
     return NextResponse.json({ jobType })
   }
   ```

2. Add failure analysis to `fail_job()` function:
   ```sql
   -- Update mcp_jobs.fail_job() to call Edge Function for analysis
   CREATE OR REPLACE FUNCTION mcp_jobs.fail_job_with_ai(
     p_job_id UUID,
     p_error TEXT,
     p_error_stack TEXT DEFAULT NULL
   ) RETURNS JSONB
   ```

3. Create DLQ triage Edge Function:
   ```bash
   supabase functions new dlq-triage
   # Implement AI-powered triage logic
   supabase functions deploy dlq-triage
   ```

4. Schedule daily DLQ analysis:
   ```sql
   -- Supabase Cron job
   SELECT cron.schedule(
     'dlq-triage-daily',
     '0 8 * * *',  -- 8 AM daily
     $$
     SELECT net.http_post(
       url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/dlq-triage',
       headers := jsonb_build_object('Authorization', 'Bearer ' || current_setting('supabase.service_role_key'))
     );
     $$
   );
   ```

---

### Phase 3: Discovery Script AI Enhancement (Week 3)

**Tasks**:
1. Update all 5 discovery scripts to use AI Gateway:
   - `discover_vercel_infra.py`
   - `discover_supabase_infra.py`
   - `discover_odoo_infra.py`
   - `discover_digitalocean_infra.sh` (via Python wrapper)
   - `discover_docker_infra.sh` (via Python wrapper)

2. Add semantic relationship extraction:
   ```python
   # Add to each discovery script
   implicit_edges = extract_implicit_dependencies(nodes, edges)
   edges.extend(implicit_edges)
   ```

3. Generate LLM-facing docs with AI:
   ```python
   # Replace static template with AI-generated narrative
   narrative_docs = generate_narrative_docs(graph_data)
   ```

4. Create validation Edge Function:
   ```typescript
   // Validate AI-generated relationships before adding to graph
   export async function validateRelationships(edges: Edge[]): Promise<Edge[]>
   ```

---

### Phase 4: Observability AI Features (Week 4)

**Tasks**:
1. Implement log summarization:
   ```bash
   supabase functions new log-summary
   supabase functions deploy log-summary
   ```

2. Add incident prediction:
   ```bash
   supabase functions new incident-predict
   supabase functions deploy incident-predict
   ```

3. Create Slack alerting integration:
   ```typescript
   // When DLQ triage or incident prediction returns high-priority items
   await fetch(process.env.SLACK_WEBHOOK_URL, {
     method: 'POST',
     body: JSON.stringify({
       text: `🚨 High-priority incident predicted: ${prediction.summary}`
     })
   })
   ```

4. Build observability dashboard in mcp-jobs UI:
   ```typescript
   // app/observability/page.tsx
   export default function ObservabilityPage() {
     const { data: logSummary } = useQuery(['log-summary'])
     const { data: predictions } = useQuery(['incident-predictions'])

     return (
       <div>
         <LogSummaryCard summary={logSummary} />
         <IncidentPredictionsTable predictions={predictions} />
       </div>
     )
   }
   ```

---

## Cost Optimization Strategy

### Model Selection Matrix

| Use Case | Primary Model | Fallback | Reasoning |
|----------|--------------|----------|-----------|
| Job classification | `openai/gpt-4o-mini` | `groq/llama-3.1-8b` | Fast, cheap, simple task |
| Failure analysis | `anthropic/claude-sonnet-4.5` | `openai/gpt-4o` | Better reasoning for complex errors |
| DLQ triage | `xai/grok-3` | `anthropic/claude-sonnet-4.5` | Multi-model comparison for critical decisions |
| Log summarization | `groq/llama-3.1-70b` | `openai/gpt-4o-mini` | Fast, cost-effective summarization |
| Incident prediction | `anthropic/claude-sonnet-4.5` | `xai/grok-3` | Strong pattern recognition |
| Doc generation | `openai/gpt-4o` | `anthropic/claude-sonnet-4.5` | Good at structured → narrative |
| Semantic extraction | `anthropic/claude-sonnet-4.5` | `openai/gpt-4o` | Deep reasoning required |

### Cost Reduction Tactics

1. **Cache common responses** (job type classifications, error patterns)
2. **Batch operations** (analyze 50 DLQ items together vs. 50 separate calls)
3. **Use cheaper models first** (gpt-4o-mini for initial triage, Claude Sonnet only for complex cases)
4. **Limit context** (send only relevant payload, not full job history)
5. **Scheduled batches** (run expensive analysis once daily, not per-event)

---

## Success Metrics

### Phase 1 (Gateway Setup)
- [ ] All 4 providers (OpenAI, Anthropic, xAI, Groq) accessible via gateway
- [ ] <100ms overhead vs. direct provider API
- [ ] Zero authentication errors

### Phase 2 (MCP Jobs AI)
- [ ] 90%+ job classification accuracy
- [ ] 50% reduction in unnecessary retries (better failure analysis)
- [ ] 80% DLQ triage automation (manual review only for complex cases)

### Phase 3 (Discovery AI)
- [ ] 20+ new implicit relationships discovered per scan
- [ ] 95%+ relationship validation accuracy (AI suggestions are correct)
- [ ] LLM-facing docs 30% more comprehensive than template-based

### Phase 4 (Observability AI)
- [ ] 90% log volume reduction (10K lines → 1K actionable insights)
- [ ] 70% incident prediction accuracy (catches issues before user impact)
- [ ] 60% MTTR reduction (faster root cause identification)

---

## Security & Compliance

### Key Management
- **Never expose gateway token to client** - server-side only
- **Use Vercel OIDC tokens** for auto-rotation (preferred over static keys)
- **Implement rate limiting** to prevent abuse

### Data Privacy
- **Redact PII** before sending to AI models (emails, IPs, tokens)
- **Log prompts and responses** for audit trail
- **Implement data retention** policies (delete AI call logs after 90 days)

### Provider Selection
- **Know where data goes** (OpenAI, Anthropic, xAI have different privacy policies)
- **Use on-prem models** for sensitive workloads (if needed)
- **Implement fallback to no-AI mode** if all providers unavailable

---

## Next Steps

**Immediate Actions**:
1. Access Vercel AI dashboard and enable gateway for mcp-jobs project
2. Generate gateway API key and add to Vercel environment variables
3. Install Vercel AI SDK in mcp-jobs submodule
4. Implement Phase 1 (Gateway Setup) and test all providers

**Questions to Resolve**:
1. Which Vercel integrations are already active? (Supabase, Inngest, Autonoma, Groq, etc.)
2. Do we have quota limits on AI Gateway? (requests/month, tokens/month)
3. Should we use Inngest for AI job processing instead of custom workers?

---

**References**:
- Vercel AI Gateway Docs: https://vercel.com/docs/ai-gateway
- Vercel AI SDK: https://ai-sdk.dev/docs/introduction
- AI Gateway Blog: https://vercel.com/blog/ai-gateway

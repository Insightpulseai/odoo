# A2A Interop Doctrine

> Use A2A for delegate / handoff / coordinate / aggregate. NOT for simple retrieval.
> SSOT: `ssot/agents/assistant_surfaces.yaml` (a2a_interop block)

---

## 1. Purpose

Agent-to-Agent (A2A) interop enables one assistant surface to **delegate work**, **hand off context**, **coordinate multi-step workflows**, or **aggregate results** across distinct assistant surfaces. It is the mechanism for cross-surface collaboration when a single surface lacks the permissions, context, or capabilities to complete a task alone.

A2A is NOT a replacement for MCP tools or direct retrieval. It adds latency, complexity, and audit surface. Use it only when the benefits of cross-surface delegation outweigh those costs.

### Canonical Rule

> **Use A2A when one surface must delegate to another surface that has distinct permissions, context, or capabilities. Use MCP for tool access. Use direct retrieval for single-step lookups. Never route through A2A what a single tool call can resolve.**

---

## 2. Surface Roles

Every assistant surface has exactly one A2A role:

| Surface | A2A Role | Rationale |
|---------|----------|-----------|
| **Diva Copilot** | **Hub** | Classifies intent, routes to specialists, aggregates results |
| **Odoo Copilot** | Participant | ERP execution — receives delegated tasks, escalates when out of scope |
| **Studio Copilot** | Participant | Creative finishing — receives asset/workflow handoffs |
| **Genie** | Participant | Analytics context — returns query results and provenance |
| **Document Intelligence Assistant** | Participant | Extraction/review — returns structured document data |
| **Landing Public Assistant** | **None** | Public surface, no A2A capability, no tenant context |

**Hub** means: can initiate delegation to any participant, aggregates cross-surface results, owns the conversation lifecycle.

**Participant** means: can receive delegated tasks from the hub, can escalate back to the hub, can hand off to other participants only via explicit allowed-target list.

**None** means: no A2A messages sent or received. The surface operates independently.

---

## 3. Allowed Patterns

### Pattern A: Hub delegates to participant

Diva classifies user intent, determines that a specialist surface is required, and sends a `delegate_task` message.

```
User -> Diva (hub)
         |
         +-- delegate_task --> Odoo Copilot
         |                        |
         +<-- return_result ------+
         |
User <-- aggregated response
```

### Pattern B: Participant escalates to hub

A participant determines the task is outside its scope and escalates back to Diva for rerouting.

```
User -> Odoo Copilot (participant)
         |
         +-- request_context --> Diva (hub)
         |                         |
         +<-- delegate_task -------+  (Diva may reroute to another participant)
```

### Pattern C: Participant-to-participant (explicit handoff)

A participant hands off to another participant that is in its `a2a_allowed_targets` list. The hub is notified for audit purposes.

```
Studio Copilot -- delegate_task --> Document Intelligence
                                       |
Studio Copilot <-- return_result ------+
Diva (hub)     <-- audit_notify -------+
```

### Pattern D: Result return

Any participant returns structured results to the caller (hub or another participant).

```
Genie -- return_result --> Diva (hub)
  {query_provenance, result_set, confidence}
```

---

## 4. Prohibited Patterns

These patterns are **banned**. Violations must be caught in code review and CI.

| Prohibited Pattern | Why |
|-------------------|-----|
| **A2A for every tool call** | Use MCP tools directly. A2A adds unnecessary latency and complexity for single-step operations. |
| **A2A for simple retrieval** | KB lookups, record reads, and single API calls do not need cross-surface delegation. Use direct retrieval or MCP. |
| **Recursive delegation loops** | Surface A delegates to B, B delegates back to A. Detect and reject in the message handler. Max delegation depth = 2. |
| **Silent delegation** | User must be informed (inline or via UI indicator) when their request is being handled by a different surface. No invisible handoffs. |
| **Public surface initiating A2A** | The landing public assistant has no tenant context and cannot initiate or receive A2A messages. |
| **Bypassing the hub for cross-domain aggregation** | Only Diva (hub) may aggregate results from multiple participants. Participants do not aggregate across surfaces. |

---

## 5. Message Types

All A2A communication uses exactly three message types:

### 5.1 delegate_task

Sent by hub or participant to request work from another surface.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `message_type` | Yes | string | `"delegate_task"` |
| `source_surface` | Yes | string | Originating surface ID |
| `target_surface` | Yes | string | Receiving surface ID |
| `customer_tenant_id` | Yes | string | Tenant context (UUID) |
| `workspace_id` | When applicable | string | Workspace/company scope |
| `intent_class` | Yes | string | Classified user intent |
| `context_payload` | Yes | object | Assembled context for the target |
| `correlation_id` | Yes | string | Trace ID for observability |
| `timeout_ms` | Yes | integer | Max wait before fallback (default: 30000) |
| `max_depth` | Yes | integer | Remaining delegation depth (starts at 2, decrements) |

### 5.2 request_context

Sent by a participant to request additional context from the hub or another allowed target.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `message_type` | Yes | string | `"request_context"` |
| `source_surface` | Yes | string | Requesting surface ID |
| `target_surface` | Yes | string | Surface being queried |
| `customer_tenant_id` | Yes | string | Tenant context (UUID) |
| `context_keys` | Yes | list[string] | Specific context items requested |
| `correlation_id` | Yes | string | Same trace ID as the parent delegation |

### 5.3 return_result

Sent by any surface to return structured results to the caller.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `message_type` | Yes | string | `"return_result"` |
| `source_surface` | Yes | string | Surface returning results |
| `target_surface` | Yes | string | Surface receiving results |
| `customer_tenant_id` | Yes | string | Tenant context (UUID) |
| `correlation_id` | Yes | string | Same trace ID as the parent delegation |
| `status` | Yes | string | `"success"`, `"partial"`, `"error"`, `"timeout"` |
| `result_payload` | Yes | object | Structured result data |
| `confidence` | No | float | 0.0-1.0, surface-specific confidence score |

---

## 6. Tenancy Rules

A2A messages are tenant-scoped. These rules are non-negotiable:

1. **`customer_tenant_id` is required** on every A2A message. Messages without a tenant ID are rejected.
2. **`workspace_id` is required** when the target surface is workspace-scoped (e.g., Odoo Copilot operates within a specific Odoo company).
3. **Public surfaces cannot initiate A2A.** The landing public assistant has no tenant context and is excluded from all A2A flows.
4. **Cross-tenant delegation is forbidden.** A message's `customer_tenant_id` must match the receiving surface's active tenant context.
5. **Tenant context propagates.** When Diva delegates to Odoo Copilot, the tenant ID from the original request propagates unchanged. No re-authentication mid-chain.

---

## 7. Retrieval Rules

A2A does not replace retrieval. The routing decision is:

| Need | Mechanism | Example |
|------|-----------|---------|
| Read a record | MCP tool | `odoo.record.read(model='account.move', id=42)` |
| Search a KB | Direct retrieval | Azure AI Search query against `odoo-docs-kb` index |
| Execute a multi-step ERP workflow | A2A delegation | Diva delegates "close the month" to Odoo Copilot |
| Get analytics context for a decision | A2A delegation | Diva delegates "revenue trend Q1" to Genie |
| Extract fields from a document | A2A delegation | Studio delegates invoice PDF to Document Intelligence |

**Rule:** If the task can be completed with a single MCP tool call or a single retrieval query, do NOT use A2A.

---

## 8. Action Rules

When a delegated task involves a **write operation** (record create/update, workflow transition, approval), additional rules apply:

1. **Fail-closed by default.** If the receiving surface cannot verify permissions, it rejects the action and returns an error.
2. **Confirmation required for destructive actions.** Delete, cancel, and reversal actions require explicit user confirmation before execution. The participant returns a `"confirmation_required"` status.
3. **Audit trail is mandatory.** Every write action triggered via A2A must be logged in `ipai.copilot.audit` with the full delegation chain (source, hub, target, correlation_id).
4. **No escalation of privilege.** A delegated task runs with the permissions of the user who initiated the original request, not the hub's service identity.

---

## 9. Audit and Observability

Every A2A interaction must produce audit records:

| Event | Logged By | Required Fields |
|-------|-----------|----------------|
| Delegation sent | Source surface | correlation_id, source, target, intent_class, tenant_id, timestamp |
| Delegation received | Target surface | correlation_id, source, target, tenant_id, timestamp |
| Result returned | Target surface | correlation_id, status, latency_ms, tenant_id |
| Result received | Source surface | correlation_id, status, latency_ms |
| Timeout | Source surface | correlation_id, target, timeout_ms |
| Rejection | Target surface | correlation_id, reason, tenant_id |

**Trace propagation:** The `correlation_id` propagates through the entire delegation chain. All surfaces emit OpenTelemetry spans tagged with the correlation ID.

**Dashboard:** A2A metrics (delegation count, latency p50/p95, error rate, timeout rate) must be visible in the platform operations dashboard.

---

## 10. Rollout Phases

### Phase 1: Hub-to-participant only (target: Q2 2026)

- Diva (hub) delegates to Odoo Copilot and Genie only
- No participant-to-participant handoffs
- All delegations are read-only (no write actions via A2A)
- Audit logging active, dashboard passive

### Phase 2: Full participant mesh (target: Q3 2026)

- Enable participant-to-participant handoffs (Pattern C)
- Add Studio Copilot and Document Intelligence as A2A participants
- Enable write actions with confirmation flow
- Dashboard active with alerting

### Phase 3: Multi-tenant production (target: Q4 2026)

- Enable cross-workspace delegation (same tenant, different workspace)
- Performance optimization (connection pooling, message batching)
- SLA enforcement (timeout budgets, circuit breakers)
- External A2A surface onboarding (partner integrations)

---

## 11. MCP Tool Governance (Unchanged)

A2A does not change MCP tool governance. Tools remain the primary mechanism for structured resource access.

### First-Wave Tool Envelope

Keep the tool set small and explicit. Only enable tools that have:
- A stable contract
- Auth via managed identity or OAuth
- Audit logging
- A defined owner

See `docs/architecture/AI_RUNTIME_AUTHORITY.md` for the current tool profiles per surface.

### Tool Registration

Tools are registered in Azure AI Foundry Agent Service. Each tool has:
- A versioned schema
- An auth mode (managed identity, OAuth, API key)
- A tenant scope (none, internal, governed, tenant-isolated)
- An action mode (read-only, fail-closed, controlled)

---

## SSOT References

- Machine-readable surfaces: `ssot/agents/assistant_surfaces.yaml`
- AgentOps policy: `ssot/governance/agentops_policy.yaml`
- Tool profiles: `ssot/agents/diva_copilot.yaml#tool_profiles`
- Assistant surfaces doc: `docs/architecture/ASSISTANT_SURFACES.md`
- Tenancy model: `ssot/architecture/tenancy_model.yaml`

---

*Last updated: 2026-03-24*

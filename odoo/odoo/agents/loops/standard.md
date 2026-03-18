# Standard Agent Execution Loop

**Version**: 1.0
**Type**: Deterministic control loop for all production agents.

---

## Loop: Observe -> Reason -> Act -> Verify

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ OBSERVE  │───>│  REASON  │───>│   ACT    │───>│  VERIFY  │
│          │    │          │    │          │    │          │
│ Read env │    │ Evaluate │    │ Execute  │    │ Check    │
│ + memory │    │ policies │    │ skills   │    │ outcomes │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
      ^                                               │
      │               LOOP (until done)               │
      └───────────────────────────────────────────────┘
```

## Phases

### 1. OBSERVE
- Read current environment state (repo, CI status, memory)
- Retrieve relevant memory items via `memory.search_items()`
- Identify what changed since last loop iteration

### 2. REASON
- Evaluate policies (`policies_ref`) for constraints and routing
- Determine applicable skills from agent's skill set
- Decide action plan (ordered list of skill invocations)

### 3. ACT
- Execute skills in order
- Each skill produces deterministic output
- All actions are logged (audit trail)

### 4. VERIFY
- Check outcomes against success criteria
- Update memory with results (`memory.items`)
- If verification fails: loop back to OBSERVE with failure context
- If verification passes: commit results and exit

## Invariants

- **Idempotent**: Running the loop twice on same input produces same output
- **Bounded**: Maximum 10 iterations per invocation (prevent infinite loops)
- **Auditable**: Every action is recorded in memory.sessions
- **Recoverable**: If agent crashes, restarting picks up from last OBSERVE

## Exit Conditions

1. **Success**: All verification checks pass
2. **Failure**: Max iterations reached without success
3. **Abort**: Policy violation detected (escalate to human)

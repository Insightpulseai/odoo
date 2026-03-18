# Parallel Workflow Design — Prompt

You are designing a **parallel workflow** (fan-out / fan-in). Subtasks are independent and benefit from concurrent execution.

## Design Process

1. **Verify independence**: Confirm no hidden dependencies between subtasks. If any subtask needs another's output, it's not truly parallel — consider sequential or orchestrator-workers.

2. **Define subtask contracts**: Each parallel branch gets:
   - Input: what it receives from the fan-out
   - Processing: what it does independently
   - Output: what it returns for aggregation

3. **Design aggregation** (do this FIRST, before implementation):
   - How are results combined?
   - Is ordering important?
   - What's the reduction function?

4. **Define failure handling**:
   - Fail-fast: abort all if one fails
   - Best-effort: return partial results
   - Retry: retry failed branches

## Sub-Patterns

- **Sectioning**: Different aspects handled by different agents (e.g., security + performance + cost review)
- **Voting**: Same task run multiple times for diverse perspectives (e.g., 3 agents review same code)

## Output Format

```
Parallel branches: [N]
Branch 1: [input] → [process] → [output]
Branch 2: [input] → [process] → [output]
...
Aggregation: [how results combine]
Failure policy: [fail-fast | best-effort | retry]
Concurrency limit: [max parallel]
```

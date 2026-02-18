# Anthropic Engineering Practices for AI Agents

Synthesized from [Anthropic Engineering](https://www.anthropic.com/engineering).

## 1. Agent Workflows

Patterns for structuring LLM applications to increase reliability and capability.

### A. Prompt Chaining

**Concept**: Decompose a task into a fixed sequence of steps.
**Use Case**: Trade latency for accuracy on known, linear processes.
**Example**: Generated copy -> Translated copy -> Format check.

### B. Routing

**Concept**: Classify input and direct to specialized prompts/models.
**Use Case**: Complex tasks with distinct categories.
**Example**: Support Triage (General vs. Technical vs. Refund). Route "Easy" queries to cheaper models, "Hard" to smarter ones.

### C. Parallelization

**Concept**: Run multiple LLM calls simultaneously.
**Variations**:

- **Sectioning**: Split independent subtasks (e.g., Guardrails vs. Response).
- **Voting**: Multiple attempts to increase confidence (e.g., Vulnerability scanning).

### D. Orchestrator-Workers

**Concept**: Central "Manager" LLM dynamically breaks down a task and delegates to "Worker" LLMs.
**Use Case**: Complex tasks where subtasks aren't known upfront (e.g., "Change this feature across the codebase").

### E. Evaluator-Optimizer

**Concept**: Iterative loop where one LLM generates and another critiques/refines.
**Use Case**: Tasks with clear evaluation criteria (e.g., Translation refinement, Code optimization).

---

## 2. Tool Design Principles

### Naming & Namespacing

- **Rule**: Distinct, prefixed names reduce confusion.
- **Bad**: `search`, `get_data`
- **Good**: `asana_search`, `jira_ticket_get`
- **Why**: Reduces context pollution and model confusion between similar tools.

### High-Signal Context

- **Rule**: Return information the _model_ understands, not just the machine.
- **Avoid**: Raw UUIDs, Base64 blobs, cryptic internal IDs.
- **Prefer**: Names, Titles, URLs, File Types.
- **Pattern**: `ResponseFormat` enum (`concise` vs `detailed`) to let the model choose verbosity.

### Code Execution > Chatty Loops (MCP)

- **Problem**: Chaining 10 tool calls to filter a list is slow and expensive.
- **Solution**: Execute code (e.g., JavaScript/Python) to filter/transform data _inside_ the environment.
- **Benefit**:
  - **Progressive Disclosure**: Read tool definitions on-demand.
  - **Context Efficiency**: Return 5 filtered rows instead of 10,000 raw rows.
  - **Control Flow**: Handle loops/retries in code, not LLM turns.

---

## 3. Evaluations (The "Zero to One" Roadmap)

### Phase 1: Start Small & Real (Tasks 0-50)

- **Source**: 20-50 tasks based on real manual checks or user reports.
- **Principle**: 80/20 rule. Don't wait for "perfect" coverage.
- **Dataset**: Use real failure cases.

### Phase 2: Unambiguous Reference Solutions

- **Rule**: Two experts should agree on Pass/Fail.
- **Check**: Can a human pass this task with the provided instructions?
- **Golden**: Have a "Reference Solution" (known good output) to verify the grader itself.

### Phase 3: Balanced Sets

- **Rule**: Test positive AND negative cases.
- **Example**: Test that it _does_ search when needed, and _does not_ search when answering simple facts.
- **Why**: Prevents "over-triggering" optimization.

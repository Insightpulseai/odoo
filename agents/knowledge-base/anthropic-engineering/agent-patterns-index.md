# Knowledge: Anthropic Engineering — Agent Patterns Index

## Source

- **Blog**: https://www.anthropic.com/engineering
- **Extracted**: 2026-03-16
- **Articles indexed**: 19

---

## Article Index (Relevance-Ranked for IPAI)

### Tier 1: Foundational Agent Architecture (Must-Know)

| # | Article | Key Pattern | IPAI Mapping |
|---|---------|-------------|-------------|
| 1 | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Workflows vs agents, 5 workflow patterns, augmented LLM | Agent factory design, constitution |
| 2 | [Context engineering for agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 4 context components, compaction, sub-agents, structured notes | CLAUDE.md, skill design, memory |
| 3 | [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 3 grader types, 8-step roadmap, pass@k/pass^k | Foundry cloud eval, eval datasets |
| 4 | [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 5 tool design principles, namespace, context efficiency | MCP tools, tool allowlist |
| 5 | [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Orchestrator-worker, citation agent, 8 prompt strategies | Supervisor agent, deep research |

### Tier 2: Implementation Patterns (Apply to Factory)

| # | Article | Key Pattern | IPAI Mapping |
|---|---------|-------------|-------------|
| 6 | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer + coding agent, session handoff, progress files | Agent factory sessions, task persistence |
| 7 | [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | Agents write code to call tools instead of direct calls | MCP server design |
| 8 | [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices) | Agentic coding patterns, CLAUDE.md usage | Our daily workflow |
| 9 | [The "think" tool](https://www.anthropic.com/engineering/claude-think-tool) | Scratchpad for complex reasoning in tool-use chains | Agent reasoning patterns |
| 10 | [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) | Dynamic tool discovery and execution | Tool catalog, MCP |

### Tier 3: Specialized Topics (Reference)

| # | Article | Topic |
|---|---------|-------|
| 11 | [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler) | Multi-agent team development |
| 12 | [Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing) | Filesystem/network isolation |
| 13 | [Desktop Extensions](https://www.anthropic.com/engineering/desktop-extensions) | One-click MCP server installation |
| 14 | [SWE-bench Verified](https://www.anthropic.com/engineering/swe-bench-sonnet) | Benchmark performance |
| 15 | [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | RAG with contextual embeddings |
| 16 | [Quantifying infra noise in evals](https://www.anthropic.com/engineering/infrastructure-noise) | Eval reliability |
| 17 | [Eval awareness in BrowseComp](https://www.anthropic.com/engineering/eval-awareness-browsecomp) | Eval integrity |
| 18 | [AI-resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) | Hiring eval design |
| 19 | [Postmortem of three issues](https://www.anthropic.com/engineering/a-postmortem-of-three-recent-issues) | Incident response |

---

## Pattern 1: Building Effective Agents

### Workflow vs Agent Decision

| Use Case | Choose | Why |
|----------|--------|-----|
| Well-defined tasks, fixed subtasks | **Workflow** | Predictable, lower cost, fewer errors |
| Open-ended problems, unknown steps | **Agent** | Flexible, dynamic tool selection |
| Most applications | **Start with workflow** | Optimize single LLM calls first |

### 5 Workflow Patterns

| Pattern | How It Works | IPAI Example |
|---------|-------------|-------------|
| **Prompt Chaining** | Sequential steps with checkpoints | Spec → plan → tasks → implement |
| **Routing** | Classify input → specialized handler | Copilot routes: BIR vs expense vs accounting |
| **Parallelization** | Simultaneous LLM calls (sectioning or voting) | Multi-file code review, PR quality gate |
| **Orchestrator-Workers** | Central LLM delegates to worker LLMs | Supervisor agent, multi-agent workflows |
| **Evaluator-Optimizer** | Generate → evaluate → improve loop | Cloud eval + iterative improvement |

### Augmented LLM Building Block

```
LLM + Retrieval + Tools + Memory = Augmented LLM
         ↑           ↑         ↑
    Azure AI     MCP/OpenAPI   Supabase ops.*
    Search       Function      + Lakebase
                 Calling
```

### Key Principles

1. **Simplicity** — avoid premature complexity; frameworks can obscure logic
2. **Transparency** — show agent planning and reasoning steps
3. **Tool design** — invest effort equivalent to human-computer interface design
4. **Measure first** — optimize single LLM calls before adding agentic patterns

---

## Pattern 2: Context Engineering

### 4 Context Components

| Component | Design Principle | IPAI Implementation |
|-----------|-----------------|---------------------|
| **System prompts** | Right altitude — specific + flexible | CLAUDE.md, constitution, rules files |
| **Tools** | Minimal viable toolset, non-overlapping | Tool allowlist, MCP servers |
| **Examples** | Diverse canonical examples | Eval datasets, skill examples |
| **Dynamic retrieval** | Just-in-time via tools | Azure AI Search, Foundry IQ |

### Long-Horizon Techniques

| Technique | How | IPAI Use |
|-----------|-----|----------|
| **Compaction** | Summarize history, preserve key decisions | Auto-context compression in long sessions |
| **Structured notes** | Persist to files outside context window | `NOTES.md`, todo lists, memory files |
| **Sub-agents** | Focused agents with clean context, report summaries | Explore agents, subagents (git-expert, devops-expert) |

### Golden Rule

> "Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."

---

## Pattern 3: Agent Evaluations

### 3 Grader Types

| Grader | Speed | Cost | Best For |
|--------|-------|------|----------|
| **Code-based** | Fast | Cheap | Deterministic checks (string match, test pass) |
| **Model-based** | Medium | Medium | Open-ended quality (rubric-based scoring) |
| **Human** | Slow | Expensive | Calibration, gold standard |

### 8-Step Eval Roadmap

1. Start early (20-50 tasks from real failures)
2. Convert manual tests to automated
3. Unambiguous task design (two experts → same verdict)
4. Balanced problems (test both positive and negative cases)
5. Robust eval harness (isolated trials, no shared state)
6. Thoughtful graders (grade output, not path)
7. Transcript review (read many transcripts)
8. Monitor saturation (when all solvable tasks pass, add harder ones)

### Key Metrics

| Metric | Formula | Use |
|--------|---------|-----|
| **pass@k** | P(≥1 success in k tries) | Acceptable when multiple solutions OK |
| **pass^k** | P(all k succeed) | Required for customer-facing reliability |

### IPAI Eval Mapping

| Anthropic Pattern | IPAI Implementation |
|-------------------|---------------------|
| Code-based graders | `validate_seed_state.py`, CI test assertions |
| Model-based graders | Foundry `builtin.task_adherence`, `builtin.fluency` |
| Human graders | Manual review (calibration) |
| 20-50 task start | `evals/odoo-copilot/dataset.jsonl` (expand to 20+) |
| Capability evals | New features being developed |
| Regression evals | Existing features that must not break |

---

## Pattern 4: Tool Design (5 Principles)

| Principle | Rule | Anti-Pattern |
|-----------|------|-------------|
| **Choose right tools** | Fewer, smarter tools > many simple ones | `list_contacts` → use `search_contacts` instead |
| **Namespace strategically** | `asana_search`, `jira_search` prefixes | Generic `search` with type parameter |
| **Return meaningful context** | Semantic identifiers, actionable data | Raw UUIDs, full database dumps |
| **Optimize token efficiency** | Pagination, filtering, truncation defaults | Return all results every time |
| **Engineer descriptions** | Like explaining to a new hire | Vague one-line description |

### Tool Description Template

```
Think of how you would describe your tool to a new hire on your team.
- What does it do?
- When should they use it vs other tools?
- What are the valid parameter formats?
- What does the response mean?
```

---

## Pattern 5: Multi-Agent Research System

### Architecture

```
User Query
    ↓
Lead Agent (Opus 4) — plans, delegates, synthesizes
    ├── Subagent 1 (Sonnet 4) — web search topic A
    ├── Subagent 2 (Sonnet 4) — web search topic B
    └── Subagent 3 (Sonnet 4) — web search topic C
    ↓
Lead Agent synthesizes findings
    ↓ (if gaps found, spawn more subagents)
Citation Agent — attributes sources
    ↓
Final Research Report
```

### 8 Prompt Engineering Strategies

1. **Think like your agents** — simulate their behavior with their exact prompts
2. **Teach delegation** — clear objectives, output formats, boundaries
3. **Scale effort to complexity** — match resources to query difficulty
4. **Critical tool design** — distinct purposes, clear descriptions
5. **Self-improvement** — let Claude diagnose failures and suggest fixes
6. **Start wide, narrow down** — broad queries → progressive refinement
7. **Guide thinking** — extended thinking as controllable scratchpad
8. **Parallel tool calling** — 3+ tools simultaneously (90% time reduction)

### Key Metrics

- Multi-agent outperformed single-agent by **90.2%** on internal research eval
- Token usage explains **80%** of performance variance
- Multi-agent uses **~15x more tokens** than single chat
- Parallel tool calling cuts research time by **up to 90%**

---

## Pattern 6: Long-Running Agent Harnesses

### Two-Part Architecture

| Component | Role | Session |
|-----------|------|---------|
| **Initializer Agent** | Creates feature spec, progress file, setup script, initial commit | First session only |
| **Coding Agent** | Works on one feature at a time, tests, commits, updates progress | Every subsequent session |

### Session Startup Pattern

```
1. Verify working directory
2. Read git logs + progress files
3. Review feature list → select highest-priority incomplete
4. Start dev server
5. Run basic functionality tests
6. Implement single feature
7. Document and commit
8. Update progress file
```

### Key Rules

- **One feature at a time** — prevents agent from doing too much
- **Merge-ready code** — every commit must be clean
- **Self-verify** — test as human user would (Puppeteer/browser automation)
- **Progress persistence** — update files before session ends

### IPAI Application

This pattern maps directly to:
- `agents/foundry/policies/factory/ops_platform__factory__resolution_rules__v1.policy.yaml` — 8-stage pipeline
- Agent factory session management
- Claude Code CLAUDE.md + memory files for context persistence

---

## IPAI Agent Factory: Anthropic Patterns Applied

| Factory Stage | Anthropic Pattern | Implementation |
|---------------|-------------------|----------------|
| Intake | Routing (classify intent) | Route to correct template/skill |
| Template resolution | Augmented LLM (retrieval + tools) | Adoption matrix lookup |
| Project creation | Initializer Agent pattern | Create workspace + context |
| Skill compilation | Prompt Chaining (sequential steps) | Resolve dependencies → compile |
| Artifact generation | Orchestrator-Workers | Lead agent delegates to specialized generators |
| Evaluation | Evaluator-Optimizer loop | Smoke eval → policy eval → iterate |
| Packaging | Prompt Chaining | Channel resolution → metadata → register |
| Publishing | Routing + approval gates | Environment protection → promote |

---

## Sources

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Context engineering for agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

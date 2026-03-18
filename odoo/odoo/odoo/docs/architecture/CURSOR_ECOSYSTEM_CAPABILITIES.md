# Cursor Ecosystem Capabilities (Bugbot + Composer + Codebase Indexing)

**Date**: 2026-01-24
**Goal**: Map Cursor's Bugbot, Composer, and codebase indexing capabilities to our stack:
Odoo CE (OCA-first) + DigitalOcean + Supabase (SSOT) + Vercel + n8n + GitHub

---

## 1) Bugbot — AI Code Review Agent

### What It Is
Bugbot is Cursor's AI agent that runs automatically on pull requests to detect logic bugs, edge cases, and security issues before code reaches production. During beta, it reviewed 1M+ PRs and flagged 1.5M+ issues with 50%+ fix rate.

**Key capabilities**:
- Logic bug detection (race conditions, null pointer exceptions)
- Security vulnerability scanning
- Edge case identification
- AI-generated code validation (where subtle errors are common)
- Custom rules via `.cursor/rules` files

**Pricing**: $40/user/month (Cursor Business)

### Stack Fit

| Layer | Integration Point | Value |
|-------|------------------|-------|
| **GitHub PRs** | Pre-merge gate | Catches bugs before CI passes |
| **Odoo addons** | Python/XML review | Detects ORM misuse, security holes |
| **Supabase migrations** | SQL review | Catches RLS gaps, injection risks |
| **n8n workflows** | JSON validation | Logic flow errors |

### Recommended Configuration

```yaml
# .cursor/rules/odoo.mdc
description: Odoo CE + OCA module review rules
rules:
  - pattern: "self.env.cr.execute"
    severity: warning
    message: "Prefer ORM methods over raw SQL"
  - pattern: "sudo()"
    severity: info
    message: "Verify sudo() is necessary - check RLS implications"
  - pattern: "api.model"
    severity: info
    message: "Ensure @api.model methods don't modify self"
```

```yaml
# .cursor/rules/supabase.mdc
description: Supabase migration review rules
rules:
  - pattern: "CREATE TABLE"
    requires: "ENABLE ROW LEVEL SECURITY"
    message: "Tables must have RLS enabled"
  - pattern: "DROP TABLE"
    severity: error
    message: "Use soft deletes (deleted_at) instead"
```

### Evidence Target
- Store Bugbot findings in `observability.code_review_events`
- Aggregate stats: bugs caught / severity / fix rate

---

## 2) Composer — AI Coding Agent (Cursor 2.0)

### What It Is
Cursor 2.0's Composer is a mixture-of-experts model trained via reinforcement learning inside real codebases. It learned to use development tools (semantic search, file editors, terminal) through hands-on practice.

**Key capabilities**:
- Codebase-wide semantic search
- Multi-agent parallelism (up to 8 agents simultaneously)
- Test running + linter fixing
- ~250 tokens/second, 4x faster than comparable models
- Deep codebase understanding via embeddings

### Stack Fit

| Task | Composer Role | Output |
|------|---------------|--------|
| **Spec Kit generation** | Draft PRDs, plans, tasks from requirements | `spec/<feature>/` bundles |
| **Odoo module scaffolding** | Generate models, views, security from spec | `addons/ipai/<module>/` |
| **Migration authoring** | Write SQL migrations with context | `db/migrations/*.sql` |
| **Workflow automation** | Generate n8n workflow JSON | `n8n/workflows/*.json` |
| **Test generation** | Create pytest/unittest from implementation | `tests/` |

### Multi-Agent Pattern (8 parallel agents)

```
┌─────────────────────────────────────────────────────────────┐
│              COMPOSER MULTI-AGENT ORCHESTRATION              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Agent 1: Spec research       Agent 2: Model generation     │
│  Agent 3: View scaffolding    Agent 4: Security rules       │
│  Agent 5: Test generation     Agent 6: Migration SQL        │
│  Agent 7: Docs update         Agent 8: CI validation        │
│                                                              │
│  ───────────────────────────────────────────────────────    │
│                         ↓                                    │
│              Merge → Review → Commit                         │
└─────────────────────────────────────────────────────────────┘
```

### Recommended .cursor/rules

```yaml
# .cursor/rules/project.mdc
description: IPAI Project Rules
rules:
  - name: "OCA-first"
    instruction: "Prefer OCA modules over custom ipai_* when available"
  - name: "Spec-driven"
    instruction: "Reference spec/<feature>/ before implementing"
  - name: "Evidence-required"
    instruction: "All deploys must produce docs/evidence/ artifacts"
  - name: "CLAUDE.md authority"
    instruction: "CLAUDE.md is the source of truth for project rules"
```

---

## 3) Codebase Indexing — Semantic Search

### What It Is
Cursor indexes your entire codebase using embeddings, enabling semantic search that finds code by meaning, not just text. Uses Tree-sitter for AST parsing to identify semantic blocks (functions, classes, methods).

**Key capabilities**:
- Natural language queries ("user authentication logic")
- Cross-file relationship understanding
- @ references for precise context injection
- Privacy mode (code never stored/trained on)
- Monorepo sub-tree selection

### Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CODEBASE INDEXING FLOW                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Source Files → Tree-sitter AST → Semantic Chunks           │
│        ↓                                                     │
│  Embedding Model (MiniLM L6 v2) → Vectors                   │
│        ↓                                                     │
│  FAISS/Vector Index → Semantic Search                       │
│        ↓                                                     │
│  Query: "month-end close logic" → Relevant code blocks      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Three Search Methods (Complementary)

| Method | Tool | Best For |
|--------|------|----------|
| **Exact text** | ripgrep (Grep tool) | Literals, identifiers, imports |
| **Structure-aware** | ast-grep | Declarations, pattern audits |
| **Semantic** | Embeddings | Intent queries, "retry logic" |

### Stack Integration

```bash
# Use @ references for precise context
@CLAUDE.md              # Project rules
@spec/close-orchestration/prd.md  # Feature spec
@addons/ipai/ipai_finance_ppm/    # Module context
@db/migrations/                    # Schema history
```

### Building Our Own Index (for n8n/Supabase integration)

We can build a parallel semantic index stored in Supabase for:
- Agent context injection
- llms-full.txt generation
- Cross-agent knowledge sharing

---

## 4) Integration Architecture

### Flow: Cursor → GitHub → n8n → Supabase

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [1] CURSOR (local)                                          │
│  ├── Composer: Multi-agent code generation                   │
│  ├── Codebase Index: Semantic search for context             │
│  └── Output: PR with changes                                 │
│                                                              │
│  [2] GITHUB (PR created)                                     │
│  ├── Bugbot: AI code review (logic bugs, security)           │
│  ├── CI: Lint + test + build gates                           │
│  └── Output: Review comments, approval/block                 │
│                                                              │
│  [3] N8N (webhook on PR merge)                               │
│  ├── Record event in Supabase observability                  │
│  ├── Trigger deploy workflow                                 │
│  └── Update codebase index artifacts                         │
│                                                              │
│  [4] SUPABASE (system of record)                             │
│  ├── observability.jobs: PR events, deploy status            │
│  ├── observability.code_review_events: Bugbot findings       │
│  └── kb.code_chunks: Semantic index for RAG                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Supabase Schema for Code Intelligence

```sql
-- Semantic code chunks for RAG / agent context
CREATE TABLE IF NOT EXISTS kb.code_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path TEXT NOT NULL,
    chunk_type TEXT NOT NULL,  -- 'function', 'class', 'method', 'module'
    chunk_name TEXT,           -- e.g., 'def create_invoice'
    content TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    embedding VECTOR(384),     -- MiniLM L6 v2 dimensions
    metadata JSONB,            -- language, dependencies, etc.
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    repo_sha TEXT              -- Git commit for versioning
);

CREATE INDEX ON kb.code_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON kb.code_chunks (file_path);
CREATE INDEX ON kb.code_chunks (chunk_type);

-- Bugbot review findings
CREATE TABLE IF NOT EXISTS observability.code_review_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pr_number INTEGER NOT NULL,
    repo TEXT NOT NULL,
    reviewer TEXT NOT NULL,    -- 'bugbot', 'human', etc.
    finding_type TEXT,         -- 'bug', 'security', 'style'
    severity TEXT,             -- 'critical', 'warning', 'info'
    file_path TEXT,
    line_number INTEGER,
    message TEXT,
    fixed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON observability.code_review_events (pr_number);
CREATE INDEX ON observability.code_review_events (finding_type, severity);
```

---

## 5) Recommended Implementation Phases

### P0: Immediate (This Week)
1. **Enable Bugbot on GitHub** — Add to PRs for ipai_* modules
2. **Create .cursor/rules/** — Project rules for Odoo/Supabase patterns
3. **Document @ reference patterns** — Add to CLAUDE.md

### P1: Next Iteration
1. **Add code_review_events table** — Store Bugbot findings
2. **Create n8n workflow** — Webhook on PR review → write to Supabase
3. **Build kb.code_chunks table** — Schema for semantic index

### P2: Later
1. **Self-hosted indexing** — Tree-sitter + embeddings pipeline
2. **RAG integration** — Query code chunks for agent context
3. **Cross-agent memory** — Share indexed context across Claude/Cursor/n8n

---

## 6) Guardrails

| Tool | Guardrail | Why |
|------|-----------|-----|
| **Bugbot** | Gate, not blocker | False positives happen; human reviews still needed |
| **Composer** | PR-only, never direct-to-main | Multi-agent can diverge; needs review |
| **Codebase Index** | Privacy mode ON | Embeddings shouldn't leave org |
| **Semantic search** | Combine with exact search | Embeddings miss literals/identifiers |

---

## 7) References

- [Cursor 2.0 and Composer](https://cursor.com/blog/2-0)
- [Codebase Indexing Docs](https://cursor.com/docs/context/codebase-indexing)
- [Composer Overview](https://docs.cursor.com/composer/overview)
- [Bugbot](https://cursor.com/bugbot)
- [Bugbot vs CodeRabbit](https://www.getpanto.ai/blog/bugbot-vs-coderabbit)
- [AI Code Review State 2025](https://www.devtoolsacademy.com/blog/state-of-ai-code-review-tools-2025/)
- [Semantic Code Search - Greptile](https://www.greptile.com/blog/semantic-codebase-search)
- [CocoIndex Codebase Indexing](https://cocoindex.io/blogs/index-code-base-for-rag)

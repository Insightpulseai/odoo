# Kapa-style Docs Copilot for Odoo CE + OCA 18.0

Production-grade documentation search system with hybrid retrieval (vector + lexical), citation-first answers, and multi-source routing.

## Architecture

```
Sources (sitemap, GitHub repos)
   ↓ crawler.py (versioning + structure-aware chunking)
Supabase PostgreSQL (documents, chunks, embeddings)
   ↓ rag.search_hybrid() (vector 65% + lexical 35%)
OpenAI GPT-4o-mini (answer generation with citations)
   ↓
Deployment:
- /api/ask (Vercel/Lambda function)
- Slack/Mattermost bot
- Website widget (future)
```

## Key Features

### 1. Multi-Source Ingestion
- **Odoo Official Docs**: Sitemap crawl with HTML parsing
- **OCA Repositories**: GitHub API crawl (README, manifests, models, views, security)
- **Internal Modules**: InsightPulse IPAI modules with patches and runbooks
- **Versioning**: Tracks `doc_version`, `commit_sha`, `visibility` (public/internal)

### 2. Hybrid Retrieval
- **Vector Search**: Cosine similarity on OpenAI `text-embedding-3-small` (1536 dims)
- **Lexical Search**: Full-text (tsvector) + trigram (pg_trgm) for exact matches
- **Weighted Scoring**: 65% vector + 35% lexical (configurable)
- **Multi-source Routing**: Search internal docs first, then OCA, then Odoo official

### 3. Citation-First Answers
- Every answer includes clickable citations with:
  - Canonical URL with section anchor
  - Version (odoo-18.0, oca-18.0, ipai-main)
  - Commit SHA (7-char prefix)
  - Confidence score
- Answers grounded in retrieved context only (no hallucination)

### 4. Feedback Loop
- Questions, answers, and votes tracked in `rag.questions`, `rag.answers`, `rag.answer_votes`
- Eval sets for continuous quality improvement
- Performance monitoring view (`rag.search_performance`)

## Installation

### Prerequisites
```bash
# Python 3.11+
pip install requests beautifulsoup4 pyyaml openai

# PostgreSQL 15+ with pgvector
# Supabase project with schema deployed
```

### Database Setup
```bash
# Deploy hybrid search schema
psql "$POSTGRES_URL" < packages/db/sql/08_rag_hybrid_search.sql

# Verify indexes
psql "$POSTGRES_URL" -c "
  SELECT indexname FROM pg_indexes
  WHERE indexname IN (
    'idx_chunks_tsv',
    'idx_chunks_trgm',
    'idx_chunks_ivfflat',
    'idx_documents_visibility'
  );
"
```

### Environment Variables
```bash
# Add to ~/.zshrc or .env
export SUPABASE_URL="https://xkxyvboeubffxxbebsll.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"
export OPENAI_API_KEY="sk-..."
export TENANT_ID="your_tenant_uuid"
export GITHUB_TOKEN="ghp_..." # Optional, for higher rate limits
```

## Usage

### 1. Crawl Documentation Sources

**Full crawl (all sources)**:
```bash
python tools/docs-crawler/crawler.py \
  --config tools/docs-crawler/config.yaml \
  --out out/docs-crawler
```

**Single source crawl**:
```bash
# Just OCA account-financial-tools
python tools/docs-crawler/crawler.py \
  --config tools/docs-crawler/config.yaml \
  --sources oca_account_financial_tools \
  --out out/oca-account

# Just internal IPAI modules
python tools/docs-crawler/crawler.py \
  --config tools/docs-crawler/config.yaml \
  --sources ipai_odoo_ce ipai_finance_ppm \
  --out out/ipai-docs
```

**Outputs**:
- `documents.json`: Document metadata with checksums, versions, commit SHAs
- `chunks.json`: Structure-aware chunks with section paths, embeddings metadata

### 2. Load Documents into Supabase

```bash
# TODO: Create ingestion script that:
# 1. Reads documents.json and chunks.json
# 2. Upserts to rag.documents and rag.chunks
# 3. Generates embeddings via OpenAI
# 4. Handles dedupe by content_checksum
```

### 3. Query via /api/ask

**CLI testing**:
```bash
python tools/docs-crawler/api_ask.py \
  --question "How do I create RLS policies in Odoo 18?" \
  --top-k 6 \
  --visibility internal
```

**Example response**:
```json
{
  "question": "How do I create RLS policies in Odoo 18?",
  "answer": "According to the OCA account-financial-tools documentation [1], RLS policies in Odoo 18 are created using the `ir.rule` model...",
  "citations": [
    {
      "id": 1,
      "url": "https://github.com/OCA/account-financial-tools/blob/18.0/README.rst",
      "section": "Security > Row Level Security",
      "version": "oca-18.0",
      "commit": "a3f2b1c",
      "anchor": "#security-row-level-security",
      "score": 0.892
    },
    ...
  ],
  "confidence": 0.876,
  "search_method": "hybrid",
  "model": "gpt-4o-mini",
  "tokens_used": 542
}
```

### 4. Deploy API Endpoint

**Vercel Function**:
```bash
# vercel/functions/api/ask.py
from tools.docs_crawler.api_ask import lambda_handler

def handler(request):
    return lambda_handler(
        {"body": request.get_json()},
        None
    )
```

**Deploy**:
```bash
vercel --prod
# Access at: https://your-domain.vercel.app/api/ask
```

## Configuration

### config.yaml

**Key settings**:
```yaml
sources:
  - type: sitemap | github_repo
    name: unique_identifier
    doc_version: "odoo-18.0" | "oca-18.0" | "ipai-main"
    visibility: public | internal

chunking:
  max_tokens: 750
  overlap_tokens: 120
  split_by_headings: true

embeddings:
  model: "text-embedding-3-small"
  dimensions: 1536

serve:
  hybrid_weights:
    vector: 0.65
    lexical: 0.35
  default_search_order:
    - ipai_odoo_ce       # Internal docs first
    - ipai_finance_ppm   # Internal modules
    - oca_*              # OCA repos
    - odoo_docs          # Official docs last
```

### Multi-source Routing

Search order determines priority:
1. **Internal documentation** (`ipai_*` sources) - checked first
2. **OCA modules** (`oca_*` sources) - checked second
3. **Odoo official** (`odoo_docs`) - checked last

This ensures internal customizations and patches are surfaced before generic docs.

## SQL Functions Reference

### rag.search_hybrid()
Hybrid retrieval combining vector similarity (65%) and lexical search (35%).

**Parameters**:
- `p_tenant_id`: Tenant UUID
- `p_query`: Search query text
- `p_query_embedding`: Query embedding vector[1536]
- `p_top_k`: Number of results (default: 12)
- `p_source_type`: Filter by source (optional)
- `p_visibility`: `public` or `internal` (optional)
- `p_doc_version`: Filter by version (optional)

**Returns**: Chunks with scores, content, metadata, citations

### rag.search_exact()
Exact/fuzzy string matching for module names, xmlids, error codes.

**Use when**: User query contains exact strings like:
- `ir.model.access.csv`
- `web.login`
- `account.move.line`
- Error codes

### rag.search_multi_source()
Multi-source routing with priority order.

**Use when**: User query should search across multiple sources in priority order.

### rag.format_citation()
Format chunk metadata into Kapa-style citation object.

## Continuous Improvement

### Track Question Quality
```sql
-- Questions with low confidence answers
SELECT
  q.question,
  a.answer,
  a.confidence_score,
  avg(v.vote) as avg_vote
FROM rag.questions q
JOIN rag.answers a ON a.question_id = q.id
LEFT JOIN rag.answer_votes v ON v.answer_id = a.id
WHERE a.confidence_score < 0.7
GROUP BY q.id, a.id
ORDER BY a.confidence_score ASC
LIMIT 20;
```

### Monitor Performance
```sql
-- Hourly performance metrics
SELECT * FROM rag.search_performance
WHERE hour > now() - interval '7 days'
ORDER BY hour DESC;
```

### Create Eval Sets
```sql
INSERT INTO rag.eval_sets (tenant_id, name, questions)
VALUES (
  'your-tenant-id',
  'Odoo 18 RLS Policies',
  '[
    {
      "question": "How do I create RLS policies in Odoo 18?",
      "expected_answer": "Use ir.rule model with domain filters...",
      "expected_citations": ["oca_account_financial_tools", "odoo_docs"]
    }
  ]'::jsonb
);
```

## Deployment Surfaces

### 1. Vercel API Endpoint
```
POST https://your-domain.vercel.app/api/ask
{
  "question": "How do I...",
  "top_k": 6,
  "visibility": "internal"
}
```

### 2. Slack Bot (Future)
```python
# slack_bot.py
import os
from slack_bolt import App
from tools.docs_crawler.api_ask import DocsAPI

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.message("ask odoo")
def handle_ask(message, say):
    question = message['text'].replace('ask odoo', '').strip()

    api = DocsAPI(...)
    result = api.ask(question)

    # Format citations as Slack blocks
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": result['answer']}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Sources:*"}}
    ]

    for citation in result['citations'][:3]:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"<{citation['url']}|{citation['section']}> ({citation['version']})"
            }
        })

    say(blocks=blocks)

app.start(port=3000)
```

### 3. Website Widget (Future)
```html
<!-- Kapa-style chat widget -->
<div id="odoo-docs-widget"></div>
<script>
  window.OdooDocsWidget.init({
    apiUrl: 'https://your-domain.vercel.app/api/ask',
    position: 'bottom-right',
    theme: 'light',
    placeholder: 'Ask about Odoo 18...'
  });
</script>
```

## Advanced Features

### Version-Specific Search
```python
# Search only Odoo 18.0 docs
result = api.ask(
    question="What's new in Odoo 18 accounting?",
    source_type="odoo_docs",
    visibility="public"
)

# Search only internal IPAI modules
result = api.ask(
    question="How does ipai_finance_ppm handle BIR deadlines?",
    source_type="ipai_finance_ppm",
    visibility="internal"
)
```

### Module API Surface Extraction
Future enhancement: Parse Python model files to extract:
- Model names (`class AccountMove(models.Model)`)
- Field definitions (`name = fields.Char(string="Name")`)
- Constraints (`_sql_constraints = [...]`)
- Security rules (from `ir.model.access.csv`)

This enables queries like:
- "What fields does account.move have?"
- "What RLS policies exist for project.project?"
- "What are the constraints on res.partner?"

## Troubleshooting

### Low search quality
1. Check embedding model consistency (`embedding_model` field)
2. Verify hybrid weights (try adjusting `p_vector_weight`/`p_lexical_weight`)
3. Check index health: `EXPLAIN ANALYZE SELECT ... FROM rag.search_hybrid(...)`

### Slow queries
1. Verify vector index exists: `\d rag.chunks` (look for `idx_chunks_ivfflat` or `idx_chunks_hnsw`)
2. Check token count: reduce `max_tokens` if chunks are too large
3. Monitor query performance: `SELECT * FROM rag.search_performance`

### Missing citations
1. Check `canonical_url` is set on documents
2. Verify `section_path` extraction during crawl
3. Check `doc_version` and `commit_sha` are populated

## Roadmap

- [ ] Automated ingestion pipeline (n8n cron job)
- [ ] Incremental crawl (webhook-triggered on GitHub push)
- [ ] Slack/Mattermost bot deployment
- [ ] Website chat widget
- [ ] Discord bot
- [ ] Module API surface extraction (models, fields, constraints, security)
- [ ] Multi-language support (detect language from query)
- [ ] Answer confidence tuning (ML model)
- [ ] A/B testing framework for retrieval strategies

## License

Part of the `odoo-ce-branding` repository. See top-level LICENSE for details.

# OpenAI Academy Prompt Packs: Crawl and Curate

> **Purpose**: Extract, catalog, and curate prompt packs from OpenAI Academy for integration into our IPAI prompt library.
>
> **Source**: https://academy.openai.com/ (prompt engineering courses and examples)
>
> **Target**: `docs/prompts/openai-academy/` artifacts

---

## Extraction Goals

1. **Discover** all published prompt packs, templates, and examples from OpenAI Academy
2. **Extract** structured data: pack name, category, use case, sample prompts, best practices
3. **Curate** into a standardized library format compatible with our prompt registry
4. **Identify Gaps** between OpenAI Academy coverage and our platform needs

---

## Extraction Schema

### Prompt Pack Entry

```json
{
  "id": "openai-academy-{slug}",
  "source": "openai-academy",
  "source_url": "https://academy.openai.com/...",
  "name": "Pack Name",
  "category": "category-slug",
  "description": "Brief description",
  "use_cases": ["use-case-1", "use-case-2"],
  "prompts": [
    {
      "name": "Prompt Name",
      "template": "The actual prompt template...",
      "variables": ["var1", "var2"],
      "example_input": {},
      "example_output": "Expected output description"
    }
  ],
  "best_practices": ["Practice 1", "Practice 2"],
  "tags": ["tag1", "tag2"],
  "extracted_at": "ISO8601 timestamp",
  "version": "1.0"
}
```

### Categories

| Category Slug | Description |
|---------------|-------------|
| `summarization` | Text summarization and condensation |
| `extraction` | Data and entity extraction |
| `generation` | Content generation and creative writing |
| `analysis` | Text analysis and evaluation |
| `classification` | Categorization and labeling |
| `conversation` | Dialog and chat patterns |
| `reasoning` | Chain-of-thought and reasoning |
| `code` | Code generation and explanation |
| `structured-output` | JSON, XML, and structured responses |
| `agents` | Agentic patterns and tool use |

---

## Extraction Process

### Phase 1: Discovery

```bash
# Run the crawler in discovery mode
python scripts/extract_openai_academy_prompt_packs.py --mode discover

# Output: docs/prompts/openai-academy/discovery_manifest.json
```

**Discovery targets**:
- Course catalog pages
- Lesson content with prompt examples
- Playground presets
- Documentation snippets
- API cookbook entries

### Phase 2: Extraction

```bash
# Run full extraction
python scripts/extract_openai_academy_prompt_packs.py --mode extract

# Output: docs/prompts/openai-academy/prompt_packs_raw.json
```

### Phase 3: Curation

```bash
# Curate into library format
python scripts/extract_openai_academy_prompt_packs.py --mode curate

# Output: docs/prompts/openai-academy/prompt_library.md
```

### Phase 4: Gap Analysis

```bash
# Compare against IPAI prompt registry
python scripts/extract_openai_academy_prompt_packs.py --mode gap-analysis

# Output: docs/prompts/openai-academy/prompt_pack_gap_report.md
```

---

## Integration with IPAI Prompt Registry

### Target Schema Alignment

Our IPAI prompt registry uses:

```yaml
# prompts/<category>/<prompt-name>.yaml
id: ipai-<category>-<name>
name: Human Readable Name
version: "1.0"
category: category-slug
description: |
  Multi-line description of what this prompt does.
template: |
  The actual prompt template with {{variables}}.
variables:
  - name: var1
    type: string
    required: true
    description: What this variable is for
input_schema:
  type: object
  properties:
    var1:
      type: string
output_format: text | json | markdown
examples:
  - input:
      var1: "example value"
    output: "Expected output"
tags:
  - tag1
  - tag2
source: openai-academy | internal | community
source_url: https://...
```

### Mapping Rules

| OpenAI Academy Field | IPAI Registry Field |
|---------------------|---------------------|
| `name` | `name` |
| `category` | `category` |
| `description` | `description` |
| `prompts[].template` | `template` |
| `prompts[].variables` | `variables` |
| `best_practices` | (append to description) |
| `use_cases` | `tags` |

---

## Output Artifacts

| File | Format | Purpose |
|------|--------|---------|
| `discovery_manifest.json` | JSON | List of discovered pages/resources |
| `prompt_packs_raw.json` | JSON | Raw extracted data before curation |
| `prompt_library.md` | Markdown | Human-readable curated library |
| `prompt_pack_gap_report.md` | Markdown | Gap analysis vs IPAI needs |
| `README.md` | Markdown | Usage and regeneration instructions |

---

## Manual Review Checklist

After automated extraction, manually verify:

- [ ] Prompt templates are complete (no truncation)
- [ ] Variables are correctly identified
- [ ] Categories are accurately assigned
- [ ] Best practices are actionable
- [ ] No proprietary/copyrighted content beyond fair use
- [ ] Source URLs are valid

---

## Refresh Schedule

| Frequency | Action |
|-----------|--------|
| Weekly | Check for new courses/content |
| Monthly | Full re-extraction and curation |
| Quarterly | Gap analysis against platform roadmap |

---

## Known Limitations

1. **Authentication**: Some OpenAI Academy content may require login
2. **Dynamic Content**: JavaScript-rendered content may need Playwright
3. **Rate Limits**: Respect robots.txt and implement polite crawling
4. **Content Changes**: Academy content may change without notice
5. **Extraction Quality**: Some prompts may be embedded in prose, requiring NLP extraction

---

## Related Resources

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [IPAI Prompt Registry](../README.md)
- [Vercel AI SDK Prompt Patterns](https://sdk.vercel.ai/docs)

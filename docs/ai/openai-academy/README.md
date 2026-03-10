# OpenAI Academy Prompt Packs

Extraction, curation, and integration of prompt engineering patterns from OpenAI Academy.

## Quick Start

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Run discovery (find available content)
python scripts/extract_openai_academy_prompt_packs.py --mode discover

# Run extraction (pull prompt data)
python scripts/extract_openai_academy_prompt_packs.py --mode extract

# Run curation (format into library)
python scripts/extract_openai_academy_prompt_packs.py --mode curate

# Run gap analysis (compare to IPAI needs)
python scripts/extract_openai_academy_prompt_packs.py --mode gap-analysis
```

## Files

| File | Purpose |
|------|---------|
| `PROMPT_PACKS_CRAWL_AND_CURATE.md` | Extraction methodology and schema |
| `prompt_packs_raw.json` | Raw extracted data (JSON) |
| `prompt_library.md` | Curated human-readable library |
| `prompt_pack_gap_report.md` | Gap analysis vs IPAI requirements |
| `README.md` | This file |

## Workflow

```
Discovery → Extraction → Curation → Gap Analysis → Integration
    ↓           ↓            ↓             ↓            ↓
manifest   raw JSON    library.md    gap_report    IPAI registry
```

## Authentication

Some OpenAI Academy content may require authentication. To use:

```bash
# Export cookie from browser (use browser dev tools)
export OPENAI_ACADEMY_COOKIE="session=..."

# Or use cookie file
python scripts/extract_openai_academy_prompt_packs.py --cookie-file cookies.txt
```

## Rate Limiting

The extractor implements polite crawling:
- 1-2 second delay between requests
- Respects robots.txt
- Caches responses to avoid re-fetching

## Output Schema

See [PROMPT_PACKS_CRAWL_AND_CURATE.md](./PROMPT_PACKS_CRAWL_AND_CURATE.md) for full schema.

## Integration with IPAI

After extraction, import prompts into IPAI registry:

```bash
# Validate extracted prompts
python scripts/validate_prompt_library.py --source openai-academy

# Import to registry
python scripts/import_prompt_library.py --source openai-academy --target prompts/
```

## Maintenance

| Schedule | Action |
|----------|--------|
| Weekly | Check for new Academy content |
| Monthly | Full re-extraction |
| Quarterly | Gap analysis refresh |

## Troubleshooting

### 403 Forbidden

OpenAI Academy may require authentication or block scrapers:
1. Use browser cookies (see Authentication above)
2. Use a different user agent
3. Try Playwright for JS-rendered content

### Empty Extraction

Content may be dynamically loaded:
1. Enable `--use-playwright` flag
2. Increase `--wait-time` for JS rendering
3. Check if content structure changed

### Truncated Prompts

Long prompts may be cut off:
1. Check source page for "show more" buttons
2. Use `--expand-all` flag
3. Manual review may be needed

## Contributing

1. Fork repository
2. Run extraction with latest Academy content
3. Review and validate outputs
4. Submit PR with updated library

## License

Extracted content is subject to OpenAI's terms of use. Use for educational and internal development purposes.

## Related

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Vercel AI SDK](https://sdk.vercel.ai/)
- [IPAI Prompt Registry](../README.md)

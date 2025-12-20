# Documentation Catalogue → Odoo CE/OCA Mapper

Automated tools for crawling external documentation sites (e.g., SAP Concur Help) and mapping their content to relevant Odoo CE 18.0 modules and OCA repositories.

## Purpose

When evaluating SaaS tools for potential Odoo replacement or feature parity analysis, this toolkit:

1. **Crawls** documentation sites recursively (same-domain, deduped, rate-limited)
2. **Catalogs** pages with metadata (title, breadcrumbs, section, word count, link graph)
3. **Maps** content to Odoo CE modules and OCA repos based on keyword rules
4. **Outputs** structured data (JSON, CSV, Markdown) for further analysis

## Components

```
tools/docs_catalog/
├── crawl_docs.py         # Recursive documentation crawler
├── odoo_map.yaml         # Keyword rules for Odoo CE/OCA mapping
├── map_to_odoo.py        # Mapping generator
└── README.md             # This file
```

## Installation

Requires Python 3.11+ with these dependencies:

```bash
pip install requests beautifulsoup4 pyyaml
```

Or add to your existing requirements file:

```txt
# tools/docs_catalog requirements
requests>=2.31.0
beautifulsoup4>=4.12.0
pyyaml>=6.0.1
```

## Usage

### Step 1: Crawl Documentation Site

```bash
python tools/docs_catalog/crawl_docs.py \
  --seed "https://help.sap.com/docs/CONCUR_EXPENSE" \
  --out "out/concur_expense" \
  --max-pages 600 \
  --delay 0.2
```

**Parameters**:
- `--seed`: Starting URL (catalogue/index page)
- `--out`: Output directory for results
- `--max-pages`: Maximum pages to crawl (default: 400)
- `--delay`: Delay between requests in seconds (default: 0.15)
- `--timeout`: HTTP timeout in seconds (default: 20)

**Outputs** (in `out/concur_expense/`):
- `catalog.json`: Structured catalogue with page metadata
- `edges.csv`: Link graph (src, dst, anchor_text)
- `catalog.md`: Human-readable outline grouped by section

**Example catalog.json entry**:
```json
{
  "url": "https://help.sap.com/docs/CONCUR_EXPENSE/expenses",
  "title": "Expense Reports | SAP Concur",
  "h1": "Expense Reports",
  "breadcrumbs": ["Concur", "Expense", "User Guide"],
  "section": "use",
  "status": 200,
  "word_count": 1543,
  "discovered_from": "https://help.sap.com/docs/CONCUR_EXPENSE"
}
```

### Step 2: Map to Odoo CE/OCA Modules

```bash
python tools/docs_catalog/map_to_odoo.py \
  --catalog "out/concur_expense/catalog.json" \
  --rules "tools/docs_catalog/odoo_map.yaml" \
  --out "out/concur_expense_odoo_map"
```

**Parameters**:
- `--catalog`: Path to catalog.json from Step 1
- `--rules`: Path to odoo_map.yaml (keyword rules)
- `--out`: Output directory for mapping results

**Outputs** (in `out/concur_expense_odoo_map/`):
- `mapping.csv`: CSV with rule, URL, title, score, matched keywords, Odoo modules, OCA repos
- `mapping.md`: Human-readable Markdown report grouped by rule

**Example mapping.md excerpt**:
```markdown
## Expense

**Odoo CE Modules**: hr_expense, hr, account, purchase

**OCA Repositories**: OCA/hr, OCA/account-financial-tools, OCA/account-invoicing, OCA/purchase-workflow

**Matched Pages**: 127

- [Expense Reports](https://help.sap.com/docs/CONCUR_EXPENSE/expenses) (score: 12, keywords: expense, expense report, reimbursement)
- [E-Receipts](https://help.sap.com/docs/CONCUR_EXPENSE/ereceipts) (score: 9, keywords: e-receipt, receipt, expense)
```

## Customizing Mapping Rules

Edit `tools/docs_catalog/odoo_map.yaml` to define your own keyword-based mappings:

```yaml
version: 1

targets:
  expense:
    odoo_ce_modules:
      - hr_expense
      - account
    oca_repos:
      - OCA/hr
      - OCA/account-financial-tools
    keywords:
      - expense
      - receipt
      - reimbursement
      - cash advance
      - per diem
```

**Scoring algorithm**:
- Exact keyword match in (title + h1 + breadcrumbs + section): +3 points
- All tokens of multi-word keyword found: +1 point
- Higher scores = stronger relevance

## Example: SAP Concur to Odoo Feature Parity

```bash
# 1. Crawl SAP Concur Expense documentation
python tools/docs_catalog/crawl_docs.py \
  --seed "https://help.sap.com/docs/CONCUR_EXPENSE" \
  --out "out/concur_expense" \
  --max-pages 600 \
  --delay 0.2

# 2. Map to Odoo CE/OCA modules
python tools/docs_catalog/map_to_odoo.py \
  --catalog "out/concur_expense/catalog.json" \
  --rules "tools/docs_catalog/odoo_map.yaml" \
  --out "out/concur_expense_odoo_map"

# 3. Review results
head -20 out/concur_expense/catalog.md
head -20 out/concur_expense_odoo_map/mapping.md
ls -lh out/concur_expense/
ls -lh out/concur_expense_odoo_map/
```

## Outputs Summary

| File | Format | Purpose |
|------|--------|---------|
| `catalog.json` | JSON | Structured catalogue for programmatic use |
| `catalog.md` | Markdown | Human-readable outline by section |
| `edges.csv` | CSV | Link graph for network analysis |
| `mapping.csv` | CSV | Full mapping with scores for filtering |
| `mapping.md` | Markdown | Top matches grouped by Odoo target |

## Integration with Odoo Development

Typical workflow after mapping:

1. **Review top-scored pages** in `mapping.md` to understand feature requirements
2. **Identify Odoo CE modules** that provide similar functionality
3. **Check OCA repositories** for enhanced/missing features
4. **Create PRDs** for custom modules to fill gaps (e.g., `ipai_expense_concur_parity`)
5. **Reference URLs** in module documentation for feature parity tracking

## Advanced Options

### Crawl Multiple Documentation Sites

```bash
for SITE in CONCUR_EXPENSE CONCUR_TRAVEL CONCUR_INVOICE; do
  python tools/docs_catalog/crawl_docs.py \
    --seed "https://help.sap.com/docs/$SITE" \
    --out "out/$(echo $SITE | tr '[:upper:]' '[:lower:]')" \
    --max-pages 400 \
    --delay 0.2
done
```

### Filter Mapping by Score Threshold

```bash
# Only show matches with score >= 6
python -c "
import csv
with open('out/concur_expense_odoo_map/mapping.csv') as f:
    r = csv.DictReader(f)
    for row in r:
        if int(row['score']) >= 6:
            print(row['url'], row['title'], row['score'])
"
```

### Generate Link Graph for Network Analysis

The `edges.csv` output can be loaded into graph analysis tools (NetworkX, Gephi) to visualize documentation structure and identify hub pages.

## Troubleshooting

**Issue**: Crawler stops early or misses pages

**Solution**: Increase `--max-pages` or check that seed URL is a catalogue/index page (not a single doc page)

---

**Issue**: Low mapping scores for relevant pages

**Solution**: Add more keywords to `odoo_map.yaml` rules or check keyword variations (singular/plural, abbreviations)

---

**Issue**: Rate limiting / 429 errors

**Solution**: Increase `--delay` parameter (e.g., `--delay 0.5` for 500ms between requests)

---

## License

Part of the `odoo-ce-branding` repository. See top-level LICENSE for details.

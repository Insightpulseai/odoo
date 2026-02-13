# Odoo EE Parity Seed (Auto-Generated)

## Overview

This seed is auto-generated weekly from the Odoo Editions comparison page.
It provides a structured catalog of all EE capabilities with placeholder fields for OCA mapping.

**Source:** https://www.odoo.com/page/editions

## Quick Start

### Regenerate Seed (Manual)

```bash
# Install dependencies
pip install beautifulsoup4 requests pyyaml

# Run generator
python scripts/gen_odoo_editions_parity_seed.py

# Verify output
python -c "
import yaml
with open('spec/parity/odoo_editions_parity_seed.yaml') as f:
    d = yaml.safe_load(f)
print(f\"Extracted {len(d['parity_seed']['rows'])} rows\")
"
```

### CI/CD

Weekly workflow: `.github/workflows/editions-parity-seed.yml`
- **Schedule:** Sundays at midnight UTC
- **Manual Trigger:** `workflow_dispatch`
- **Drift Detection:** Automatic via `git diff`

## Manual Enrichment Guide

The generated YAML includes placeholder `mapping` fields for each row:

```yaml
- area: "Finance"
  app: "Accounting"
  feature: "OCR on invoices"
  assumed_ee_only: true
  mapping:
    oca_repo: null      # TODO: Fill with OCA GitHub repo URL
    oca_module: null    # TODO: Fill with OCA module name
    ipai_module: null   # TODO: If custom bridge module needed
  confidence: 0.0       # TODO: Update to 0.0-1.0 based on match quality
  notes: "seed row (feature-level) from editions page; mapping required"
```

### Enrichment Workflow

1. **Identify EE-Only Features**: Review rows with `assumed_ee_only: true`
2. **Search OCA Modules**: Check https://github.com/OCA and `oca.lock.json`
3. **Update Mapping**: Fill in `oca_repo` and `oca_module` fields
4. **Set Confidence**:
   - `1.0`: Exact match, verified functionality
   - `0.8-0.9`: Good match, minor gaps
   - `0.5-0.7`: Partial match, significant gaps
   - `0.0-0.4`: Poor match or no equivalent
5. **Add Notes**: Document any caveats or implementation notes

### Example Enriched Row

```yaml
- area: "Finance"
  app: "Accounting"
  feature: "OCR on invoices"
  assumed_ee_only: true
  mapping:
    oca_repo: "https://github.com/OCA/account-invoicing"
    oca_module: "account_invoice_import"
    ipai_module: null
  confidence: 0.8
  notes: "OCA module provides OCR via partner integrations; requires external OCR service"
```

## Integration with Existing Parity Tracking

This seed complements `config/ee_parity/ee_parity_mapping.yml`:
- **Seed**: Exhaustive catalog (all capabilities from Editions page)
- **Mapping**: Curated implementation plans (selected priority features)

Use this seed to identify gaps in the manual mapping file.

## Data Model

### Row Structure

| Field | Type | Description |
|-------|------|-------------|
| `area` | string | Top-level section (Finance, Sales, HR, etc.) |
| `app` | string | Application name (Accounting, Invoicing, CRM, etc.) |
| `feature` | string\|null | Subfeature or null for app-level rows |
| `source_url` | string | Odoo Editions page URL |
| `evidence_text` | string\|null | Extracted feature text from page |
| `assumed_ee_only` | boolean | Heuristic hint based on keywords |
| `mapping.oca_repo` | string\|null | OCA GitHub repo URL (manual enrichment) |
| `mapping.oca_module` | string\|null | OCA module name (manual enrichment) |
| `mapping.ipai_module` | string\|null | Custom IPAI bridge module if needed |
| `confidence` | float | Match quality score (0.0-1.0) |
| `notes` | string | Free-form annotation |

### Heuristic EE-Only Keywords

Features containing these keywords are marked `assumed_ee_only: true`:
- OCR, AI, Studio, VoIP, IoT, Barcode, Shopfloor, Scheduling

**Note:** This is a heuristic hint only. Manual enrichment should verify actual availability.

## Troubleshooting

### Script Fails with Network Error

```bash
# Check network connectivity
curl -I https://www.odoo.com/page/editions

# Verify user-agent header is set (script includes this)
# If blocked, update USER_AGENT in gen_odoo_editions_parity_seed.py
```

### Output Has <20 Rows (Smoke Test Failure)

```bash
# Check if Editions page structure changed
curl https://www.odoo.com/page/editions > /tmp/editions.html
open /tmp/editions.html  # Review page structure

# Update parsing logic in extract_visible_structure() as needed
```

### YAML Syntax Errors

```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('spec/parity/odoo_editions_parity_seed.yaml'))"

# Check for special characters needing escaping
# PyYAML handles most cases automatically
```

## Maintenance

### Update Heuristic Keywords

Edit `EE_KEYWORDS` list in `scripts/gen_odoo_editions_parity_seed.py`:

```python
EE_KEYWORDS = [
    "ocr", "ai", "studio", "voip", "iot", "barcode",
    "shopfloor", "scheduling", "machine learning", "artificial intelligence",
    # Add new keywords here
]
```

### Improve Parsing Logic

The `extract_visible_structure()` function uses simple heuristics:
- **Area detection**: All caps or title case + short
- **App detection**: Title case + medium length
- **Feature detection**: Starts with bullet or lowercase

Adjust these heuristics if extraction quality degrades after Odoo page updates.

## Version History

- **v1** (2026-02-13): Initial implementation with text-based parsing
  - BeautifulSoup4 HTML extraction
  - area → app → feature data model
  - Heuristic EE-only detection
  - Placeholder mapping fields for manual enrichment

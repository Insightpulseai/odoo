# Figma Community Toolkit for Data Engineering UI

Curated collection of Figma Community assets optimized for building Databricks-style Data Engineering workspaces.

## Purpose

Accelerate design-to-dev handoff for:
- Notebook + table hybrid interfaces
- Interactive charts (heatmaps, bar charts, line graphs)
- Pipeline/workflow builders
- Data catalog/governance UI
- Shareable dashboards

## Structure

```
figma/community/
├── manifest.json    # Full metadata + scoring for all curated items
├── shortlist.csv    # Quick-reference ranked list
└── README.md        # This file
```

## Scoring Rubric (0-100)

| Criteria | Max Points | Description |
|----------|------------|-------------|
| Relevance | 30 | Data Engineering UI fit (notebooks, tables, charts, pipelines) |
| Adoption | 20 | Installs, likes, publisher reputation, update recency |
| Token Readiness | 15 | Uses Variables API, consistent styles, naming |
| Handoff Readiness | 15 | Components, variants, auto-layout, Dev Mode support |
| Extensibility | 10 | Adaptable to our design tokens + Code Connect |
| License | 10 | Permissive or clearly stated usage terms |

## Target Use Cases

### Templates & UI Kits
- Dashboard frameworks for analytics
- Table/grid components with sorting, filtering
- Notebook cell layouts (code, markdown, output)
- Form builders for data input

### Plugins
- **Tokens Studio** - Design token management
- **Table Generator** - Quick table creation
- **Chart** - Data visualization components
- **Design Lint** - Consistency checking
- **JSON to Figma** - Data-driven design

### Libraries
- Enterprise dashboard systems
- Data visualization component sets
- Icon libraries (data/analytics themed)

## Integration with Design Sync

Items in this toolkit should be:
1. Compatible with our `figma/tokens/` design token schema
2. Mappable via Code Connect (`figma/connect/`)
3. Documented with component naming conventions

## Refresh Cadence

Monthly review recommended:
1. Re-run target queries on Figma Community
2. Score new items against rubric
3. Update `manifest.json` and `shortlist.csv`
4. Archive deprecated items

## Usage

```bash
# View current shortlist
cat figma/community/shortlist.csv | column -t -s,

# Parse manifest programmatically
node -e "console.log(JSON.parse(require('fs').readFileSync('figma/community/manifest.json')).items.length)"
```

## Contributing

To add items:
1. Search Figma Community using target queries
2. Score against rubric
3. Add to `manifest.json` with full metadata
4. Update `shortlist.csv` with summary row
5. Note any licensing concerns

---

*Last curated: 2026-01-25*

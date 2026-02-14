# Figma Design Sync

Co-located namespace for Figma Tokens + Code Connect integration.

## Structure

```
figma/
├── tokens/              # Exported Figma Variables (auto-generated)
│   ├── variables.local.json   # Raw API response
│   └── tokens.json            # Flattened token map
├── connect/             # Code Connect mappings (*.figma.tsx)
│   └── *.figma.tsx      # Component-to-Figma mappings
├── community/           # Curated Figma Community assets
│   ├── manifest.json    # Full metadata + scoring
│   ├── shortlist.csv    # Quick reference list
│   └── README.md        # Curation guidelines
└── README.md            # This file
```

## Quick Start

### Prerequisites

```bash
export FIGMA_ACCESS_TOKEN="figd_xxxxxxxxxxxxx"
export FIGMA_FILE_KEY="your_file_key_here"
```

### Run Design Sync

```bash
./scripts/design-sync.sh
```

This will:
1. Export Figma Variables to `figma/tokens/`
2. Publish Code Connect mappings from `figma/connect/`

### One-Time Code Connect Setup

```bash
# Install CLI
npm install --global @figma/code-connect@latest

# Interactive setup (generates figma.config.json + mappings)
npx figma connect --token="$FIGMA_ACCESS_TOKEN"

# When prompted for output directory: ./figma/connect

# Publish mappings
npx figma connect publish --token="$FIGMA_ACCESS_TOKEN"
```

## CI/CD

The `design-sync.yml` workflow runs automatically on:
- Manual trigger (`workflow_dispatch`)
- Push to `main` affecting `figma/**` or sync scripts

Required secrets:
- `FIGMA_ACCESS_TOKEN` - Figma Personal Access Token
- `FIGMA_FILE_KEY` - Target Figma file key

## Verification

```bash
# Check tokens exported
ls -la figma/tokens/
test -f figma/tokens/tokens.json && echo "OK"

# Validate JSON
node -e "JSON.parse(require('fs').readFileSync('figma/tokens/tokens.json','utf8')); console.log('tokens.json OK')"
```

## Requirements

- **Figma Access**: Dev seat or Full seat on paid plan (Variables API requires this)
- **Node.js**: >= 18.0.0
- **Secrets**: `FIGMA_ACCESS_TOKEN`, `FIGMA_FILE_KEY`

## Related

- [Figma Variables API](https://developers.figma.com/docs/rest-api/variables-endpoints/)
- [Code Connect Quickstart](https://developers.figma.com/docs/code-connect/quickstart-guide/)
- [Design Tokens W3C](https://design-tokens.github.io/community-group/format/)

---

*Last updated: 2026-01-25*

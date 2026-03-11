# Visio-DrawIO Export Skill

Export Visio diagrams (.vsdx) to DrawIO format with PNG/SVG previews, validation, and visual regression testing.

## Features

- **Visio Import**: Parse .vsdx and .vsd files
- **DrawIO Conversion**: Preserve layers, styles, and connections
- **Image Export**: Generate PNG and SVG previews (headless)
- **Validation**: Check diagram structure and content
- **Visual Regression**: Compare diagrams against baselines
- **Control Room Integration**: Submit as orchestrated job

## Quick Start

### CLI Usage

```bash
# Convert single file
visio-drawio-export \
  --input diagram.vsdx \
  --outdir artifacts/diagrams \
  --formats png,svg

# Batch convert with validation
visio-drawio-export \
  --input-glob "docs/**/*.vsdx" \
  --outdir artifacts/diagrams \
  --validate strict

# Visual regression
visio-drawio-export \
  --diff \
  --baseline artifacts/baselines \
  --current artifacts/diagrams \
  --diff-threshold 0.003
```

### Docker Usage

```bash
# Build image
docker build -t visio-drawio-export:ci skills/visio-drawio-export/docker

# Run export
docker run --rm -v "$PWD:/work" visio-drawio-export:ci \
  --input-glob "**/*.vsdx" \
  --outdir "artifacts/diagrams" \
  --formats "png,svg" \
  --validate strict
```

### Control Room Integration

Submit as a diagram export job:

```bash
curl -X POST http://localhost:8789/api/v1/jobs/run \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "diagram_export",
    "spec": {
      "text": "Export architecture diagrams",
      "inputs": {
        "source_glob": "docs/**/*.vsdx",
        "output_dir": "artifacts/diagrams",
        "formats": ["png", "svg"]
      }
    },
    "created_by": "ci-pipeline"
  }'
```

## GitHub Actions

Add to your workflow:

```yaml
- name: Export diagrams
  uses: ./.github/actions/visio-drawio-export
  with:
    input-glob: "docs/**/*.vsdx"
    output-dir: "artifacts/diagrams"
    formats: "png,svg"
    validate: "strict"
```

Or use the pre-built workflow in `.github/workflows/diagrams-qa.yml`.

## Visual Regression

Visual regression compares exported images against baselines to detect unintended changes.

### Setup Baselines

```bash
# Export current diagrams as baselines
visio-drawio-export \
  --input-glob "docs/**/*.vsdx" \
  --outdir artifacts/baselines \
  --formats png
```

### Run Comparison

```bash
# Compare against baselines (fails if diff > 0.3%)
visio-drawio-export \
  --diff \
  --baseline artifacts/baselines \
  --current artifacts/diagrams \
  --diff-threshold 0.003
```

### Threshold Guidelines

| Threshold | Use Case |
|-----------|----------|
| 0.001 | Pixel-perfect match |
| 0.003 | Allow minor anti-aliasing (recommended) |
| 0.01 | Allow small color variations |
| 0.05 | Allow layout adjustments |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DRAWIO_HEADLESS` | Enable headless mode | `true` |
| `DRAWIO_SCALE` | Export scale factor | `2.0` |
| `DIFF_THRESHOLD` | Visual diff threshold | `0.003` |

### Output Structure

```
artifacts/diagrams/
├── manifest.json           # Export manifest
├── diagram1.drawio         # DrawIO XML
├── diagram1.png            # PNG preview
├── diagram1.svg            # SVG preview
└── diagram2/
    ├── page-0.png
    ├── page-1.png
    └── ...
```

## Validation

Strict validation checks:

- Valid DrawIO XML structure
- Minimum shape count (configurable)
- Connector validity
- Layer structure
- Page size limits

```bash
visio-drawio-export --validate strict --min-shapes 5
```

## Development

### Prerequisites

- Node.js 18+
- Docker (for headless DrawIO)
- drawio-desktop (optional, for local development)

### Build

```bash
cd skills/visio-drawio-export
npm install
npm run build
```

### Test

```bash
npm test
npm run test:visual  # Visual regression tests
```

## License

MIT - See LICENSE file

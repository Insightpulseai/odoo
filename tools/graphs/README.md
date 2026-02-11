# Graph Generation Tooling

Interactive HTML-based graph visualization for the Odoo repository.

## Overview

Two graph types available:

1. **Schema ERD** - Database structure visualization (357 Odoo models, 288 tables)
2. **Knowledge Graph** - Documentation and spec relationship mapping (318+ nodes)

Both graphs feature:
- ✅ Interactive pan/zoom controls
- ✅ Filter/search functionality
- ✅ No external dependencies (vanilla JavaScript)
- ✅ One-command generation

## Prerequisites

**Required:**
- **Graphviz** (`dot` command)

**Install:**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Verify installation
dot -V
```

**Already available:**
- Python 3.11+ (required by Odoo 19)
- Standard library only (no pip installs)

## Quick Start

### Generate Both Graphs
```bash
./tools/graphs/generate_all.sh
```

Opens both viewers in your browser automatically.

### Generate Schema ERD Only
```bash
./tools/graphs/generate_schema_erd.sh
```

**With filters:**
```bash
# IPAI modules only (80+ custom tables)
./tools/graphs/generate_schema_erd.sh --filter ipai_

# Specific prefix
./tools/graphs/generate_schema_erd.sh --filter account_
```

### Generate Knowledge Graph Only
```bash
./tools/graphs/generate_knowledge_graph.sh
```

## Output Files

All outputs are in `out/graphs/` (gitignored):

```
out/graphs/
├── schema/
│   ├── index.html              # Interactive HTML viewer
│   ├── erd_full.svg            # All 288 tables
│   ├── erd_ipai.svg            # IPAI modules only
│   └── erd_full.png            # PNG export (optional)
└── knowledge/
    ├── index.html              # Interactive HTML viewer
    ├── knowledge_graph.dot     # Graphviz DOT format
    ├── knowledge_graph.svg     # Rendered graph
    └── knowledge_graph.png     # PNG export
```

## Features

### Schema ERD Viewer

**Controls:**
- **All Tables** - Full schema (288 tables)
- **IPAI Modules** - Custom modules only (80+ tables)
- **Core Only** - Odoo core tables (exclude IPAI)
- **Search** - Find tables by name
- **Zoom** - Mouse wheel or +/− buttons
- **Pan** - Click and drag

**Data source:**
- Leverages existing `scripts/generate_erd_graphviz.py` (295 lines)
- Uses `docs/data-model/ODOO_CANONICAL_SCHEMA.dbml` (132KB schema)

### Knowledge Graph Viewer

**Controls:**
- **All Nodes** - Complete graph (318+ nodes)
- **Repo** - Repository structure nodes
- **Specs** - Spec bundle nodes (32 bundles)
- **Modules** - Odoo module nodes (43 IPAI modules)
- **Workflows** - GitHub Actions workflows (153 workflows)
- **Search** - Find nodes by ID/name
- **Zoom/Pan** - Same as ERD viewer

**Data sources:**
- `docs/knowledge/graph_seed.json` - 318 pre-structured nodes
- `docs/*.md` - 690 markdown files with internal links
- `spec/*.md` - 256 markdown files (32 spec bundles)

**Node types:**
- `Repo` - Repository structure (blue)
- `SpecBundle` - Feature specifications (orange)
- `Module` - Odoo modules (purple)
- `Workflow` - CI/CD workflows (green)
- `Script` - Automation scripts (pink)
- `Doc` - Documentation files (lime)
- `Service` - External services (teal)
- `Integration` - Integration points (yellow)

## Performance

**Schema ERD:**
- Input: 357 Odoo models, 288 tables
- Rendering time: ~5-10 seconds
- Output SVG: ~900KB
- HTML viewer: instant load, smooth interaction

**Knowledge Graph:**
- Input: 318 nodes + 946 markdown files
- Markdown parsing: ~2-3 seconds
- Estimated edges: 500-1000 (from markdown links)
- Rendering time: ~3-5 seconds
- Output SVG: ~200-400KB

**Total execution time:** ~15 seconds for both graphs

## Troubleshooting

### Graphviz not found
```
ERROR: Graphviz 'dot' command not found
```

**Solution:**
```bash
brew install graphviz  # macOS
sudo apt-get install graphviz  # Ubuntu
```

### SVG generation failed
```
ERROR: SVG generation failed
```

**Possible causes:**
1. Database not running (for schema ERD)
2. Graph too large (memory issue)
3. Invalid DOT syntax

**Debug:**
```bash
# Check DOT file directly
cat out/graphs/knowledge/knowledge_graph.dot | dot -Tsvg > test.svg

# Reduce graph size
./tools/graphs/generate_schema_erd.sh --filter ipai_
```

### HTML viewer blank

**Possible causes:**
1. SVG file path incorrect
2. Browser security restrictions (file:// protocol)

**Solution:**
```bash
# Verify SVG exists
ls -lh out/graphs/schema/*.svg
ls -lh out/graphs/knowledge/*.svg

# Open directly
open out/graphs/schema/erd_full.svg
```

### Pan/zoom not working

**Possible causes:**
1. JavaScript disabled in browser
2. SVG viewBox missing

**Solution:**
- Enable JavaScript in browser settings
- Regenerate graphs (should auto-fix viewBox)

## Architecture

### File Structure

```
tools/graphs/
├── generate_schema_erd.sh          # ERD wrapper (60 lines)
├── generate_knowledge_graph.py     # Knowledge graph generator (250 lines)
├── generate_knowledge_graph.sh     # Knowledge graph wrapper (40 lines)
├── generate_all.sh                 # Run both generators (30 lines)
├── README.md                       # This file (80 lines)
├── lib/
│   └── pan_zoom.js                # SVG zoom/pan controller (50 lines)
└── templates/
    ├── erd_viewer.html            # ERD HTML viewer (120 lines)
    └── knowledge_viewer.html      # Knowledge graph viewer (150 lines)
```

### How It Works

**Schema ERD:**
1. Wrapper script checks dependencies (Graphviz)
2. Runs existing `scripts/generate_erd_graphviz.py --format svg`
3. Copies SVG to `out/graphs/schema/`
4. Generates HTML wrapper from template
5. Opens in browser

**Knowledge Graph:**
1. Python generator loads `docs/knowledge/graph_seed.json`
2. Scans all markdown files for internal links `[text](path.md)`
3. Builds Graphviz DOT with clustering by node type
4. Renders to SVG/PNG via Graphviz
5. Shell wrapper generates HTML viewer
6. Opens in browser

## Advanced Usage

### Custom Filters (Schema ERD)

Filter by any table prefix:
```bash
./tools/graphs/generate_schema_erd.sh --filter account_
./tools/graphs/generate_schema_erd.sh --filter stock_
./tools/graphs/generate_schema_erd.sh --filter sale_
```

### Export PNG (High Resolution)

Both generators create PNG exports automatically:
```bash
# Outputs are in:
out/graphs/schema/erd_full.png
out/graphs/knowledge/knowledge_graph.png
```

### View DOT Source

```bash
# Knowledge graph DOT file
cat out/graphs/knowledge/knowledge_graph.dot

# Manually render with custom options
dot -Tpng -Gdpi=300 out/graphs/knowledge/knowledge_graph.dot -o high_res.png
```

## Integration with CI/CD

**Existing workflow:**
- `.github/workflows/erd-docs.yml` - Auto-generates ERD on schema changes

**Future enhancement:**
- Add knowledge graph generation to CI
- Publish HTML viewers as GitHub Pages
- Auto-update on doc/spec changes

## Credits

**Leverages existing infrastructure:**
- `scripts/generate_erd_graphviz.py` - ERD generator (295 lines, unchanged)
- `scripts/generate_odoo_dbml.py` - Model collection logic
- `docs/knowledge/graph_seed.json` - Knowledge graph seed data (318 nodes)

**New additions (~700 lines total):**
- HTML viewers with pan/zoom controls
- Knowledge graph generator
- Shell wrapper scripts
- This documentation

## Support

**Issues:**
- File bugs in GitHub Issues with `[graphs]` prefix
- Include error messages and system info (OS, Graphviz version)

**Questions:**
- Check this README first
- Review existing scripts for examples
- Consult SuperClaude framework docs

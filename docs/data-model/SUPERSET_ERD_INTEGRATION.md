# Superset ERD Integration Guide

This document describes how to display auto-generated ERD diagrams in Apache Superset dashboards.

## Overview

ERD diagrams are automatically generated via CI/CD and can be embedded in Superset dashboards using one of these methods:

1. **Direct URL embedding** (recommended) - Link to hosted SVG/PNG
2. **Supabase Storage** - Store in storage bucket, embed via URL
3. **GitHub Pages** - Host on gh-pages branch

## Generated Artifacts

| File | Format | Description |
|------|--------|-------------|
| `ODOO_ERD.svg` | SVG | Full ERD (scalable) |
| `ODOO_ERD.png` | PNG | Full ERD (raster) |
| `ODOO_ERD_ipai.svg` | SVG | IPAI modules only |
| `ODOO_ERD_ipai.png` | PNG | IPAI modules only |
| `ODOO_ERD.dot` | DOT | Graphviz source |
| `ODOO_ERD.mmd` | Mermaid | Mermaid diagram |
| `ODOO_ERD.puml` | PlantUML | PlantUML diagram |

## Method 1: GitHub Raw URL (Simplest)

Embed using the raw GitHub URL in a Superset Markdown chart:

```markdown
## Database ERD

![ERD](https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD.svg)
```

Or for the IPAI-only view:

```markdown
## IPAI Modules ERD

![IPAI ERD](https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD_ipai.svg)
```

## Method 2: GitHub Pages

If GitHub Pages is enabled on the `gh-pages` branch:

```markdown
<img src="https://jgtolentino.github.io/odoo-ce/erd/diagrams/summary/relationships.real.large.svg"
     style="width:100%; max-width:2000px;" />
```

## Method 3: Supabase Storage

### Setup

1. Create a storage bucket named `erd` in Supabase
2. Configure CI to upload artifacts after generation:

```yaml
# In .github/workflows/erd-graphviz.yml
- name: Upload to Supabase Storage
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
  run: |
    curl -X PUT \
      "${SUPABASE_URL}/storage/v1/object/erd/latest.svg" \
      -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
      -H "Content-Type: image/svg+xml" \
      --data-binary @docs/data-model/ODOO_ERD.svg
```

### Embed in Superset

```markdown
<img src="https://spdtwktxdalcfigzeqrz.supabase.co/storage/v1/object/public/erd/latest.svg"
     style="width:100%; max-width:2000px;" />
```

## Method 4: Supabase Edge Function

For more control (caching, auth), deploy an Edge Function:

### Deploy Function

```bash
supabase functions deploy serve-erd --project-ref spdtwktxdalcfigzeqrz
```

### Function Code (`supabase/functions/serve-erd/index.ts`)

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req: Request) => {
  const url = new URL(req.url);
  const format = url.searchParams.get("format") || "svg";
  const filter = url.searchParams.get("filter") || "";

  const filename = filter ? `ODOO_ERD_${filter}.${format}` : `ODOO_ERD.${format}`;

  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const { data, error } = await supabase.storage
    .from("erd")
    .download(filename);

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 404,
      headers: { "Content-Type": "application/json" }
    });
  }

  const contentType = format === "svg" ? "image/svg+xml" : "image/png";

  return new Response(data, {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=3600",
      "Access-Control-Allow-Origin": "*"
    }
  });
});
```

### Embed via Edge Function

```markdown
<img src="https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/serve-erd?format=svg"
     style="width:100%; max-width:2000px;" />
```

## Creating a Superset Dashboard

1. **Navigate to Superset** > Charts > + Chart
2. Select **Markdown** chart type
3. Add the following markdown:

```markdown
# Database Entity Relationship Diagram

> Auto-updated on every model change via CI/CD

## Full ERD

<img src="https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD.svg"
     alt="Full ERD"
     style="width:100%; max-height:800px; object-fit:contain;" />

## IPAI Modules Only

<img src="https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/docs/data-model/ODOO_ERD_ipai.svg"
     alt="IPAI ERD"
     style="width:100%; max-height:600px; object-fit:contain;" />

---

*Last generated: Check [ODOO_MODEL_INDEX.json](https://github.com/jgtolentino/odoo-ce/blob/main/docs/data-model/ODOO_MODEL_INDEX.json) for model count*
```

4. Save and add to a dashboard named **"Database ERD"**

## Automatic Updates

The ERD is regenerated automatically when:

- Model files change in `addons/ipai/**/models/**`
- Scripts change in `scripts/generate_*.py`
- Migrations change in `db/migrations/**`
- Manual trigger via workflow_dispatch

## Viewing Locally

```bash
# Generate all formats
python scripts/generate_erd_graphviz.py --format all

# Open SVG in browser
open docs/data-model/ODOO_ERD.svg

# Or use a Mermaid viewer for .mmd files
```

## Troubleshooting

### SVG not displaying in Superset

- Ensure the URL is publicly accessible
- Check CORS headers if using Edge Function
- Try PNG format as fallback

### ERD too large

- Use `--filter ipai_` to generate module-specific ERDs
- Use `--max-columns 10` to limit column display
- Use `--no-columns` for a simpler view

### Graphviz errors

- Install Graphviz: `apt-get install graphviz` or `brew install graphviz`
- Check DOT syntax: `dot -Tsvg -O file.dot`

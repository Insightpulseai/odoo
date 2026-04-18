# Canvas & Artifact Preview Architecture

> ChatGPT-style canvas and artifact preview on Azure using existing IPAI services.
> No new Azure services needed — assembles the experience from existing estate.

---

## Problem Statement

Users need to see AI-generated artifacts (documents, charts, tables, code, images) rendered live alongside the conversation — not as raw text dumps. This requires a three-surface workspace: chat, editable canvas, and live preview.

---

## Service Mapping (Existing IPAI Resources)

| Role | Azure Service | IPAI Resource | Status |
|------|--------------|---------------|--------|
| **Frontend shell** | ACA (or Static Web Apps) | `ipai-website` or new SWA | Exists |
| **Agent backend** | Container Apps | `ipai-odoo-dev` / `ipai-prismalab` | Exists |
| **Model inference** | Azure AI Foundry | `ipai-copilot-resource` | Exists |
| **Real-time streaming** | SignalR | `sigr-ipai-dev-sea` | Exists |
| **Artifact storage** | Storage Account | `stdevipai` | Exists |
| **Grounding/RAG** | AI Search | `srch-ipai-dev-sea` | Exists |
| **Telemetry** | App Insights | `appi-ipai-dev` | Exists |

**Note:** Web PubSub is the recommended service for new builds, but SignalR (`sigr-ipai-dev-sea`) is already provisioned and supports the same token streaming pattern. Use what exists.

---

## Artifact Object Model

```yaml
artifact:
  id: "art_20260418_001"
  type: "document"          # document | html_app | chart | table | image | spreadsheet
  title: "TBWA Q1 Project Cost Estimate"
  created_by: "pulser"
  created_at: "2026-04-18T20:00:00Z"
  version: 3

  source:
    format: "markdown"      # markdown | json | html | python | yaml
    uri: "blob://stdevipai/artifacts/art_001/source.md"

  preview:
    format: "html"
    uri: "blob://stdevipai/artifacts/art_001/preview.html"

  exports:
    pdf: "blob://stdevipai/artifacts/art_001/export.pdf"
    docx: "blob://stdevipai/artifacts/art_001/export.docx"

  metadata:
    conversation_id: "conv_456"
    odoo_record: "sale.order,42"     # linked Odoo record if applicable
    confidence: 0.92
    needs_review: false
```

---

## Preview Rendering Lifecycle

```
1. User sends prompt
     │
2. Agent generates artifact source (markdown/JSON/HTML)
     │
3. Source saved to blob storage
     │
4. Preview renderer converts source → rendered HTML
     │
5. Preview pushed to client via SignalR/WebPubSub
     │
6. Client renders in right-side preview panel
     │
7. User edits source → re-render → updated preview
     │
8. User exports → backend generates PDF/DOCX/XLSX
```

---

## Artifact Types

### Document (proposals, reports, manuscripts)
- Source: Markdown
- Preview: Rendered HTML
- Export: PDF, DOCX
- Use: TBWA project cost estimates, PrismaLab manuscripts, SOAs

### HTML App (interactive tools, calculators)
- Source: HTML + JS
- Preview: Sandboxed iframe
- Export: ZIP, hosted URL
- Use: PrismaLab free tools, interactive dashboards

### Chart / Table (analytics, forest plots)
- Source: JSON spec (Vega-Lite, Chart.js, or custom)
- Preview: Rendered SVG/Canvas
- Export: PNG (300 DPI), SVG, CSV (data)
- Use: PrismaLab forest plots, TBWA profitability charts

### Spreadsheet Grid (data extraction, rate cards)
- Source: JSON (rows × columns)
- Preview: Client-side grid renderer
- Export: XLSX, CSV
- Use: TBWA rate card, data extraction tables, BIR forms

### Image (medical imaging, diagrams)
- Source: Original image + analysis JSON
- Preview: Annotated image overlay
- Export: PNG, SVG (annotations)
- Use: PrismaLab medical image analysis, PRISMA flow diagrams

---

## Real-Time Event Model

Using SignalR (`sigr-ipai-dev-sea`) or Web PubSub:

```
Channels:
  session/{id}/tokens      → streaming LLM output tokens
  session/{id}/status      → agent status (thinking, generating, done)
  session/{id}/preview     → preview update events (new version available)
  session/{id}/artifacts   → artifact lifecycle events (created, updated, exported)
```

### Event Payloads

```json
// Token stream
{"channel": "session/123/tokens", "data": {"token": "The ", "index": 42}}

// Status update
{"channel": "session/123/status", "data": {"state": "generating", "artifact_id": "art_001"}}

// Preview ready
{"channel": "session/123/preview", "data": {"artifact_id": "art_001", "version": 3, "preview_uri": "blob://..."}}

// Artifact exported
{"channel": "session/123/artifacts", "data": {"artifact_id": "art_001", "export": "pdf", "uri": "blob://..."}}
```

---

## 3-Pane UI Layout

```
┌────────────────────────────────────────────────────────────────┐
│  InsightPulseAI Workspace                                      │
├──────────┬──────────────────────────┬──────────────────────────┤
│          │                          │                          │
│  RAIL    │  CANVAS                  │  PREVIEW                 │
│          │                          │                          │
│  Chat    │  Editable source         │  Live rendered output    │
│  history │  (markdown, JSON, code)  │  (HTML, PDF, chart)      │
│          │                          │                          │
│  Files   │  ┌──────────────────┐    │  ┌──────────────────┐    │
│  list    │  │ ## Project Cost  │    │  │ ┌────────────┐   │    │
│          │  │                  │    │  │ │ TBWA\SMP   │   │    │
│  Runs    │  │ | Item | Rate | │    │  │ │ Project    │   │    │
│  status  │  │ | Studio | 93K │    │  │ │ Cost Est.  │   │    │
│          │  │ | Crew  | 74K │    │  │ │            │   │    │
│  Version │  │ | Post  | 46K │    │  │ │ ₱407,484   │   │    │
│  history │  │                  │    │  │ └────────────┘   │    │
│          │  └──────────────────┘    │  └──────────────────┘    │
│          │                          │                          │
│          │  [Save] [Version] [Undo] │  [Export PDF] [DOCX]     │
│          │                          │  [Share Link]            │
└──────────┴──────────────────────────┴──────────────────────────┘
```

---

## APIs

### Create Artifact
```
POST /api/artifacts
Body: { type, title, source_content, conversation_id }
Returns: { artifact_id, preview_uri }
```

### Update Artifact Source
```
PUT /api/artifacts/{id}/source
Body: { content, format }
Returns: { version, preview_uri }
Triggers: re-render → SignalR preview event
```

### Render Preview
```
POST /api/artifacts/{id}/render
Returns: { preview_uri, format }
```

### Stream Run Events
```
WS /api/sessions/{id}/stream
Protocol: SignalR or WebSocket
Events: tokens, status, preview, artifacts
```

### Export Artifact
```
POST /api/artifacts/{id}/export
Body: { format: "pdf" | "docx" | "xlsx" | "png" }
Returns: { export_uri, size_bytes }
```

---

## Security & Sandboxing

| Boundary | Control |
|----------|---------|
| HTML preview iframe | `sandbox="allow-scripts"` — no same-origin access |
| Artifact storage | SAS tokens with 1-hour expiry for preview/export URIs |
| User isolation | Artifacts scoped to conversation → user → tenant |
| Export generation | Server-side only (python-docx, weasyprint, matplotlib) |
| SignalR auth | Entra ID token required for channel subscription |

---

## Implementation Phases

### Phase 1: Document Preview (MVP)
- Markdown source → HTML preview
- PDF/DOCX export
- Used for: TBWA cost estimates, PrismaLab manuscripts

### Phase 2: Chart/Table Preview
- JSON spec → SVG/Canvas chart
- Used for: Forest plots, profitability dashboards

### Phase 3: Interactive HTML Preview
- HTML+JS in sandboxed iframe
- Used for: PrismaLab free tools, calculators

### Phase 4: Real-Time Streaming
- SignalR token streaming
- Live preview updates during generation

---

## What's NOT in V1

- AKS / VM-based rendering
- Collaborative multi-user editing (Google Docs-style)
- Version diffing UI
- Custom template designer
- Embedded spreadsheet editor (use export → Excel instead)

---

*Architecture: Azure-native, repo-first, assembled from existing 63-resource estate*
*Last updated: 2026-04-18*

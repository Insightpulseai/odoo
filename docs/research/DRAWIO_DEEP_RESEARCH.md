# draw.io Deep Research Report

**Date**: 2026-03-07
**Context**: Platform evaluation for InsightPulse AI stack — diagramming, BPM modeling, process documentation
**Comparison**: draw.io vs SAP Signavio

---

## 1. Company & History

| Detail | Value |
|--------|-------|
| **Legal Name** | draw.io Ltd (formerly JGraph Ltd, renamed Sep 2025) |
| **Company #** | 04051179 (England) |
| **HQ** | Artisans' House, 7 Queensbridge, NN4 7BF, Northampton, England |
| **Swiss Entity** | draw.io AG, Altenhofstrasse 45, 8008 Zurich |
| **Founded** | 2000 (as Pimuzar Limited) |
| **Key People** | David Benson (co-founder), Gaudenz Alder (mxGraph creator, ETH Zurich) |
| **Origin** | JGraph (Java, 2000) -> mxGraph (JavaScript/SVG, 2006) -> Diagramly (2011) -> draw.io (2012) |

### Business Model

- **Core app is 100% free** — no login, no registration, no license required
- Revenue comes from **Atlassian Marketplace** (Confluence + Jira integrations)
- Atlassian marketplace published by **Seibert Group** (400+ employees, largest Atlassian partner)
- draw.io is the **#1 rated diagramming app** on Atlassian Marketplace with more installs than all other native Confluence diagramming apps combined
- Philosophy: "Provide free, high quality diagramming software for everyone" — disrupt the $1B+ diagramming market by eliminating artificial scarcity
- No vendor lock-in: diagram files are open XML, always editable for free
- Bootstrapped and profitable — no VC funding
- License: Apache 2.0 (briefly modified Aug-Dec 2024 to restrict Atlassian competitors, then reverted)

### Sources
- [About draw.io](https://www.drawio.com/about)
- [diagrams.net - Wikipedia](https://en.wikipedia.org/wiki/Diagrams.net)
- [draw.io Ltd - UK Companies House](https://find-and-update.company-information.service.gov.uk/company/04051179)

---

## 2. Technical Architecture

### Rendering Engine
- **Client-side JavaScript** editor built on the mxGraph library (now open-sourced under Apache License)
- Renders using **SVG** and **HTML5 Canvas**
- Runs entirely in the browser — no server-side processing for diagram editing
- Server-side components only needed for: PDF export, image conversion, .vsdx export

### File Format
- Native format: `.drawio` (compressed XML) or `.drawio.xml` (uncompressed)
- Can also save as `.drawio.svg` (SVG with embedded diagram data) or `.drawio.png` (PNG with embedded diagram data)
- XML schema has been stable since 2005 — files created in 2005 load in today's app
- Backward compatibility is a core promise

### Storage Options
draw.io does **not** store your data — you choose where:

| Storage | Method |
|---------|--------|
| **Local device** | Save/open files directly |
| **Google Drive** | OAuth integration |
| **OneDrive / SharePoint** | OAuth integration |
| **GitHub** | Direct repository integration |
| **GitLab** | Direct repository integration |
| **Dropbox** | OAuth integration |
| **Confluence / Jira** | Atlassian app (macros) |
| **Notion** | Chrome extension |
| **Plane.so** | Native integration |
| **Self-hosted server** | Docker deployment |

---

## 3. Security & Privacy

### Privacy-First Architecture
- **Zero data access**: draw.io cannot see, access, or store your diagram data
- No user accounts, no tracking cookies for the free web app
- All processing happens client-side in the browser
- Server-side export (PDF/image) processes data transiently — not stored

### Compliance
- GDPR compliant (EU data residency via user-controlled storage)
- Enables **ISO 27000, 27001, 27002** compliance (data never leaves your infra)
- SOC 2 compliance posture for Atlassian marketplace apps
- **Atlassian Cloud Fortified** — only diagramming app to achieve this
- **draw.io Zero Egress** edition on Forge — zero data egress for maximum security
- Data Center approved for Atlassian (enterprise security reviews available)
- Advanced Edition supports "lockdown" mode — disables all communication except browser-to-storage
- Data Protection Officer appointed under UK GDPR / Data Protection Act 2018
- IP + device info in access logs cyclically overwritten every 10 days

### AI Privacy Note
- AI diagram generation (Generate tool) sends data to the selected LLM provider (OpenAI, Google, Anthropic)
- Users can configure which LLM backend to use or disable AI entirely
- The `create` and `update` actions share diagram data with the AI provider; `createPublic` uses only the text prompt

---

## 4. Integrations

### Tier 1 — Native/Official

| Platform | Integration Type | Details |
|----------|-----------------|---------|
| **Google Drive / Workspace** | OAuth storage | Real-time collaboration with shared cursors |
| **Microsoft OneDrive / SharePoint** | OAuth storage | Real-time collaboration with shared cursors |
| **Microsoft Teams** | App | Embedded diagramming |
| **Atlassian Confluence** | Marketplace app | #1 rated, Cloud + Data Center + Server |
| **Atlassian Jira** | Marketplace app | Embed diagrams in issues |
| **GitHub** | Direct mode | `app.diagrams.net/?mode=github` |
| **GitLab** | Wiki integration | Built into GitLab 15.10+ wiki editor |
| **Dropbox** | OAuth storage | File sync |
| **Notion** | Chrome extension | Embed/edit in Notion pages |
| **Plane.so** | Native integration | `/draw` slash command in pages |

### Tier 2 — Desktop, IDE & AI Agents

| Platform | Type |
|----------|------|
| **Desktop app** | Windows, macOS, Linux (Electron) — offline capable |
| **VS Code** | Extension (`.drawio` file editing in IDE) |
| **github.dev / Codespaces** | VS Code web extension |
| **MCP Server** | Official `@drawio/mcp` npm package (Feb 2026) |

### MCP Server (Model Context Protocol)

draw.io has an **official MCP server** — directly relevant for AI agent workflows:

| Feature | Details |
|---------|---------|
| **Package** | `@drawio/mcp` on npm |
| **Repository** | `github.com/jgraph/drawio-mcp` |
| **Hosted endpoint** | `https://mcp.draw.io/mcp` |
| **Modes** | MCP App Server (inline in chat), MCP Tool Server (stdio), Claude Code Skill, Project Instructions |
| **Tools** | `open_drawio_xml`, `open_drawio_csv`, `open_drawio_mermaid` |

This means Claude Code, Cursor, and other AI agents can **generate and open draw.io diagrams programmatically** — a direct integration point for the IPAI stack's AI agent architecture.

### Tier 3 — Community / Third-Party

| Platform | Type |
|----------|------|
| **Nextcloud** | Integration with shared cursors |
| **Grafana** | Panel plugin |
| **JupyterLab** | IPyDrawio extension |
| **MediaWiki** | Extension |
| **ONLYOFFICE** | Plugin |
| **Redmine** | Plugin |

### Sources
- [draw.io Integrations](https://www.drawio.com/integrations)
- [draw.io blog - Integrations](https://www.drawio.com/blog/integrations)
- [draw.io for Plane.so](https://www.drawio.com/blog/diagrams-in-plane)

---

## 5. Features

### Diagram Types
- Flowcharts, UML (all 14 types), BPMN 2.0, ERD, network diagrams
- AWS / Azure / GCP architecture diagrams (official shape libraries)
- Kubernetes, Docker, Cisco network diagrams
- Org charts, mind maps, Gantt charts, PERT diagrams
- Mockups / wireframes, floor plans
- Electrical, P&ID engineering diagrams
- Threat modeling (STRIDE)

### AI Diagram Generation (Generate Tool)
- **Sparkle button** in toolbar — describe diagram in natural language
- Supports multiple LLM backends:
  - OpenAI: GPT-5.1, GPT-4.1, GPT-4o, GPT-3.5
  - Google: Gemini 2.5 Pro, Gemini 2.5 Flash
  - Anthropic: Claude 4.5 Sonnet, Claude 4.0 Sonnet, Claude 3.7 Sonnet
- Generates: flowcharts, infrastructure diagrams, Mermaid diagrams, interface mockups
- Configurable via `configure-ai-options` — admins can set default model, restrict providers
- No login required for AI generation (uses OpenAI by default)

### Real-Time Collaboration
- **Shared cursors** — see team members' mouse positions live
- Available with: Google Drive, OneDrive, Confluence Cloud, Nextcloud (with autosave)
- No separate collaboration server needed — uses storage platform's sync

### Import/Export Formats

| Format | Import | Export | Notes |
|--------|--------|--------|-------|
| `.drawio` / `.xml` | Yes | Yes | Native format |
| `.vsdx` (Visio) | Yes | **Removed v26.1** | Export removed March 2025 |
| `.svg` | Yes | Yes | Can embed XML for round-trip |
| `.png` | Yes | Yes | Can embed XML for round-trip |
| `.pdf` | — | Yes | Multi-page with links |
| `.html` | Yes | Yes | |
| BPMN 2.0 XML | **No** | **No** | Frequently requested, not implemented |
| Gliffy | Yes | — | |
| Lucidchart | Yes | — | |
| Mermaid | Yes | Yes |
| PlantUML | Yes | — |
| CSV/text | Yes | — |

### Other Features
- **Freehand drawing** mode
- **Smart templates** with AI generation
- **Custom shape libraries** — create, share, load via URL
- **Tags and layers** for complex diagrams
- **Dark mode** with adaptive colors
- **Scratchpad** for frequently used shapes
- **Math typesetting** (LaTeX)
- **Link to specific pages/layers** in multi-page diagrams

### Sources
- [draw.io Features](https://www.drawio.com/blog/features)
- [Generate tool blog post](https://drawio-app.com/blog/the-generate-tool-in-draw-io/)
- [Configure AI options](https://www.drawio.com/doc/faq/configure-ai-options)
- [Real-time collaboration](https://www.drawio.com/blog/real-time-collaboration-diagrams)

---

## 6. Pricing & Licensing

### Free (Always)

| Component | Cost |
|-----------|------|
| **Web app** (app.diagrams.net) | Free |
| **Desktop app** (Windows/Mac/Linux) | Free |
| **VS Code extension** | Free |
| **GitHub / GitLab integration** | Free |
| **Google Drive / OneDrive** | Free |
| **Self-hosted Docker** | Free |
| **Source code** (Apache 2.0) | Free |

### Paid — Atlassian Marketplace Only

| Tier | Confluence Cloud | Jira Cloud |
|------|-----------------|------------|
| **1-10 users** | Free | Free |
| **11-100 users** | ~$1-2/user/year | ~$0.50-1/user/year |
| **101+ users** | Volume pricing (~$0.50-2/user/year) | Volume pricing |
| **Data Center** | Per-instance pricing | Per-instance pricing |

**Editions** (Confluence/Jira):
- **Standard**: Full diagramming features
- **Advanced**: Standard + premium support, dedicated account manager, custom security reviews, enhanced data controls, development previews

### Sources
- [draw.io Pricing](https://drawio-app.com/pricing/)
- [Atlassian Marketplace - draw.io](https://marketplace.atlassian.com/apps/1210933/draw-io-diagrams-for-confluence)
- [draw.io Pricing - CostBench](https://costbench.com/software/diagramming/drawio/)

---

## 7. API & Extensibility

### Embed Mode (HTML5 Messaging API)
- Host draw.io in an **iframe** with special URL parameters
- Control the editor via **postMessage** API
- `embed.diagrams.net` — dedicated embed endpoint
- `diagram-editor.js` — reusable JavaScript wrapper for the editor
- Chrome extension template (Manifest V3) for adding draw.io to any web app

### Storage Format Options for Embedding
- **PNG** with embedded XML — fast loading, larger files
- **SVG** with embedded XML — fast loading, scalable, recommended
- **Raw XML** — smallest, requires rendering

### Custom Shape Libraries
- Create custom libraries of shapes, images, groups, templates
- Load via URL parameter: `?clibs=U<library_url>`
- Configure defaults via JSON: `defaultLibraries`, `defaultCustomLibraries`
- Share company-wide in Confluence via admin configuration

### Plugins
Built-in plugins include:
- **anon** — scrambles text/metadata for sharing
- **svgdata** — adds metadata/IDs to SVG exports
- **sql** — auto-generate database diagrams from SQL
- **tags** — tag-based shape management
- Custom plugins possible but with security dialog in embed mode

### Sources
- [draw.io Integration API](https://github.com/jgraph/drawio-integration)
- [Custom shape libraries](https://www.drawio.com/blog/custom-libraries)
- [Plugins list](https://www.drawio.com/doc/faq/plugins)

---

## 8. Self-Hosting (Docker)

### Official Docker Image

```yaml
# docker-compose.yml
version: "3"
services:
  drawio:
    image: jgraph/drawio:latest
    ports:
      - "8080:8080"
      - "8443:8443"
    restart: unless-stopped
```

### Features of Self-Hosted
- Full diagram editor with all shape libraries
- Server-side PDF/image/.vsdx export
- Google Drive and OneDrive storage support
- No dependency on draw.io servers
- WebSocket support for HTTPS
- Configurable via `PreConfig.js` and `PostConfig.js` (mounted as volumes)
- Active maintenance — versions 28.0.4 (Jul 2025), 29.2.9 (Dec 2025)

### Self-Contained Mode
- `jgraph/docker-drawio` repo has a `self-contained` variant
- Includes all export dependencies bundled
- No external network calls
- Suitable for air-gapped / regulated environments

### GitLab Self-Managed Integration
```bash
docker run -it --rm --name="draw" -p 8006:8080 -p 8443:8443 jgraph/drawio
```
Then enable in GitLab Admin > Settings > Diagrams.net

### Sources
- [draw.io Docker blog](https://www.drawio.com/blog/diagrams-docker-app)
- [jgraph/docker-drawio GitHub](https://github.com/jgraph/docker-drawio)
- [Self-contained README](https://github.com/jgraph/docker-drawio/blob/dev/self-contained/README.md)

---

## 9. Git Integration Details

### GitHub

| Feature | Details |
|---------|---------|
| **Direct mode** | `app.diagrams.net/?mode=github` |
| **File formats** | `.png`, `.svg`, `.html`, `.xml` |
| **Version control** | Full git history, diffs, PRs |
| **github.dev** | Edit `.drawio` files in browser IDE |
| **VS Code extension** | Edit locally, commit changes |
| **Side-by-side diff** | Compare original vs edited diagram |

### GitLab

| Feature | Details |
|---------|---------|
| **Wiki integration** | Built into GitLab 15.10+ |
| **Format** | Saves as `.drawio.svg` in wiki pages |
| **Self-managed** | Self-hosted draw.io server supported |
| **Version tracking** | All changes tracked via GitLab versioning |

### Best Practices for Git + draw.io
1. Use `.drawio.svg` format — renders in GitHub/GitLab preview AND contains editable diagram data
2. Store diagrams alongside code in `docs/` directories
3. Use PRs for diagram reviews — visual diffs available
4. VS Code extension enables edit-commit workflow without leaving IDE

### Sources
- [draw.io GitHub integration](https://github.com/jgraph/drawio-github)
- [Edit diagrams with github.dev](https://www.drawio.com/blog/edit-diagrams-with-github-dev)
- [GitLab wiki integration](https://www.drawio.com/blog/gitlab-wiki-integration)
- [GitLab Docs - Diagrams.net](https://docs.gitlab.com/administration/integration/diagrams_net/)

---

## 10. Plane.so Integration

Plane.so (open-source project management) has a native draw.io integration.

### draw.io in Plane Pages

| Feature | Details |
|---------|---------|
| **Activation** | Workspace Settings > Integrations > Draw.io > Configure |
| **Slash commands** | `/draw`, `/diagram`, `/drawio-diagram` |
| **Editors** | Full draw.io editor + simplified Board editor (whiteboard) |
| **Shape libraries** | All standard + AI-generated smart templates + Mermaid |
| **Display** | Diagrams render inline in pages, click to edit |
| **Dark mode** | Adaptive colors — works in both light/dark |
| **Whiteboard** | Freehand drawing/sketching for brainstorming |
| **Limitation** | Diagram changes NOT in page version history |
| **Note** | Third-party integration — draw.io did not develop it |

### Plane.so Editions & Architecture

| Edition | License | Key Features |
|---------|---------|-------------|
| **Community (CE)** | AGPL v3.0 (open source) | Core features, unlimited users/projects, free forever |
| **Commercial (Self-Hosted)** | Closed source | CE + SSO/RBAC, governance, compliance, reporting |
| **Airgapped** | Closed source | Commercial + zero external calls, for defense/gov/regulated |
| **Cloud** | SaaS | Hosted by Plane |

### Plane.so Pricing

| Tier | Cost | Notes |
|------|------|-------|
| **Free** | $0 | Core features (Community or Commercial CE) |
| **Pro** | $6/seat/month | Custom work items, integrations |
| **Business** | Custom | Workflow automations, approvals, templates |
| **Enterprise** | Custom | Airgapped, LDAP, advanced compliance |

Same price for cloud and self-hosted.

### Plane.so Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django (Python) |
| **Frontend** | Next.js (React) |
| **Database** | PostgreSQL (built-in) |
| **Storage** | MinIO (built-in) |
| **Deployment** | Docker or Kubernetes (Helm) |
| **Min requirements** | 2 CPU, 4 GB RAM, 20 GB storage |
| **Architectures** | x64, ARM64 |
| **OS** | Ubuntu, Debian, CentOS, Amazon Linux |

### Plane.so on DigitalOcean

Community Edition is available as a **1-Click App on DigitalOcean Marketplace** — directly compatible with the InsightPulse AI hosting strategy.

### Sources
- [draw.io for Plane.so blog](https://www.drawio.com/blog/diagrams-in-plane)
- [Plane.so Marketplace - draw.io](https://plane.so/marketplace/drawio)
- [Plane.so Pricing](https://plane.so/pricing)
- [Plane.so Self-Hosting](https://developers.plane.so/self-hosting/overview)
- [Plane.so Editions](https://developers.plane.so/self-hosting/editions-and-versions)
- [Plane.so on DigitalOcean](https://marketplace.digitalocean.com/apps/plane-community-edition)
- [Plane.so Editor Blocks](https://docs.plane.so/core-concepts/pages/editor-blocks)

---

## 11. draw.io vs SAP Signavio — Comparison

### Executive Summary

| Dimension | draw.io | SAP Signavio |
|-----------|---------|--------------|
| **Primary Purpose** | General diagramming tool | Enterprise BPM + Process Mining suite |
| **Cost** | Free (open source) | $150K-800K+/year enterprise |
| **BPMN 2.0** | Full shape support (modeling only) | Full modeling + simulation + execution |
| **Process Mining** | None | Core capability (event log analysis) |
| **AI Features** | Diagram generation (multi-LLM) | Process analysis, text-to-process, agent mining |
| **Collaboration** | Real-time shared cursors | Enterprise workflow + approval chains |
| **Self-Hosted** | Yes (Docker, free) | Yes (but expensive) |
| **ERP Integration** | None native | Deep SAP integration, some ERP connectors |
| **Target User** | Developers, architects, teams | Enterprise process analysts, consultants |

### Detailed Comparison

#### Process Mining & BPM

| Capability | draw.io | SAP Signavio |
|------------|---------|--------------|
| BPMN 2.0 modeling | Yes (shapes + notation) | Yes (full spec + validation) |
| BPMN simulation | No | Yes |
| BPMN execution | No | Yes (via SAP integration) |
| Process mining (event logs) | No | Yes (core feature) |
| Task mining | No | Yes |
| AI agent mining | No | Yes (Nov 2025) |
| Conformance checking | No | Yes |
| Process KPIs / dashboards | No | Yes |
| Text-to-process | Yes (AI generate) | Yes (AI modeler) |
| Process governance | No | Yes (approval workflows) |
| Decision modeling (DMN) | No | Yes |
| Process repository | No | Yes (enterprise catalog) |

#### Cost Analysis

| Scenario | draw.io | SAP Signavio |
|----------|---------|--------------|
| **10-person team** | $0 | ~$20K-30K/year |
| **100-person org** | $0 | ~$150K-300K/year |
| **500-person enterprise** | $0 | ~$500K-800K+/year |
| **Self-hosted** | $0 (Docker) | Custom quote |
| **Atlassian users (100)** | ~$100-200/year | N/A |

#### When to Use Each

**Use draw.io when:**
- You need a general-purpose diagramming tool
- Budget is limited or zero
- You want Git-integrated diagrams (docs-as-code)
- You need architecture, network, UML, ERD diagrams
- Your team uses Confluence, GitHub, GitLab, or Plane.so
- Privacy is paramount (no data leaves your control)
- You need BPMN notation without process mining

**Use SAP Signavio when:**
- You need actual process mining (analyzing event logs from ERP systems)
- You're in the SAP ecosystem and need deep integration
- You need process simulation and conformance checking
- You need enterprise process governance with approval workflows
- You need AI-driven process optimization insights
- You have budget for enterprise licensing ($150K+/year)
- You need regulatory compliance process documentation with audit trails

### Open-Source BPM Alternatives

If you need BPM capabilities beyond draw.io but can't afford Signavio:

| Tool | Type | BPMN | Process Mining | Cost |
|------|------|------|----------------|------|
| **Camunda Modeler** | BPM modeling + execution | Full BPMN 2.0 | No | Free (open source) |
| **bpmn.io** | BPMN web modeler | Full BPMN 2.0 | No | Free (open source) |
| **ProM** | Process mining framework | Import | Yes (full) | Free (open source) |
| **PM4Py** | Python process mining | Import | Yes (full) | Free (open source) |
| **Apromore** | Process mining + modeling | Yes | Yes | Free (community edition) |
| **ProcessMind** | SaaS process mining | Yes | Yes | $99/month |

### Sources
- [SAP Signavio Process Intelligence](https://www.signavio.com/products/process-intelligence/)
- [SAP Signavio AI Agent Mining](https://news.sap.com/2025/11/how-sap-signavio-agent-mining-transforms-enterprise-ai/)
- [SAP Signavio Pricing - Capterra](https://www.capterra.com/p/137139/Signavio/pricing/)
- [Top SAP Signavio Alternatives - G2](https://www.g2.com/products/sap-signavio/competitors/alternatives)
- [Open Source Process Mining Tools](https://research.aimultiple.com/open-source-process-mining/)

---

## 12. Relevance to InsightPulse AI / Odoo CE Stack

### Recommendation

**draw.io is the clear choice** for the InsightPulse AI stack:

1. **Cost**: Free — aligns with cost-minimized self-hosted philosophy
2. **Self-hosted**: Docker deployment fits existing DO infrastructure
3. **Git integration**: `.drawio.svg` files can live in repo alongside code
4. **VS Code**: Extension enables diagram editing in development workflow
5. **Privacy**: No data leaves infrastructure — matches security requirements
6. **BPMN 2.0**: Sufficient for process documentation (not process mining)
7. **AI generation**: Supports Claude, GPT, Gemini for diagram generation
8. **Open format**: No vendor lock-in, XML files always readable
9. **Plane.so**: Native integration if using Plane for project management

### Integration Points

```
draw.io Docker (self-hosted, port 8080)
    |
    +-- GitLab/GitHub: .drawio.svg in docs/ directories
    +-- VS Code: Direct editing via extension
    +-- Confluence: If using Atlassian (marketplace app)
    +-- Plane.so: /draw slash command in pages
    +-- Odoo: Embed SVG exports in knowledge base
    +-- n8n: Generate diagrams via API (embed mode)
```

### Potential docker-compose Addition

```yaml
# Add to existing docker-compose.yml
services:
  drawio:
    image: jgraph/drawio:latest
    ports:
      - "8080:8080"
    restart: unless-stopped
    volumes:
      - ./config/drawio/PreConfig.js:/usr/local/tomcat/webapps/draw/js/PreConfig.js
      - ./config/drawio/PostConfig.js:/usr/local/tomcat/webapps/draw/js/PostConfig.js
```

### SAP Signavio — Not Recommended

SAP Signavio is **not appropriate** for this stack:
- Pricing ($150K-800K+/year) contradicts cost-minimized philosophy
- SAP ecosystem lock-in contradicts vendor independence goals
- Process mining requires SAP ERP event logs — not applicable for Odoo CE
- Enterprise licensing contradicts open-source-first approach

If process mining is needed in the future, consider **PM4Py** (Python, free) or **Apromore** (self-hosted, community edition).

### Critical Limitation: No BPMN 2.0 XML Export

draw.io does **not** export native BPMN 2.0 XML — it treats BPMN shapes as generic drawing elements without semantic validation. This is a [frequently requested feature](https://github.com/jgraph/drawio/discussions/2829) that remains unimplemented. If executable BPMN 2.0 XML interoperability is required, use **bpmn.io** or **Camunda Modeler** instead.

---

## 13. Open-Source BPM Alternatives Landscape

If executable BPM or native BPMN 2.0 compliance is needed beyond draw.io's visual diagramming:

| Tool | Type | BPMN 2.0 | Execution Engine | License | Best For |
|------|------|----------|------------------|---------|----------|
| **draw.io** | General diagramming | Shapes only | No | Apache v2 | Quick visual diagrams |
| **bpmn.io** | Embeddable JS library | Full standard | No (modeling) | Camunda-backed | Embedding BPMN editors in web apps |
| **Camunda Modeler** | Desktop BPMN editor | Full + DMN | Exports to Camunda | Open source | Designing executable processes |
| **Operaton** | BPM engine (Camunda 7 fork) | Full standard | Yes | Community-owned | Running BPMN processes, free |
| **CIB seven** | BPM engine (Camunda 7 fork) | Full standard | Yes | OSS + commercial | Camunda 7 migration path |
| **Flowable** | BPM platform | BPMN + CMMN + DMN | Yes | Open core | Low-code BPM |
| **jBPM** | BPM engine | Full standard | Yes | Open source | Java-based automation |
| **Activiti** | Lightweight BPM | BPMN 2.0 | Yes | Open source | Simple Java workflows |

**Lineage**: Activiti (2010) -> Camunda fork (2013) -> Flowable fork (2017) -> Operaton fork (2024) -> CIB seven (2025)

**For the Odoo CE stack**: bpmn.io or Camunda Modeler for BPMN modeling; Operaton or Flowable if executable BPM automation is needed alongside Odoo. draw.io remains the best choice for general-purpose diagramming at zero cost.

### Sources (BPM Alternatives)
- [bpmn.io](https://bpmn.io/)
- [Operaton - Open Source BPM](https://operaton.org/)
- [CIB seven](https://cibseven.org/en/)
- [draw.io BPMN 2.0 XML export discussion](https://github.com/jgraph/drawio/discussions/2829)

---

*Research compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*

# UX Wireframes — Rork-Style App Builder

> Scope: Information architecture, screen layouts, component hierarchy, and states.
> Fidelity: Low–mid (layout + behavior), ready for Figma or direct frontend build.

---

## 1) Global Information Architecture

```
/ (Dashboard)
 ├─ /apps
 │   └─ /apps/:app_id
 │       ├─ workspace        (core builder)
 │       ├─ spec             (Spec Graph)
 │       ├─ code             (PR / diff)
 │       ├─ verify           (tests, checks)
 │       ├─ preview          (device/web)
 │       └─ publish          (deploy & domains)
 ├─ /integrations            (catalog + health)
 ├─ /runs                    (build history)
 ├─ /settings
 └─ /org
```

---

## 2) Primary Screen Wireframes

### A. Dashboard (/)

```
+------------------------------------------------------+
| Top Bar: Org ▾ | Create App | Search | Profile ▾     |
+------------------------------------------------------+
| KPI Row                                               |
| [Apps] [Builds] [Errors] [Deployments]               |
+------------------------------------------------------+
| Apps List                                             |
| ---------------------------------------------------- |
| App Name | Status | Last Build | Env | Actions ▸      |
| ---------------------------------------------------- |
| Shelf     | ✓     | 2m ago     | prod| Open           |
| OdooOps   | ⚠     | 10m ago    | stg | Open           |
+------------------------------------------------------+
```

Behaviors:
- "Create App" opens prompt-first modal
- Status badges live via Realtime

---

### B. App Workspace (/apps/:id/workspace) — Core Screen

```
+--------------------------------------------------------------------------------+
| App: Shelf | Env: prod ▾ | Build: PASS ✓ | Publish | ⋯                         |
+--------------------------------------------------------------------------------+
| Prompt / Chat                     | Live Preview / Device                      |
|----------------------------------|--------------------------------------------|
| > Build an asset mgmt app…        | [Web Preview] [iOS QR] [Android QR]         |
|                                   |                                            |
| Assistant responses               |  ┌─────────────────────────────────────┐  |
|                                   |  |   Live App Preview                    |  |
|                                   |  |                                     |  |
|                                   |  └─────────────────────────────────────┘  |
|----------------------------------|--------------------------------------------|
| Spec Graph (Tree)                 | Code / PR Diff                             |
|----------------------------------|--------------------------------------------|
| ▸ Auth                            | + files changed (12)                       |
| ▸ Data                            |  ──────────────────────────────────────  |
| ▸ UI                              |  + pages/dashboard.tsx                    |
| ▸ Integrations                    |  + api/assets.ts                          |
|                                   |  + db/migrations/…                        |
+--------------------------------------------------------------------------------+
```

Key UX Rules:
- Prompt edits → Spec updates → Code PR auto-updates
- Preview refreshes only on green verify
- Spec Graph is clickable → scrolls diff

---

### C. Spec Graph Viewer (/apps/:id/spec)

```
+------------------------------------------------------+
| Spec Graph — Read / Diff                             |
+------------------------------------------------------+
| Left: Tree                  | Right: Detail         |
|-----------------------------|------------------------|
| ▸ Auth                      | Entity: User          |
| ▸ Data                      | Fields                |
| ▸ UI                        | Relationships         |
| ▸ Integrations              | Constraints           |
|                              | Source of truth:     |
|                              | supabase / odoo      |
+------------------------------------------------------+
```

States:
- Generated
- Modified (local)
- Locked (published tag)

---

### D. Code / PR Viewer (/apps/:id/code)

```
+------------------------------------------------------+
| PR #142 — Auto-generated                             |
+------------------------------------------------------+
| Files            | Diff                              |
|------------------|-----------------------------------|
| api/assets.ts    | + export async function …         |
| ui/List.tsx      | - old                              |
| db/001_init.sql  | + create table assets …           |
+------------------------------------------------------+
```

Rules:
- Read-only unless "Manual Override" toggled
- All overrides logged as Spec annotations

---

### E. Verification (/apps/:id/verify)

```
+------------------------------------------------------+
| Verification Report                                  |
+------------------------------------------------------+
| ✓ Type check                                         |
| ✓ Lint                                               |
| ✓ DB migrate                                         |
| ✓ Policy gate (SSOT/SoR)                             |
| ⚠ Integration health (Zoho SMTP blocked)             |
+------------------------------------------------------+
| Blocking issues must be resolved before Publish      |
+------------------------------------------------------+
```

---

### F. Preview (/apps/:id/preview)

```
+------------------------------------------------------+
| Preview                                              |
+------------------------------------------------------+
| [Web] [iOS] [Android]                                |
|                                                      |
| Device Frame                                         |
| ┌─────────────────────────────────────────────────┐ |
| |                                                 | |
| |   Running app preview                           | |
| |                                                 | |
| └─────────────────────────────────────────────────┘ |
+------------------------------------------------------+
```

---

### G. Publish (/apps/:id/publish)

```
+------------------------------------------------------+
| Publish                                              |
+------------------------------------------------------+
| Environment: prod ▾                                  |
| Domain: shelf.insightpulseai.com                     |
| Version: v1.2.0                                      |
|                                                      |
| [ Publish ]                                          |
+------------------------------------------------------+
```

Post-Publish:
- Locks Spec
- Tags repo
- Writes canonical URL entry

---

### H. Integrations (/integrations)

```
+------------------------------------------------------+
| Integrations                                         |
+------------------------------------------------------+
| Card Grid                                            |
| ┌──────────────┐ ┌──────────────┐                  |
| | Stripe ✓     | | Mailgun ✓    |                  |
| | Payments     | | Email        |                  |
| └──────────────┘ └──────────────┘                  |
| ┌──────────────┐ ┌──────────────┐                  |
| | Zoho ⚠       | | Superset ✓   |                  |
| | Blocked      | | Analytics    |                  |
| └──────────────┘ └──────────────┘                  |
+------------------------------------------------------+
```

---

## 3) Global Components

- TopBar
- PromptComposer
- SpecGraphTree
- DiffViewer
- VerificationChecklist
- IntegrationCard
- DevicePreviewPanel
- StatusBadge

---

## 4) Responsive Rules

**Desktop**: 3-column workspace, persistent Spec + Code

**Tablet**: 2-column (Chat + Preview), Spec/Code in tabs

**Mobile**: Preview-first, Prompt + Spec in drawer

---

## 5) Error & Empty States

- No Spec → "Describe what to build"
- Failed Verify → Inline remediation prompt
- Blocked Integration → Explain + workaround

---

## 6) Design System Assumptions

- Base: Supabase UI / shadcn-style primitives
- Density: High-information (dev-tool)
- Theme: Light + Dark
- Accessibility: Keyboard-first, ARIA labels

---

## 7) Mobile Workspace Layout

```
┌─────────────────────────┐
│ TopBar                  │
├─────────────────────────┤
│                         │
│   LIVE PREVIEW          │
│                         │
├─────────────────────────┤
│ ⌄ Prompt | Spec | Code  │
└─────────────────────────┘
```

Mobile Rules:

| Area | Behavior |
|------|----------|
| Default | Preview |
| Prompt | Bottom sheet |
| Spec | Swipe-up drawer |
| Code | Read-only modal |
| Publish | Full-screen confirmation |

Mobile Components:
- Drawer (shadcn)
- BottomSheet
- SegmentedTabs
- DeviceFrame scales dynamically

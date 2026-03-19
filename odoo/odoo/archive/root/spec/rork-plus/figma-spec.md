# Figma Frames + Design Spec — Rork-Style App Builder

---

## Figma File Structure

```
RORK-STYLE-PLATFORM.fig
├─ Foundations
│  ├─ Colors
│  ├─ Typography
│  ├─ Spacing
│  └─ Elevation
├─ Components
│  ├─ TopBar
│  ├─ PromptComposer
│  ├─ SpecTree
│  ├─ DiffViewer
│  ├─ VerificationChecklist
│  ├─ IntegrationCard
│  ├─ DeviceFrame
│  └─ StatusBadge
├─ Desktop
│  ├─ Dashboard
│  ├─ AppWorkspace
│  ├─ SpecGraph
│  ├─ CodeViewer
│  ├─ Verify
│  ├─ Preview
│  ├─ Publish
│  └─ Integrations
├─ Mobile
│  ├─ Dashboard
│  ├─ AppWorkspace
│  ├─ SpecDrawer
│  ├─ Preview
│  └─ Publish
```

---

## Core Desktop Frames

### Dashboard
- Frame: 1440 x 1024
- Grid: 12-col, 80px margins
- Layout:
  - TopBar (fixed)
  - KPI row (auto-layout horizontal)
  - Apps table (auto-layout vertical, row height 56)

### App Workspace (KEY FRAME)
- Frame: 1600 x 1024
- 3-column auto-layout

| Column | Width | Content |
|--------|-------|---------|
| Prompt / Chat | 360px fixed | PromptComposer |
| Preview | flex | DeviceFrame |
| Spec + Code | 420px fixed | SpecCodePanel (tabbed) |

Auto-layout rules:
- Horizontal
- Fill container
- Gap: 16
- Columns scroll independently

### Spec Graph
- Left: Tree (fixed 320)
- Right: Detail (fill)
- Tree nodes use:
  - Status dot (generated / modified / locked)
  - Click → highlights code diff

### Code / PR Viewer
- Left: File list (280)
- Right: Diff viewer (monospace, line numbers)
- Sticky header: PR #, status, repo

### Integrations
- Grid: 3-column cards
- Card states:
  - Active
  - Blocked
  - Disabled
- Each card links to:
  - SSOT entry
  - Health log

---

## Mobile Frames (390 x 844)

### Mobile Workspace
- Default view: Preview
- Bottom sheet:
  - Prompt
  - Spec
  - Code
- Gesture-based drawer (like Supabase Studio mobile)

---

## TSX Layout Scaffolds

### Root Layout (`app/layout.tsx`)

```tsx
import { TopBar } from '@/components/top-bar'
import { Toaster } from '@/components/ui/sonner'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-background text-foreground">
        <TopBar />
        <main className="h-[calc(100vh-56px)]">{children}</main>
        <Toaster />
      </body>
    </html>
  )
}
```

### Dashboard (`app/page.tsx`)

```tsx
import { AppsTable } from '@/components/apps-table'
import { KPIBar } from '@/components/kpi-bar'

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6">
      <KPIBar />
      <AppsTable />
    </div>
  )
}
```

### Workspace (`app/apps/[id]/workspace/page.tsx`)

```tsx
import { PromptPanel } from '@/components/prompt-panel'
import { PreviewPanel } from '@/components/preview-panel'
import { SpecCodePanel } from '@/components/spec-code-panel'

export default function WorkspacePage() {
  return (
    <div className="flex h-full gap-4 p-4">
      <div className="w-[360px]">
        <PromptPanel />
      </div>
      <div className="flex-1">
        <PreviewPanel />
      </div>
      <div className="w-[420px]">
        <SpecCodePanel />
      </div>
    </div>
  )
}
```

### Spec + Code Panel (Tabbed)

```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

export function SpecCodePanel() {
  return (
    <Tabs defaultValue="spec" className="h-full">
      <TabsList>
        <TabsTrigger value="spec">Spec</TabsTrigger>
        <TabsTrigger value="code">Code</TabsTrigger>
      </TabsList>
      <TabsContent value="spec" className="h-full">
        <SpecTree />
      </TabsContent>
      <TabsContent value="code" className="h-full">
        <DiffViewer />
      </TabsContent>
    </Tabs>
  )
}
```

### Verification Checklist

```tsx
export function VerifyPanel({ checks }) {
  return (
    <ul className="space-y-2">
      {checks.map(c => (
        <li key={c.id} className="flex items-center gap-2">
          <StatusBadge status={c.status} />
          <span>{c.label}</span>
        </li>
      ))}
    </ul>
  )
}
```

---

## UX Guarantees

- Prompt → Spec → Code → Verify → Publish is unbroken
- Spec is always inspectable
- Manual code edits are annotated + reversible
- Supabase = SSOT, Odoo = SoR enforced at UI level
- Every deployment writes Canonical URL + tag

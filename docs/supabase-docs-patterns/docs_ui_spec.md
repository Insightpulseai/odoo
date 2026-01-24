# Supabase Docs UI Specification

> Extracted from Supabase documentation site for UI pattern replication.
> Last updated: 2026-01-24

## Overview

This document defines the UI patterns, layout structure, and component specifications for replicating the Supabase documentation interface.

---

## Layout Grid & Regions

```
┌─────────────────────────────────────────────────────────────────┐
│                        HEADER (z-50)                            │
│  [Logo DOCS] [Start] [Products] [Build] [Manage] [Ref] [⌘K]    │
├───────────────────┬─────────────────────────────────────────────┤
│                   │                                             │
│   SIDEBAR         │           CONTENT                           │
│   (420px fixed)   │           (flex-1)                          │
│   (sticky top)    │                                             │
│                   │  ┌───────────────────────────────────────┐ │
│  ┌─────────────┐  │  │  Breadcrumbs                          │ │
│  │ Section 1   │  │  │                                       │ │
│  │  └ Item     │  │  │  # Page Title                        │ │
│  │  └ Item     │  │  │                                       │ │
│  ├─────────────┤  │  │  Content...                          │ │
│  │ Section 2   │  │  │                                       │ │
│  │  └ Item     │  │  │                           ┌─────────┐│ │
│  │  └ Item ▸   │  │  │                           │ TOC     ││ │
│  │    └ Child  │  │  │                           │ On this ││ │
│  │    └ Child  │  │  │                           │ page    ││ │
│  └─────────────┘  │  │                           └─────────┘│ │
│                   │  │                                       │ │
│                   │  │  [Edit on GitHub] [Feedback]          │ │
│                   │  └───────────────────────────────────────┘ │
├───────────────────┴─────────────────────────────────────────────┤
│                          FOOTER                                 │
│  [Links Columns]            [© Supabase] [Social: X/GH/Discord] │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Inventory

### 1. Global Header (`DocsHeader`)

**Responsibilities:**
- Display wordmark with "DOCS" label
- Primary navigation menu (horizontal)
- Search trigger with keyboard shortcut indicator
- Dashboard link (external)

**Props:**
```typescript
interface DocsHeaderProps {
  logo?: React.ReactNode;
  docsLabel?: string;
  navItems: NavItem[];
  searchPlaceholder?: string;
  dashboardUrl?: string;
}
```

**Styling:**
- Position: `fixed top-0`
- Z-index: `z-50`
- Height: `h-14` (56px)
- Background: `bg-background` (dark mode aware)
- Border: `border-b border-border`

**Primary Nav Items (default):**
| Label | Description |
|-------|-------------|
| Start | Getting started guides |
| Products | Database, Auth, Storage, Edge Functions, Realtime |
| Build | Local dev, deployment, integrations |
| Manage | Platform, security, troubleshooting |
| Reference | API docs, CLI, SDKs |
| Resources | Glossary, changelog, status |

**Search Behavior:**
- Placeholder: "Search docs..."
- Keyboard shortcut: `⌘K` (Mac) / `Ctrl+K` (Windows)
- Opens modal/dialog with search results
- Result panel: grouped by section

---

### 2. Left Sidebar (`DocsSidebar`)

**Responsibilities:**
- Hierarchical navigation tree
- Section expand/collapse (accordion)
- Active route highlighting
- Sticky positioning

**Props:**
```typescript
interface DocsSidebarProps {
  sections: NavSection[];
  currentPath: string;
  onNavigate?: (path: string) => void;
}

interface NavSection {
  id: string;
  title: string;
  icon?: string;
  items: NavItem[];
}

interface NavItem {
  title: string;
  href: string;
  icon?: string;
  children?: NavItem[];
  isExternal?: boolean;
}
```

**Styling:**
- Width: `w-[420px]` desktop, `w-full` mobile drawer
- Position: `sticky top-14` (below header)
- Height: `h-[calc(100vh-56px)]`
- Overflow: `overflow-y-auto`
- Border: `border-r border-border`

**States:**
| State | Style |
|-------|-------|
| Default | `text-foreground-light` |
| Hover | `text-foreground hover:bg-muted` |
| Active | `bg-background text-brand-link font-medium` |
| Section expanded | Chevron rotated 90° |

**Accordion Behavior:**
- Type: `single` (only one section open at a time)
- Persist open state in localStorage
- Animated chevron rotation

---

### 3. Content Area (`DocsContent`)

**Responsibilities:**
- Page title and intro
- Main content rendering (MDX)
- Breadcrumbs (optional)
- Edit link and feedback widget

**Props:**
```typescript
interface DocsContentProps {
  title: string;
  description?: string;
  breadcrumbs?: Breadcrumb[];
  editUrl?: string;
  children: React.ReactNode;
}

interface Breadcrumb {
  title: string;
  href?: string;
}
```

**Styling:**
- Container: `flex-1 min-w-0`
- Max width: `max-w-4xl`
- Padding: `px-8 py-10`
- Typography: Prose styles with custom heading anchors

**Breadcrumb Rules:**
- Desktop: Show max 3 items, collapse middle if more
- Mobile: Show max 4 items
- Separator: `/` or chevron icon
- Current page: Not clickable, muted color

---

### 4. Table of Contents (`DocsToc`)

**Responsibilities:**
- "On this page" heading
- Auto-generated from H2/H3 headings
- Scroll-spy highlighting
- Optional video preview
- Feedback widget

**Props:**
```typescript
interface DocsTocProps {
  headings: TocHeading[];
  videoUrl?: string;
  showFeedback?: boolean;
}

interface TocHeading {
  id: string;
  text: string;
  level: 2 | 3;
}
```

**Styling:**
- Width: `w-64` (256px)
- Position: `sticky top-20`
- Border: `border-l border-border`
- Font: `font-mono uppercase text-xs`

**Scroll-Spy Behavior:**
- Highlight current heading based on scroll position
- Smooth scroll on click
- Intersection Observer for active detection

---

### 5. Footer (`DocsFooter`)

**Responsibilities:**
- Primary links with icons and CTAs
- Copyright notice
- Social links

**Props:**
```typescript
interface DocsFooterProps {
  primaryLinks?: FooterLink[];
  secondaryLinks?: FooterLink[];
  socialLinks?: SocialLink[];
  copyright?: string;
}

interface FooterLink {
  label: string;
  href: string;
  icon?: string;
  description?: string;
}

interface SocialLink {
  platform: 'twitter' | 'github' | 'discord' | 'youtube';
  href: string;
}
```

**Styling:**
- Background: `bg-background`
- Border: `border-t border-border`
- Padding: `py-8 px-8`
- Layout: Two columns, responsive

**Default Social Links:**
- Twitter/X
- GitHub
- Discord
- YouTube

---

## Behavior Notes

### Responsive Breakpoints

| Breakpoint | Sidebar | TOC | Layout |
|------------|---------|-----|--------|
| `< 640px` (sm) | Drawer overlay | Hidden | Single column |
| `640-1023px` (md) | Drawer overlay | Hidden | Single column |
| `>= 1024px` (lg) | Fixed sidebar | Visible | Three column |
| `>= 1280px` (xl) | Full 420px | Full 256px | Three column |

### Mobile Menu Behavior

- Hamburger icon in header
- Slide-in drawer from left (75% width mobile, 50% tablet)
- Semi-transparent backdrop with blur
- Close on navigation or backdrop click
- Section name displayed in toggle

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open search |
| `Escape` | Close search/modal |
| `↑/↓` | Navigate search results |
| `Enter` | Select result |

### Sticky Regions

- Header: Always fixed at top
- Sidebar: Sticky below header, scrolls independently
- TOC: Sticky in content area, scrolls with section

### Dark Mode

All components support dark mode via CSS variables:
```css
:root {
  --background: #ffffff;
  --foreground: #111111;
  --muted: #f5f5f5;
  --border: #e5e5e5;
  --brand-link: #3ecf8e;
  --foreground-light: #888888;
}

.dark {
  --background: #111111;
  --foreground: #ffffff;
  --muted: #1a1a1a;
  --border: #333333;
  --brand-link: #3ecf8e;
  --foreground-light: #888888;
}
```

---

## Edit on GitHub Link

**URL Pattern:**
```
https://github.com/{org}/{repo}/edit/{branch}/apps/docs/content/{path}.mdx
```

**Example:**
```
https://github.com/supabase/supabase/edit/master/apps/docs/content/guides/platform/integrations.mdx
```

---

## Feedback Widget

**Structure:**
```
Is this helpful?
[👎 No] [👍 Yes]
```

**Behavior:**
- Appears at end of content
- Records feedback with page path
- Optional: Expand for detailed feedback form

---

## Implementation Checklist

- [ ] Header renders with navigation and search
- [ ] Sidebar navigates hierarchically with accordions
- [ ] Content area renders MDX with prose styling
- [ ] TOC generates from headings with scroll-spy
- [ ] Footer displays links and social icons
- [ ] Mobile drawer works with backdrop
- [ ] Keyboard shortcuts functional
- [ ] Dark mode switches correctly
- [ ] Active link highlighting works
- [ ] Edit on GitHub link generates correctly

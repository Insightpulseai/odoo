# Fluent 2 docs UI system

## Why Fluent 2

The docs platform runs on Azure infrastructure, serves enterprise users, and must integrate visually with Azure-adjacent tooling (Azure Portal, DevOps, Entra). Fluent 2 is the natural choice for four reasons:

1. **Azure alignment**: Fluent is Microsoft's design system. Our platform runs on Azure Container Apps behind Azure Front Door. Visual consistency with the Azure ecosystem reduces cognitive switching for administrators.
2. **Enterprise/admin focus**: Fluent is designed for dense, information-rich applications. Documentation platforms are exactly this — navigation trees, metadata panels, search overlays, version switching, admin tables.
3. **Cross-platform**: Fluent UI React v9 supports web, with design tokens that extend to native platforms if needed later.
4. **Accessibility**: Fluent 2 ships with WCAG 2.2 AA compliance, high contrast themes, keyboard navigation, and screen reader support built into every component.

### Why not Primer

Primer (GitHub's design system) optimizes for developer tool aesthetics — code-centric, monospace-heavy, repository-oriented layouts. It is excellent for GitHub-like surfaces. Our docs platform is an enterprise admin tool, not a code browser. Fluent's density, panel layouts, and Azure alignment fit better.

## Implementation target

| Item | Value |
|---|---|
| Package | `@fluentui/react-components` (v9) |
| Root provider | `FluentProvider` wrapping the entire app |
| Light theme | `webLightTheme` |
| Dark theme | `webDarkTheme` |
| High contrast | `teamsHighContrastTheme` |
| Framework | React 18+ |
| Build | Vite or Next.js (static export) |

## App shell layout

```
┌─────────────────────────────────────────────────────────┐
│  GLOBAL HEADER (Toolbar)                                │
│  Logo | Search | Version | Settings | User              │
├────────────┬──────────────────────────┬─────────────────┤
│            │                          │                 │
│  LEFT NAV  │  MAIN CONTENT PANE      │  RIGHT PANE     │
│  (Tree)    │                          │  (TOC/Metadata) │
│            │  Breadcrumbs             │                 │
│  Sections  │  Page title              │  On this page   │
│  > Pages   │  Prose content           │  ─────────────  │
│  > Pages   │  Code blocks             │  Page metadata  │
│            │  Diagrams                │  Last updated   │
│  Sections  │  Tables                  │  Contributors   │
│  > Pages   │                          │  Tags           │
│            │                          │                 │
├────────────┴──────────────────────────┴─────────────────┤
│  (Overlays: Search/Command, Settings, History, Comments)│
└─────────────────────────────────────────────────────────┘
```

### Layout rules

- Global header is fixed. It does not scroll.
- Left nav is collapsible. On mobile, it becomes a drawer.
- Main content pane scrolls independently.
- Right pane is hidden on viewports below 1024px. TOC moves to a collapsible section above content on mobile.
- Overlays (search, settings, history, comments) are modal dialogs.

## Ownership boundary

### Fluent owns

Everything structural, interactive, and chrome-level:

- **Shell**: App shell, layout grid, responsive breakpoints
- **Navigation**: Left tree, breadcrumbs, global header, version switcher
- **Forms**: Search input, settings forms, filter controls
- **Buttons**: All actions — edit, share, copy, history, feedback
- **Dialogs**: Settings, confirmation, review, history, comments
- **Command surfaces**: Command palette (search overlay), context menus
- **Status/feedback**: Toast notifications, message bars, progress indicators
- **Admin tables**: Index pages, settings pages, contributor lists

### Content renderer owns

Everything inside the main content pane that is rendered from Markdown:

- **Prose layout**: Heading hierarchy, paragraph spacing, list styles
- **Markdown rendering**: Parsed and rendered Markdown content
- **Code blocks**: Syntax highlighting (Shiki or Prism), copy button, language label
- **Diagrams/embeds**: Mermaid diagrams, embedded media, interactive widgets
- **Long-form typography**: Font sizing, line height, max content width, reading rhythm

The content renderer uses its own CSS scoped to the content pane. It does not use Fluent typography components for prose — Fluent's `Text` component is for UI labels, not long-form reading.

## Component strategy

| Docs surface | Fluent components | Notes |
|---|---|---|
| App shell | `FluentProvider` + theme | Root wrapper, theme context |
| Global header | `Toolbar`, `ToolbarButton`, `Text`, `Avatar` | Fixed top bar |
| Left navigation | `Tree`, `TreeItem`, `TreeItemLayout`, `NavDrawer` | Collapsible nested sections |
| Breadcrumbs | `Breadcrumb`, `BreadcrumbItem`, `BreadcrumbButton` | Path from root to current page |
| Search | `SearchBox`, `Dialog`, `DialogSurface` | Command palette pattern |
| Version switcher | `Dropdown`, `Option` | Branch/tag selector in header |
| Page actions | `Button`, `SplitButton`, `Menu`, `MenuItem` | Edit, share, history, feedback |
| Metadata panel | `Card`, `InfoLabel`, `Tag`, `Badge` | Right pane page metadata |
| Tabs | `TabList`, `Tab` | Content sections, API/example toggle |
| Admin tables | `Table`, `TableHeader`, `TableRow`, `TableCell` | Settings pages, index listings |
| Dialogs | `Dialog`, `DialogSurface`, `DialogTitle`, `DialogActions` | Settings, confirm, review |
| Notifications | `Toast`, `Toaster`, `MessageBar` | Inline and transient status |
| Comments | Custom component + `Card`, `Textarea`, `Button` | Review/feedback panel |
| Code blocks | Custom (Shiki/Prism) | Not Fluent — scoped to content pane |
| Diagrams | Custom (Mermaid embed) | Not Fluent — scoped to content pane |

## Accessibility requirements

| Requirement | Standard | Implementation |
|---|---|---|
| Compliance level | WCAG 2.2 AA | All interactive elements meet AA contrast, focus, and labeling |
| Keyboard navigation | Full | All navigation, actions, and dialogs operable via keyboard. Focus traps in dialogs. Skip-to-content link. |
| Screen reader | ARIA landmarks + live regions | Nav is `<nav>`, content is `<main>`, header is `<header>`. Status changes announced via `aria-live`. |
| High contrast | `teamsHighContrastTheme` | Toggle in settings. All Fluent components support it natively. Custom content styles must also respect it. |
| Reduced motion | `prefers-reduced-motion` | All animations and transitions respect the OS-level reduced motion preference. |
| Focus indicators | Visible focus rings | Fluent v9 provides default focus indicators. Never suppress them. |
| Color independence | No color-only meaning | Status, errors, and categories use icons and text in addition to color. |

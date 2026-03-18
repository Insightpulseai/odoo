# Fluent docs component map

Maps every docs UI surface to its Fluent UI React v9 component (or marks it as custom).

## Component mapping

| Surface | Fluent component | Import path | Notes |
|---|---|---|---|
| App shell | `FluentProvider` + `webLightTheme` / `webDarkTheme` | `@fluentui/react-components` | Root provider. Wraps entire app. Theme switching via state. |
| Global header | `Toolbar` + `ToolbarButton` + `Text` + `Avatar` | `@fluentui/react-components` | Fixed top bar. Logo, search trigger, version selector, user menu. |
| Left navigation | `Tree` + `TreeItem` + `TreeItemLayout` | `@fluentui/react-components` | Collapsible sections. Nested to 3 levels max. |
| Nav drawer (mobile) | `NavDrawer` + `NavDrawerBody` | `@fluentui/react-nav-preview` | Slide-in drawer on viewports below 768px. |
| Breadcrumbs | `Breadcrumb` + `BreadcrumbItem` + `BreadcrumbButton` | `@fluentui/react-components` | Shows path from root to current page. Last item is plain text, not a link. |
| Content area | Custom | N/A | Markdown renderer (remark/rehype pipeline). Scoped CSS. Not a Fluent component. |
| Right TOC | `Tree` (flat, lightweight) | `@fluentui/react-components` | On-this-page sidebar. Single-level tree of heading anchors. Highlights active section on scroll. |
| Search | `SearchBox` + `Dialog` + `DialogSurface` | `@fluentui/react-components` | Command palette pattern. `Ctrl+K` / `Cmd+K` shortcut. Results rendered in dialog body. |
| Version switcher | `Dropdown` + `Option` | `@fluentui/react-components` | Reads `versions.json`. Triggers navigation to versioned path. |
| Page actions | `Button` + `SplitButton` + `Menu` + `MenuItem` | `@fluentui/react-components` | Edit on GitHub, copy link, share, view history, submit feedback. |
| Metadata panel | `Card` + `CardHeader` + `InfoLabel` + `Tag` + `Badge` | `@fluentui/react-components` | Right pane below TOC. Shows last updated, contributors, tags, status. |
| Tabs | `TabList` + `Tab` | `@fluentui/react-components` | Used for content sections (overview/API/examples) and settings panels. |
| Tables (admin) | `Table` + `TableHeader` + `TableHeaderCell` + `TableRow` + `TableCell` + `TableBody` | `@fluentui/react-components` | Index pages, settings, contributor lists. Sortable headers where needed. |
| Dialogs | `Dialog` + `DialogSurface` + `DialogTitle` + `DialogBody` + `DialogActions` | `@fluentui/react-components` | Settings, confirmation, review submission, history viewer. |
| Notifications | `Toast` + `Toaster` + `useToastController` | `@fluentui/react-components` | Transient feedback: copied link, saved settings, error states. |
| Message bars | `MessageBar` + `MessageBarBody` + `MessageBarTitle` | `@fluentui/react-components` | Persistent inline feedback: version archived banner, deprecation notice. |
| Comments | Custom + `Card` + `Textarea` + `Button` | Mixed | Review/feedback panel. Custom layout, Fluent primitives for inputs and containers. |
| Code blocks | Custom (Shiki or Prism) | N/A | Syntax-highlighted code. Copy button uses Fluent `Button`. Language label uses Fluent `Badge`. |
| Diagrams | Custom (Mermaid) | N/A | Rendered in an iframe or shadow DOM. Not Fluent. Themed to match current Fluent theme tokens. |
| Tooltip | `Tooltip` | `@fluentui/react-components` | Used on icon-only buttons and truncated labels. |
| Spinner | `Spinner` | `@fluentui/react-components` | Loading states for search results, content fetches, lazy-loaded sections. |
| Divider | `Divider` | `@fluentui/react-components` | Section separators in nav, metadata panel, and settings. |

## Custom component contracts

Components marked "custom" must still follow these rules:

1. **Theme tokens**: Use Fluent design tokens (`tokens.colorNeutralForeground1`, etc.) for colors, spacing, and typography. Never hardcode hex values.
2. **CSS scoping**: Custom components scope their styles to avoid leaking into Fluent components. Use CSS modules or `data-*` attribute selectors.
3. **Accessibility**: Custom components meet the same WCAG 2.2 AA bar as Fluent components. Keyboard navigation, ARIA attributes, focus management.
4. **Dark mode**: Custom components must respond to the active Fluent theme. Read tokens from `FluentProvider` context.
5. **High contrast**: Custom components must be tested with `teamsHighContrastTheme` and respect `forced-colors` media query.

## Package dependencies

```json
{
  "@fluentui/react-components": "^9.x",
  "@fluentui/react-nav-preview": "^0.x",
  "@fluentui/react-icons": "^2.x"
}
```

Icons use `@fluentui/react-icons`. Prefer semantic icon names (`SearchRegular`, `EditRegular`, `ShareRegular`) over generic ones.

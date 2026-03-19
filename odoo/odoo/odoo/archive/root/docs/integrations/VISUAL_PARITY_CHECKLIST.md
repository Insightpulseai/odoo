# Visual Parity Checklist

Mapping of Supabase Docs UI elements to implemented components.

## Header (`DocsHeader.tsx`)

| Supabase Element | Implemented | Component/Notes |
|------------------|-------------|-----------------|
| Wordmark + DOCS label | ✅ | Logo SVG + `docsLabel` prop |
| Primary nav items | ✅ | `navItems` prop with defaults |
| Search box | ✅ | SearchModal with placeholder |
| Keyboard shortcut (⌘K) | ✅ | useEffect keydown listener |
| Dashboard link | ✅ | External link with icon |
| Mobile menu toggle | ✅ | Hamburger icon button |
| Sticky header | ✅ | `sticky top-0 z-50` |
| Backdrop blur | ✅ | `backdrop-blur supports-[backdrop-filter]` |

## Sidebar (`DocsSidebar.tsx`)

| Supabase Element | Implemented | Component/Notes |
|------------------|-------------|-----------------|
| Section headers with icons | ✅ | `NavSection.icon` + SectionIcon |
| Expand/collapse sections | ✅ | Accordion with chevron rotation |
| Hierarchical nesting | ✅ | `NavItem.children` support |
| Active route highlighting | ✅ | `isActive` / `isActiveParent` checks |
| Auto-expand on path match | ✅ | useEffect with pathname detection |
| Sticky positioning | ✅ | `sticky top-14` |
| Independent scroll | ✅ | `overflow-y-auto` |
| Border separator | ✅ | `border-r border-border` |
| Mobile drawer | ✅ | Transform animation + backdrop |

## Content Area (`DocsShell.tsx`)

| Supabase Element | Implemented | Component/Notes |
|------------------|-------------|-----------------|
| Page title (H1) | ✅ | `title` prop |
| Description text | ✅ | `description` prop |
| Prose styling | ✅ | Tailwind prose classes |
| Max width constraint | ✅ | `max-w-4xl` |
| Edit on GitHub link | ✅ | `editUrl` prop + icon |
| Feedback widget | ✅ | Thumbs up/down buttons |
| Responsive padding | ✅ | `px-6 py-8 lg:px-8 lg:py-10` |

## Table of Contents (`DocsToc.tsx`)

| Supabase Element | Implemented | Component/Notes |
|------------------|-------------|-----------------|
| "On this page" heading | ✅ | Monospace uppercase style |
| H2/H3 heading list | ✅ | `headings` prop |
| Scroll-spy highlighting | ✅ | IntersectionObserver |
| Smooth scroll on click | ✅ | `scrollToHeading` function |
| Nested indentation (H3) | ✅ | `ml-3` for level 3 |
| Sticky positioning | ✅ | `sticky top-20` |
| Border separator | ✅ | `border-l border-border` |
| Video preview (optional) | ✅ | YouTube thumbnail expandable |
| Quick links section | ✅ | Help/Changelog/Status links |

## Footer (`DocsFooter.tsx`)

| Supabase Element | Implemented | Component/Notes |
|------------------|-------------|-----------------|
| Primary links with icons | ✅ | Card layout with descriptions |
| Copyright notice | ✅ | Dynamic year + company |
| Secondary nav links | ✅ | Contributing/Styleguide/OSS |
| Social links | ✅ | Twitter/GitHub/Discord/YouTube |
| Responsive layout | ✅ | Grid + flex on breakpoints |
| Border separator | ✅ | `border-t border-border` |

## Responsive Behavior

| Breakpoint | Sidebar | TOC | Status |
|------------|---------|-----|--------|
| Mobile (<640px) | Drawer | Hidden | ✅ |
| Tablet (640-1023px) | Drawer | Hidden | ✅ |
| Desktop (≥1024px) | Fixed | Visible | ✅ |

## Dark Mode

| Element | CSS Variable | Status |
|---------|--------------|--------|
| Background | `--background` | ✅ |
| Foreground | `--foreground` | ✅ |
| Muted | `--muted` | ✅ |
| Border | `--border` | ✅ |
| Brand link | `--brand-link` | ✅ |
| Foreground light | `--foreground-light` | ✅ |

## Remaining Items (Future)

- [ ] Breadcrumbs component with collapse behavior
- [ ] Search index integration (Algolia/Meilisearch)
- [ ] Feedback submission API
- [ ] Video preview expand animation
- [ ] Playwright visual regression tests

---

*Generated: 2026-01-24*

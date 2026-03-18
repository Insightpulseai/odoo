# IPAI Design Extraction

Screenshot → Wireframe → Component Map → Tokens pipeline for UI parity work.

## Directory Structure

```
design/
├── inputs/              # Source screenshots (PNG/JPG)
├── wireframe/           # Layout specifications (JSON)
├── tokens/              # Component tokens (JSON)
├── components/          # Component registry & bindings (JSON)
├── schema.wireframe.json  # Wireframe JSON schema
└── schema.tokens.json     # Tokens JSON schema
```

## Workflow

### 1. Capture Screenshots

Place reference screenshots in `design/inputs/`:

```bash
cp "/path/to/Screenshot_M365_Planner.png" design/inputs/
```

### 2. Extract Wireframe

Create layout specification from screenshot:

```json
{
  "screen": "m365_planner",
  "viewport": { "width": 2048, "height": 1280 },
  "nodes": [
    {
      "id": "shell",
      "type": "AppShell",
      "frame": { "x": 0, "y": 0, "w": 2048, "h": 1280 },
      "children": ["topbar", "sidebar", "content"]
    }
  ]
}
```

### 3. Define Component Tokens

Create Fluent UI v9-style tokens:

```json
{
  "screen": "m365_planner",
  "globals": {
    "color.brand.primary": "#6264A7",
    "radius.md": 4
  },
  "components": {
    "Button": {
      "tokens": { "height": 36, "radius": "{radius.md}" },
      "states": { "hover": { "bg": "{color.brand.primaryHover}" } }
    }
  }
}
```

### 4. Implement Components

Use wireframe + tokens to build UI:

- **Odoo**: Apply via `ipai_design_system` module
- **React/Next.js**: Import `tokens.json`, generate CSS vars
- **Tailwind**: Create token-based theme config

## Node Types

| Type | Description |
|------|-------------|
| AppShell | Root layout container |
| Header | Top navigation bar |
| Sidebar | Left navigation panel |
| NavList | Navigation menu list |
| NavItem | Single navigation item |
| Toolbar | Action bar with buttons |
| Content | Main content area |
| Card | Container with elevation |
| Table | Data table |
| Kanban | Kanban board |
| EmptyState | Empty state placeholder |
| Button | Action button |
| Input | Text input field |
| Avatar | User avatar with presence |
| Copilot | AI assistant components |

## Token Resolution

Tokens use `{reference}` syntax for composition:

```json
{
  "globals": {
    "color.brand.primary": "#6264A7",
    "radius.md": 4
  },
  "components": {
    "Button": {
      "tokens": {
        "bg": "{color.brand.primary}",
        "radius": "{radius.md}"
      }
    }
  }
}
```

## Available Specs

| Screen | Wireframe | Tokens |
|--------|-----------|--------|
| M365 Planner | `wireframe/m365_planner.shell.json` | `tokens/m365_planner.tokens.json` |

## Integration with ipai_design_system

The extracted tokens feed into the Odoo design system:

1. **Globals** → `tokens.css` custom properties
2. **Components** → `components.css` class definitions
3. **Export** → `tokens.json` for portals

---

*See: `addons/ipai/ipai_design_system/` for implementation*

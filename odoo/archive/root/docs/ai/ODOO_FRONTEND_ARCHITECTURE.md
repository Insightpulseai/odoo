---
status: complete
related_skills:
  - odoo-owl-components
  - odoo-js-modules
  - odoo-hoot-testing
last_updated: 2026-02-09
---

# Odoo Frontend Architecture Reference

Complete guide to Odoo 19 frontend architecture, covering Owl framework, JavaScript modules, services, and testing.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Odoo Web Client                          │
├─────────────────────────────────────────────────────────────┤
│  Owl Components Layer                                        │
│  - Component lifecycle                                       │
│  - Template rendering                                        │
│  - State management                                          │
├─────────────────────────────────────────────────────────────┤
│  JavaScript Module System                                    │
│  - Module loading & bundling                                 │
│  - Dependency injection                                      │
│  - Code splitting                                            │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                               │
│  - ORM, RPC, HTTP                                           │
│  - Notification, Dialog, Action                             │
│  - Router, User, Company                                     │
├─────────────────────────────────────────────────────────────┤
│  Registry System                                             │
│  - Actions, Fields, Views                                    │
│  - Services, Commands                                        │
│  - Main Components                                           │
├─────────────────────────────────────────────────────────────┤
│  Backend Integration                                         │
│  - JSON-RPC protocol                                         │
│  - WebSocket (longpolling)                                   │
│  - Asset management                                          │
└─────────────────────────────────────────────────────────────┘
```

## Core Technologies

| Technology | Purpose | Documentation |
|------------|---------|---------------|
| **Owl** | Reactive component framework | `odoo-owl-components` skill |
| **ES6 Modules** | Code organization | `odoo-js-modules` skill |
| **HOOT** | Testing framework | `odoo-hoot-testing` skill |
| **QWeb** | Template engine | XML templates |
| **SCSS** | Styling | Bootstrap-based |

## Project Structure

```
my_addon/
├── __manifest__.py              # Asset declarations
├── static/
│   └── src/
│       ├── components/          # Owl components
│       │   ├── component_name/
│       │   │   ├── component_name.js
│       │   │   └── component_name.xml
│       │   └── index.js
│       ├── models/              # Data models
│       │   └── index.js
│       ├── services/            # Services
│       │   └── index.js
│       ├── utils/               # Utilities
│       │   └── index.js
│       ├── views/               # View definitions
│       │   └── index.js
│       └── scss/                # Styles
│           └── main.scss
└── tests/                       # Test files
    └── component_name.test.js
```

## Development Workflow

1. **Create Component** → Define class + template
2. **Register Component** → Add to registry
3. **Write Tests** → HOOT test suite
4. **Add to Assets** → Declare in manifest
5. **Use in Views** → Reference in XML

## Key Concepts

### Component Lifecycle
1. `setup()` - Initialize state, services
2. `onWillStart` - Load async data
3. `onMounted` - DOM ready
4. `onWillUpdateProps` - Props changing
5. `onWillUnmount` - Cleanup

### State Management
- `useState()` - Reactive state
- Props for parent-child communication
- Events for child-parent communication
- Services for global state

### Service Pattern
- Singleton instances
- Dependency injection
- Lazy loading
- Lifecycle management

## Integration Points

### Backend ↔ Frontend
```javascript
// ORM service for database operations
this.orm = useService("orm");
await this.orm.searchRead("model.name", domain, fields);

// RPC service for custom methods
this.rpc = useService("rpc");
await this.rpc("/my/custom/route", { params });
```

### Views ↔ Components
```xml
<!-- Register widget -->
<field name="field_name" widget="my_widget"/>
```

```javascript
// Register widget
registry.category("fields").add("my_widget", MyWidget);
```

## Best Practices

✅ **DO:**
- Use `/** @odoo-module **/` directive
- Define props with types
- Mock services in tests
- Keep components focused
- Use hooks for reusable logic

❌ **DON'T:**
- Mix business logic in templates
- Access DOM directly (use refs)
- Forget to cleanup in `onWillUnmount`
- Skip testing
- Create circular dependencies

## Performance

### Optimization Techniques
1. **Memoization** - `useMemo()` for expensive computations
2. **Lazy Loading** - Dynamic imports for heavy components
3. **Code Splitting** - Separate bundles per route
4. **Debouncing** - Delay frequent operations
5. **Virtual Scrolling** - Large lists

### Asset Optimization
```python
'assets': {
    'web.assets_backend': [
        'my_addon/static/src/**/*.js',
        ('lazy', 'my_addon/static/src/heavy/*.js'),  # Lazy load
    ],
}
```

## Testing Strategy

### Test Pyramid
```
      ╱╲
     ╱  ╲      E2E Tests (10%)
    ╱────╲     Integration Tests (20%)
   ╱──────╲    Unit Tests (70%)
  ╱────────╲
```

### Coverage Goals
- Unit Tests: >80%
- Integration Tests: >60%
- E2E Tests: Critical paths

## Common Patterns

### Data Loading
```javascript
setup() {
    this.state = useState({ data: [], loading: false });
    onWillStart(this.loadData.bind(this));
}

async loadData() {
    this.state.loading = true;
    this.state.data = await this.orm.searchRead(...);
    this.state.loading = false;
}
```

### Form Handling
```javascript
async onSubmit() {
    try {
        await this.orm.create("model", [this.state.formData]);
        this.notification.add("Saved!", { type: "success" });
    } catch (error) {
        this.notification.add(error.message, { type: "danger" });
    }
}
```

### Modal Pattern
```javascript
this.dialog.add(MyDialog, {
    props: { data },
    onConfirm: this.onModalConfirm.bind(this),
});
```

## Debugging

### Browser DevTools
```javascript
// In console
odoo.__DEBUG__.services  // List services
odoo.loader.modules      // List modules
```

### Component Debugging
```xml
<t t-debug=""/>  <!-- Pause template rendering -->
```

### Test Debugging
```javascript
import { pause } from "@odoo/hoot";
await pause();  // Pause test execution
```

## Migration Guide

### From Legacy (JS classes) to Owl

**Before (Legacy):**
```javascript
var MyWidget = Widget.extend({
    init: function() {
        this._super.apply(this, arguments);
    },
});
```

**After (Owl):**
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";

export class MyWidget extends Component {
    setup() {
        // Initialization
    }
}
```

## Resources

### Skills
- `~/.claude/superclaude/skills/odoo/odoo-owl-components/`
- `~/.claude/superclaude/skills/odoo/odoo-js-modules/`
- `~/.claude/superclaude/skills/odoo/odoo-hoot-testing/`

### Documentation
- [Odoo Web Framework](https://www.odoo.com/documentation/19.0/developer/reference/frontend/)
- [Owl Framework](https://github.com/odoo/owl)
- [JavaScript Reference](https://www.odoo.com/documentation/19.0/developer/reference/frontend/javascript.html)

### Examples
- Core Odoo modules: `/addons/web/static/src/`
- Community examples: OCA repositories

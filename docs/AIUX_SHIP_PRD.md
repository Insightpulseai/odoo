# AIUX Shipping PRD

**Version:** 1.0.0
**Target:** Odoo 18 CE (self-hosted)
**Last Updated:** 2026-01-07

---

## Executive Summary

This document defines the canonical shipping bundle for the IPAI AIUX (AI User Experience) stack on Odoo 18 Community Edition. The bundle includes design tokens, React widget components, and Odoo theme integration with an AI chat assistant.

### Key Constraints (Non-Negotiable)

1. **NO Enterprise modules** - CE/OCA only
2. **NO Odoo S.A. AI** - No IAP, Agent Studio, or odoo.com dependencies
3. **Self-hosted only** - No SaaS or cloud dependencies
4. **Deterministic** - Clean DB install must be reproducible in CI

---

## 1. Mode Naming Convention (CRITICAL FIX)

### Problem Statement

Previous specifications used inconsistent mode naming:
- Types defined: `'minimize' | 'popup' | 'fullscreen'`
- Spec described: `minimize`, `popup`, `side panel`

### Resolution

**Canonical Mode Type:**
```typescript
type Mode = 'minimize' | 'popup' | 'sidepanel';
```

| Mode | Description | Behavior |
|------|-------------|----------|
| `minimize` | Collapsed pill | Floating button, tooltip on hover |
| `popup` | Floating window | Draggable chat popup, 400x500px |
| `sidepanel` | Full side panel | Docked panel, resizable width |

**IMPORTANT:** Never use `fullscreen` - use `sidepanel` for the docked panel mode.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIUX Stack                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   packages/                                                      │
│   ├── ipai-design-tokens/     → CSS/SCSS/Tailwind tokens        │
│   │   ├── tokens.css          → CSS custom properties           │
│   │   ├── tokens.scss         → SCSS variables                  │
│   │   └── tailwind.preset.js  → Tailwind integration            │
│   │                                                              │
│   └── ask-ai-react/           → React widget (optional)         │
│       ├── AskAI.tsx           → Main component                  │
│       └── modes/              → minimize/popup/sidepanel        │
│                                                                  │
│   addons/ipai/                                                   │
│   ├── ipai_theme_aiux/        → Odoo 18 theme                   │
│   │   └── static/src/         → SCSS + JS assets                │
│   │                                                              │
│   └── ipai_aiux_chat/         → Chat widget + API               │
│       ├── controllers/        → /api/ai/chat endpoint           │
│       └── static/src/         → OWL widget                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Design Tokens

**Package:** `@ipai/design-tokens`
**Location:** `packages/ipai-design-tokens/`

**Outputs:**
- `tokens.css` - CSS custom properties with `--aiux-` prefix
- `tokens.scss` - SCSS variables with `$aiux-` prefix
- `tailwind.preset.js` - Tailwind theme extension

**Token Categories:**
```css
/* Colors */
--aiux-color-background-canvas: #ffffff;
--aiux-color-background-sidebar: #fafafa;
--aiux-color-background-card: #ffffff;
--aiux-color-foreground-primary: #1a1a1a;
--aiux-color-accent-primary: #0066cc;

/* Spacing */
--aiux-spacing-xs: 4px;
--aiux-spacing-sm: 8px;
--aiux-spacing-md: 16px;
--aiux-spacing-lg: 24px;
--aiux-spacing-xl: 32px;

/* Border Radius */
--aiux-borderRadius-md: 8px;
--aiux-borderRadius-lg: 12px;
--aiux-borderRadius-xl: 16px;
--aiux-borderRadius-full: 9999px;

/* Shadows */
--aiux-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--aiux-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--aiux-shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Animation */
--aiux-animation-duration-fast: 150ms;
--aiux-animation-duration-normal: 300ms;
--aiux-animation-easing-default: cubic-bezier(0.4, 0, 0.2, 1);
```

### 3.2 AskAI Widget Interface

**TypeScript Types:**
```typescript
export type Mode = 'minimize' | 'popup' | 'sidepanel';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  thinkingDuration?: number;
}

export interface AskAIProps {
  defaultMode?: Mode;           // Default: 'minimize'
  apiEndpoint?: string;         // Default: '/api/ai/chat'
  context?: Record<string, unknown>;
  placeholder?: string;
  accentColor?: string;
  zIndex?: number;
  onMessage?: (message: Message) => void;
  onModeChange?: (mode: Mode) => void;
  onError?: (error: Error) => void;
}
```

### 3.3 Odoo Theme Module

**Module:** `ipai_theme_aiux`
**Location:** `addons/ipai/ipai_theme_aiux/`

**Manifest:**
```python
{
    "name": "IPAI Theme AIUX",
    "version": "18.0.1.0.0",
    "category": "Theme/Backend",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "ipai_theme_aiux/static/src/scss/aiux_tokens.scss",
            "ipai_theme_aiux/static/src/scss/layout.scss",
            "ipai_theme_aiux/static/src/scss/sidebar.scss",
            "ipai_theme_aiux/static/src/scss/cards.scss",
            "ipai_theme_aiux/static/src/scss/forms.scss",
            "ipai_theme_aiux/static/src/scss/ask_ai.scss",
            "ipai_theme_aiux/static/src/js/sidebar_toggle.js",
        ]
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
```

### 3.4 AIUX Chat Module

**Module:** `ipai_aiux_chat`
**Location:** `addons/ipai/ipai_aiux_chat/`

**API Endpoint:**
```
POST /api/ai/chat
Content-Type: application/json

Request:
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "context": {
    "res_model": "sale.order",
    "res_id": 123
  }
}

Response:
{
  "content": "...",
  "model": "internal",
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0
  }
}
```

---

## 4. Acceptance Criteria

### AC-001: Token Build
- [ ] `pnpm run build:tokens` produces `tokens.css`, `tokens.scss`, `tailwind.preset.js`
- [ ] All tokens use `--aiux-` prefix in CSS
- [ ] All tokens use `$aiux-` prefix in SCSS

### AC-002: Mode Types
- [ ] Mode type is `'minimize' | 'popup' | 'sidepanel'` (NOT fullscreen)
- [ ] Default mode is `minimize`
- [ ] Mode transitions preserve conversation context

### AC-003: Sidebar Toggle
- [ ] Sidebar collapse state persists in localStorage
- [ ] Tooltip shows on collapsed menu items
- [ ] Smooth animation on toggle

### AC-004: Theme Installation
- [ ] `ipai_theme_aiux` installs without errors
- [ ] Assets compile to `web.assets_backend`
- [ ] No 500 errors on asset endpoints

### AC-005: Chat Widget
- [ ] OWL widget renders in backend
- [ ] `/api/ai/chat` endpoint responds
- [ ] Messages display with proper formatting

### AC-006: Clean Install
- [ ] Fresh database install passes
- [ ] Module upgrade is idempotent
- [ ] No Python tracebacks in logs

---

## 5. Canonical Runtime Configuration

### 5.1 Database Configuration

```ini
[options]
db_host = db
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
db_name = odoo
dbfilter = ^(odoo|insightpulse)$
list_db = False
```

**Critical Points:**
- `db_host` must match Docker service name (`db`)
- `dbfilter` must explicitly list allowed databases
- `list_db = False` prevents database enumeration
- Password from environment variable, never hardcoded

### 5.2 Logging Configuration

```ini
log_level = info
log_handler = :INFO
logfile = /var/log/odoo/odoo.log
```

**Production Settings:**
- Use `info` level, not `debug`
- Log to file for persistence
- Rotate logs with logrotate

### 5.3 Performance Configuration

```ini
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_time_cpu = 600
limit_time_real = 1200
```

---

## 6. Avoiding Asset 500 Errors

### 6.1 Root Causes

Asset 500 errors typically occur due to:

1. **Missing dependencies** - SCSS imports not found
2. **Syntax errors** - Invalid SCSS/JS syntax
3. **Circular imports** - Asset bundle dependency loops
4. **Permission issues** - Static files not readable

### 6.2 Prevention Checklist

- [ ] Verify all SCSS imports exist before deployment
- [ ] Run `odoo-bin --dev=all` locally to validate assets
- [ ] Check file permissions (755 for directories, 644 for files)
- [ ] Ensure addons path is correctly configured
- [ ] Clear asset cache after deployment: `DELETE FROM ir_attachment WHERE name LIKE 'web.assets%'`

### 6.3 Debugging Commands

```bash
# Check asset compilation
docker exec odoo-core odoo-bin shell -d odoo -c "
from odoo.addons.base.models.assetsbundle import AssetsBundle
bundle = AssetsBundle('web.assets_backend', [])
print(bundle.css())
"

# Verify static files exist
docker exec odoo-core find /mnt/extra-addons -name "*.scss" | head -20

# Check for syntax errors
docker exec odoo-core python3 -c "
import sass
sass.compile(filename='/mnt/extra-addons/ipai/ipai_theme_aiux/static/src/scss/layout.scss')
"
```

---

## 7. Installation Order

```yaml
# Phase 1: Odoo base
- base
- web
- mail

# Phase 2: OCA base
- base_technical_user
- base_view_inheritance_extension
- web_responsive

# Phase 3: OCA accounting (if needed)
- account_financial_report

# Phase 4: IPAI core
- ipai_dev_studio_base
- ipai_workspace_core
- ipai_ce_branding

# Phase 5: IPAI theme
- ipai_theme_aiux

# Phase 6: IPAI AIUX
- ipai_aiux_chat
- ipai_ask_ai
- ipai_ask_ai_chatter
```

---

## 8. Verification Gates

| Gate | Command | Expected |
|------|---------|----------|
| Clean Install | `odoo-bin -d test -i base --stop-after-init` | Exit 0 |
| Upgrade Idempotent | `odoo-bin -d test -u all --stop-after-init` (x2) | Exit 0 both times |
| Assets Build | `curl -sf localhost:8069/web/assets/backend` | HTTP 200 |
| Login Page | `curl -sf localhost:8069/web/login` | HTTP 200 |
| No Tracebacks | `docker logs odoo \| grep Traceback` | Empty |

---

## 9. CI/CD Integration

The `aiux-ship-gate.yml` workflow validates:

1. **Database Setup** - Creates fresh PostgreSQL + Odoo
2. **Module Installation** - Installs in defined order
3. **Asset Verification** - Checks all asset endpoints
4. **Proof Generation** - Creates `AIUX_SHIP_PROOF.md`

Artifacts produced:
- `docs/releases/AIUX_SHIP_PROOF.md` - Verification results
- `odoo.log` - Full Odoo logs
- `installed_modules.txt` - List of installed modules

---

## 10. Appendix: Mode Naming Migration

If upgrading from a codebase using `fullscreen`:

```bash
# Find all occurrences
grep -r "fullscreen" --include="*.ts" --include="*.tsx" --include="*.js"

# Replace with sidepanel
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  -exec sed -i 's/fullscreen/sidepanel/g' {} +

# Verify no fullscreen references remain
grep -r "fullscreen" --include="*.ts" --include="*.tsx" --include="*.js"
```

---

*This PRD is the canonical reference for AIUX shipping. All implementations must conform to these specifications.*

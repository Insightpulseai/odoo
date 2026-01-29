# InsightPulse AI Design System - Quick Start

You now have **TWO OPTIONS** for using the InsightPulse AI design system:

---

## 🎯 Option 1: React Component (Full-Featured Chat Widget)

**Best for**: React, Next.js, Vite apps

### View Demo NOW
```bash
# Already running at http://localhost:5173/
# Or start it:
cd /Users/tbwa/Documents/GitHub/odoo-ce/packages/ipai-design-tokens
pnpm dev
```

### Use in Your React App
```tsx
import { AIChatWidget } from '@ipai/design-tokens/react/AIChatWidget';

function App() {
  return (
    <div>
      <h1>My App</h1>
      <AIChatWidget />
    </div>
  );
}
```

**Features**:
- ✨ Floating action button (FAB)
- 💬 Expandable chat panel
- ⌨️ Message input with send button
- 🎨 Fluent 2-aligned design tokens
- 📱 Responsive design

---

## 🌐 Option 2: Vanilla CSS Theme (Pure CSS)

**Best for**: WordPress, static sites, vanilla HTML, ANY website

### View Demo NOW
```bash
open /Users/tbwa/Documents/GitHub/odoo-ce/packages/ipai-design-tokens/demo-vanilla.html
```

Or with Python:
```bash
cd /Users/tbwa/Documents/GitHub/odoo-ce/packages/ipai-design-tokens
python3 -m http.server 8000
# Open http://localhost:8000/demo-vanilla.html
```

### Use in Your HTML
```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="insightpulse-ai.css">
</head>
<body>
  <!-- Button -->
  <button class="ipai-btn ipai-btn-primary">Get Started</button>

  <!-- Card -->
  <div class="ipai-card">
    <div class="ipai-card-header">Hello</div>
    <div class="ipai-card-content">World</div>
  </div>

  <!-- Badge -->
  <span class="ipai-badge ipai-badge-ai">✨ AI-Powered</span>

  <!-- Custom styling with CSS variables -->
  <div style="color: var(--ipai-primary-500); padding: var(--ipai-spacing-m);">
    Custom styled content
  </div>
</body>
</html>
```

**Features**:
- 🎨 Complete design token system
- 📦 Pre-built components (buttons, cards, badges, forms)
- 💎 Utility classes
- 🌐 Zero dependencies
- ♿ Accessibility-focused

---

## 📋 Quick Component Reference

### CSS Classes

| Component | Class | Example |
|-----------|-------|---------|
| **Buttons** | `ipai-btn ipai-btn-primary` | Primary button |
| | `ipai-btn ipai-btn-secondary` | Secondary button |
| | `ipai-btn ipai-btn-ai` | AI-themed button |
| **Cards** | `ipai-card` | Card container |
| | `ipai-card-header` | Card title |
| | `ipai-card-content` | Card body |
| **Badges** | `ipai-badge ipai-badge-success` | Green success badge |
| | `ipai-badge ipai-badge-warning` | Orange warning badge |
| | `ipai-badge ipai-badge-error` | Red error badge |
| | `ipai-badge ipai-badge-ai` | Purple AI badge |
| **Forms** | `ipai-input` | Text input field |

### CSS Variables (Design Tokens)

| Category | Variable | Value |
|----------|----------|-------|
| **Colors** | `--ipai-primary-500` | #0073e6 (primary blue) |
| | `--ipai-ai-accent` | #7c3aed (AI purple) |
| | `--ipai-neutral-100` | #1a1a1a (text black) |
| **Typography** | `--ipai-font-size-400` | 16px (body text) |
| | `--ipai-font-weight-semibold` | 600 |
| **Spacing** | `--ipai-spacing-m` | 16px (default) |
| | `--ipai-spacing-xl` | 24px |
| **Shadows** | `--ipai-shadow-8` | Floating elements |

---

## 🎨 Design Token Philosophy

Both implementations use the **same Fluent 2-aligned tokens**:

- **Colors**: Primary (blue), Neutral (grays), AI Accent (purple), Semantic (success/warning/error)
- **Typography**: 9-level scale (100-900) + 4 weights
- **Spacing**: 4px base grid (xxs to xxxl)
- **Elevation**: 4 shadow levels (2, 4, 8, 16)
- **Motion**: 5 duration levels (faster to slower)

---

## 📁 Files

| File | Purpose |
|------|---------|
| `src/react/AIChatWidget.tsx` | React component + tokens |
| `insightpulse-ai.css` | Vanilla CSS theme |
| `demo/` | React demo (Vite) |
| `demo-vanilla.html` | Vanilla CSS demo |
| `README-AICHAT.md` | Full documentation |

---

## 🚀 Next Steps

1. **Choose your option** (React or Vanilla CSS)
2. **View the demo** (already running or open HTML file)
3. **Copy the code** to your project
4. **Customize** using design tokens

---

## 💡 Use Cases

**React Component** ✓
- React apps
- Next.js projects
- Vite-based apps
- TypeScript projects

**Vanilla CSS** ✓
- WordPress themes
- Static HTML sites
- Landing pages
- Marketing pages
- Any website (no build step needed)

---

## ❓ Questions?

See `README-AICHAT.md` for complete documentation including:
- Installation instructions
- Full API reference
- Integration examples
- Browser support
- Customization guide

---

**Built with**: Fluent 2 design principles
**Maintained by**: InsightPulse AI Team

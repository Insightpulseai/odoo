# InsightPulse AI Chat Widget & Design System

This package provides **two ways** to use the InsightPulse AI design system:

1. **React Component** - Full-featured chat widget for React applications
2. **Vanilla CSS Theme** - Pure CSS custom web theme for any website

Both implementations use the same Fluent 2-aligned design tokens for consistency.

---

## Option 1: React Component (for React apps)

### Installation

```bash
# In your React project
pnpm add @ipai/design-tokens
```

### Usage

```tsx
import { AIChatWidget, AIChatWidgetDemo } from '@ipai/design-tokens/react/AIChatWidget';

// Use the chat widget component
function App() {
  return (
    <div>
      <h1>My App</h1>
      <AIChatWidget />
    </div>
  );
}

// Or use the full demo page
function DemoPage() {
  return <AIChatWidgetDemo />;
}
```

### Features

- ✨ Floating Action Button (FAB) with expand/collapse
- 💬 Chat interface with message history
- ⌨️ Text input with send button
- 📱 Responsive design (400px panel width)
- 🎨 Fluent 2-aligned design tokens
- ⚡ Typing indicators
- 🎭 User/assistant message styling

### Customization

The component exports `insightPulseTokens` for customization:

```tsx
import { insightPulseTokens } from '@ipai/design-tokens/react/AIChatWidget';

// Access design tokens
const primaryColor = insightPulseTokens.colors.primary[500];
const spacing = insightPulseTokens.spacing.m;
```

---

## Option 2: Vanilla CSS Theme (for any website)

### Installation

1. Download `insightpulse-ai.css` from this package
2. Include in your HTML:

```html
<link rel="stylesheet" href="insightpulse-ai.css">
```

### Features

- 🎨 Complete design token system (colors, typography, spacing)
- 📦 Pre-built components (buttons, cards, badges, forms)
- 💎 Utility classes for quick styling
- 🌐 Works with vanilla HTML, WordPress, static sites, etc.
- ♿ Accessibility-focused

### Component Classes

#### Buttons
```html
<button class="ipai-btn ipai-btn-primary">Primary Button</button>
<button class="ipai-btn ipai-btn-secondary">Secondary Button</button>
<button class="ipai-btn ipai-btn-ai">✨ AI Action</button>
```

#### Cards
```html
<div class="ipai-card">
  <div class="ipai-card-header">Card Title</div>
  <div class="ipai-card-content">Card content goes here</div>
</div>
```

#### Badges
```html
<span class="ipai-badge ipai-badge-success">✓ Success</span>
<span class="ipai-badge ipai-badge-warning">⚠ Warning</span>
<span class="ipai-badge ipai-badge-error">✕ Error</span>
<span class="ipai-badge ipai-badge-ai">✨ AI</span>
```

#### Form Inputs
```html
<input type="text" class="ipai-input" placeholder="Enter text...">
```

### Design Tokens (CSS Variables)

All tokens are available as CSS custom properties:

```css
/* Colors */
--ipai-primary-500: #0073e6;
--ipai-neutral-100: #1a1a1a;
--ipai-ai-accent: #7c3aed;

/* Typography */
--ipai-font-size-400: 16px;
--ipai-font-weight-semibold: 600;

/* Spacing */
--ipai-spacing-m: 16px;
--ipai-spacing-xl: 24px;

/* Elevation */
--ipai-shadow-8: 0 0 2px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.14);
```

### Utility Classes

```html
<!-- Typography -->
<p class="ipai-text-600 ipai-font-semibold">Large semibold text</p>

<!-- Spacing -->
<div class="ipai-p-m ipai-m-l">Padding medium, margin large</div>

<!-- Elevation -->
<div class="ipai-shadow-8">Floating element</div>

<!-- Border Radius -->
<div class="ipai-rounded-large">Rounded corners</div>
```

---

## Local Development

### React Component Demo

```bash
cd packages/ipai-design-tokens
pnpm install
pnpm dev
```

Open http://localhost:5173/ to see the React demo.

### Vanilla CSS Demo

```bash
cd packages/ipai-design-tokens
open demo-vanilla.html
```

Or serve with any static file server:

```bash
python3 -m http.server 8000
# Open http://localhost:8000/demo-vanilla.html
```

---

## Design Token System

### Color Palette

**Primary Brand Colors** (Blue scale 50-900)
- Primary: `#0073e6` (500)
- Used for: Buttons, links, focus states

**Neutral Grays** (0-100)
- White: `#ffffff` (0)
- Black: `#1a1a1a` (100)
- Used for: Text, backgrounds, borders

**Semantic Colors**
- Success: `#107c10`
- Warning: `#faa500`
- Error: `#d13438`
- Info: `#0078d4`
- AI Accent: `#7c3aed` (purple)

### Typography Scale

Based on Fluent 2 with 9 levels (100-900):
- 100: 10px (tiny labels)
- 200: 12px (captions)
- 300: 14px (small text)
- 400: 16px (body text - default)
- 500: 20px (subheadings)
- 600: 24px (headings)
- 700: 28px (large headings)
- 800: 32px (display text)
- 900: 40px (hero text)

### Spacing Scale

4px base grid:
- xxs: 4px
- xs: 8px
- s: 12px
- m: 16px (default)
- l: 20px
- xl: 24px
- xxl: 32px
- xxxl: 40px

### Elevation (Shadows)

4 levels for depth hierarchy:
- 2: Subtle (hover states)
- 4: Cards, buttons
- 8: Floating elements, FAB
- 16: Modals, dialogs

### Motion/Duration

5 speed levels:
- faster: 50ms
- fast: 100ms
- normal: 200ms (default)
- slow: 300ms
- slower: 400ms

---

## Integration Examples

### WordPress Theme

```php
// functions.php
function enqueue_insightpulse_theme() {
  wp_enqueue_style(
    'insightpulse-ai',
    get_template_directory_uri() . '/assets/insightpulse-ai.css',
    array(),
    '1.0.0'
  );
}
add_action('wp_enqueue_scripts', 'enqueue_insightpulse_theme');
```

### Next.js App

```tsx
// _app.tsx
import '@ipai/design-tokens/insightpulse-ai.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}
```

### Vite/Vite-based Apps

```tsx
// main.tsx
import '@ipai/design-tokens/insightpulse-ai.css';
```

### Static HTML

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.example.com/insightpulse-ai.css">
</head>
<body>
  <button class="ipai-btn ipai-btn-primary">Get Started</button>
</body>
</html>
```

---

## Browser Support

- Chrome/Edge: ✅ Last 2 versions
- Firefox: ✅ Last 2 versions
- Safari: ✅ Last 2 versions
- Mobile Safari/Chrome: ✅ iOS 14+, Android 10+

Uses modern CSS features:
- CSS Custom Properties (variables)
- CSS Grid
- Flexbox
- Border radius
- Box shadow

---

## File Structure

```
packages/ipai-design-tokens/
├── src/
│   └── react/
│       └── AIChatWidget.tsx      # React component
├── demo/
│   ├── index.html                # React demo entry
│   └── main.tsx                  # React demo app
├── insightpulse-ai.css          # Vanilla CSS theme ⭐
├── demo-vanilla.html            # Vanilla CSS demo ⭐
├── vite.config.ts               # Vite config for demos
└── README-AICHAT.md             # This file
```

---

## License

Part of the InsightPulse AI monorepo. See root LICENSE file.

---

## Questions?

- React component issues: Check `src/react/AIChatWidget.tsx`
- CSS theme issues: Check `insightpulse-ai.css`
- Design tokens: All tokens use `--ipai-` prefix
- Examples: `demo-vanilla.html` (vanilla) or `pnpm dev` (React)

---

**Maintained by**: InsightPulse AI Team
**Design System**: Fluent 2-aligned
**Version**: 0.5.0

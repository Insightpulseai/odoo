# InsightPulse AI Theme System for Odoo

Multi-aesthetic theme system with 10 distinct themes for Odoo 18+ backend.

## Overview

This module provides a comprehensive theme system inspired by modern AI applications, offering 5 aesthetic systems with light and dark modes each.

### Theme Architecture

**5 Aesthetic Systems × 2 Color Modes = 10 Themes**

| Aesthetic | Light Mode | Dark Mode | Inspiration |
|-----------|------------|-----------|-------------|
| **Default** | ✅ Bright, clean | ✅ High contrast | InsightPulse AI brand |
| **Dull** | ✅ Soft, low contrast | ✅ Muted, eye-friendly | Low-fatigue design |
| **Claude** | ✅ Warm, paper-like | ✅ Warm dark depth | Claude AI aesthetic |
| **ChatGPT** | ✅ Cool, professional | ✅ Cool dark minimal | ChatGPT aesthetic |
| **Gemini** | ✅ Bright, colorful | ✅ Dark gradient | Google Gemini aesthetic |

## Features

### 🎨 Live Theme Switcher

- **Aesthetic Selector**: Dropdown in Odoo navbar with emoji indicators
- **Light/Dark Toggle**: Quick toggle button with sun/moon icons
- **Real-time Switching**: No page reload required
- **LocalStorage Persistence**: Theme preferences saved automatically
- **System Integration**: Detects and respects OS dark mode preference

### 🎯 Design Token System

All themes use consistent CSS custom properties:

```css
--theme-background          /* Main background color */
--theme-surface             /* Card/panel surfaces */
--theme-surface-elevated    /* Dropdowns, modals */
--theme-text                /* Primary text */
--theme-text-secondary      /* Secondary text */
--theme-text-tertiary       /* Tertiary text */
--theme-border              /* Border colors */
--theme-primary             /* Primary brand color */
--theme-primary-hover       /* Primary hover state */
--theme-ai-accent           /* AI-specific elements */
--theme-ai-accent-light     /* AI backgrounds */
```

### 📦 Odoo Component Coverage

- ✅ Forms and sheets
- ✅ Lists and tables
- ✅ Kanban views
- ✅ Cards and panels
- ✅ Navigation bars
- ✅ Buttons and inputs
- ✅ Dropdowns and popovers
- ✅ Modals and dialogs
- ✅ Status bars
- ✅ Chatter
- ✅ Control panels
- ✅ Notifications

## Installation

### 1. Install Module

```bash
# Via Odoo CLI
odoo -d your_database -i ipai_theme_fluent2

# Or via Odoo UI
Apps → Search "IPAI Fluent 2" → Install
```

### 2. Verify Installation

After installation, you should see:
- Theme switcher controls in top-right navbar (before systray items)
- Aesthetic dropdown with emoji indicators (🎨 Default, 🌫️ Dull, etc.)
- Light/Dark toggle button with sun/moon icon

## Usage

### In Odoo UI

**Switch Aesthetic**:
1. Click aesthetic dropdown in navbar
2. Select desired aesthetic system
3. Theme applies immediately

**Toggle Light/Dark**:
1. Click light/dark button in navbar
2. Mode switches instantly
3. Preference saved automatically

### Programmatic API

Access the theme system via browser console or Odoo services:

```javascript
// Get theme manager instance
const themeManager = window.IpaiThemeSystem;

// Get current theme
const current = themeManager.getCurrentTheme();
console.log(current);
// { aesthetic: 'claude', colorMode: 'dark', themeMode: 'claude-dark' }

// Set specific theme
themeManager.setTheme('gemini', 'light');

// Toggle light/dark mode
themeManager.toggleColorMode();

// Get available options
console.log(themeManager.getAvailableAesthetics());
// ['default', 'dull', 'claude', 'chatgpt', 'gemini']

console.log(themeManager.getAvailableColorModes());
// ['light', 'dark']
```

### Custom Event Listener

Listen for theme changes in your custom modules:

```javascript
document.addEventListener('ipai-theme-changed', (event) => {
    console.log('Theme changed:', event.detail);
    // { aesthetic: 'claude', colorMode: 'dark', themeMode: 'claude-dark' }

    // Perform custom actions on theme change
    updateCustomComponents(event.detail);
});
```

## Theme Descriptions

### Default Aesthetic

**Light Mode**: Bright, clean InsightPulse AI brand aesthetic
- Background: Pure white (#ffffff)
- Primary: InsightPulse blue (#0073e6)
- AI Accent: Purple (#7c3aed)

**Dark Mode**: High contrast, modern dark theme
- Background: Near black (#0d0d0d)
- Primary: Bright blue (#4da6ff)
- AI Accent: Light purple (#a78bfa)

### Dull Aesthetic

**Light Mode**: Soft, low-contrast, easy on eyes
- Muted background (#e8e8e8)
- Reduced contrast for extended use
- Softer primary colors

**Dark Mode**: Muted dark, reduced eye strain
- Less extreme contrast than default dark
- Comfortable for night-time use

### Claude Aesthetic

**Light Mode**: Warm, sophisticated, paper-like
- Cream background (#faf9f7)
- Warm primary colors (amber/orange)
- Elegant, professional feel

**Dark Mode**: Warm dark, sophisticated depth
- Warm dark tones (brown-black)
- Maintains sophistication in dark mode

### ChatGPT Aesthetic

**Light Mode**: Cool, professional, minimal
- Clean white surfaces
- Teal/green primary (#10a37f)
- Professional, minimalist feel

**Dark Mode**: Cool dark, professional depth
- Cool dark grays
- Bright teal accents

### Gemini Aesthetic

**Light Mode**: Bright, colorful, Google-inspired
- Google Material white
- Blue primary colors (#1a73e8)
- Playful, modern feel

**Dark Mode**: Dark gradient, playful depth
- Dark Material Design grays
- Vibrant blue accents

## Development

### Adding Custom Theme Support

To make your custom module respect the theme system:

```css
/* In your module's CSS */
.my_custom_component {
    background-color: var(--theme-surface);
    color: var(--theme-text);
    border: 1px solid var(--theme-border);
}

.my_custom_component:hover {
    background-color: var(--theme-surface-elevated);
}

.my_custom_button {
    background-color: var(--theme-primary);
    color: #ffffff;
}

.my_custom_button:hover {
    background-color: var(--theme-primary-hover);
}
```

### Theme Detection in JavaScript

```javascript
const html = document.documentElement;
const aesthetic = html.getAttribute('data-aesthetic');
const colorMode = html.getAttribute('data-color-mode');

console.log(`Current theme: ${aesthetic}-${colorMode}`);
```

## Compatibility

- **Odoo Version**: 19.0+ (also compatible with 18.0)
- **Browser Support**: Modern browsers with CSS custom properties support
  - Chrome/Edge 49+
  - Firefox 31+
  - Safari 9.1+
- **Dependencies**: `web` module (Odoo core)

## Technical Details

### Files Structure

```
ipai_theme_fluent2/
├── __manifest__.py                        # Module configuration
├── __init__.py
├── README.md                              # This file
└── static/src/
    ├── css/
    │   ├── fluent2.css                   # Official Fluent 2 tokens
    │   ├── tokens.css                    # IPAI semantic tokens
    │   ├── theme.css                     # Original theme implementation
    │   └── theme-system.css              # Multi-aesthetic theme system
    └── js/
        ├── theme.js                      # Original theme manager
        └── theme-system.js               # Theme system manager
```

### Data Attributes

Themes are applied via HTML data attributes:

```html
<html data-aesthetic="claude" data-color-mode="dark">
```

### LocalStorage Keys

- `ipai-aesthetic`: Stores selected aesthetic (default/dull/claude/chatgpt/gemini)
- `ipai-color-mode`: Stores color mode preference (light/dark)

## Troubleshooting

### Theme Switcher Not Appearing

1. Check if module is installed: Apps → IPAI Fluent 2 Theme Tokens
2. Clear browser cache and hard refresh (Ctrl+Shift+R)
3. Check browser console for JavaScript errors
4. Verify assets are loaded: Inspect → Network → CSS/JS files

### Theme Not Persisting

1. Check browser LocalStorage is enabled
2. Open browser console and check:
   ```javascript
   localStorage.getItem('ipai-aesthetic');
   localStorage.getItem('ipai-color-mode');
   ```
3. Clear LocalStorage and set theme again

### Custom Components Not Themed

Ensure your CSS uses theme variables:
```css
/* ❌ Wrong - hardcoded colors */
.my_component { background: #ffffff; }

/* ✅ Correct - theme variables */
.my_component { background: var(--theme-surface); }
```

## License

AGPL-3

## Author

InsightPulse AI - https://insightpulseai.net

## Support

For issues and feature requests, please contact InsightPulse AI support or open an issue in the project repository.

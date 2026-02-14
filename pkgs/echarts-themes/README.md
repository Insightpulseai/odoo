# @ipai/echarts-themes

Unified ECharts theme system for InsightPulse AI - Single source of truth for Superset, Odoo, React apps, and dev tools.

## Features

- ✅ **6 Professional Themes**: dark, shine, vintage, roma, macarons, infographic (Apache ECharts official themes)
- ✅ **TypeScript Support**: Full type definitions for theme objects and metadata
- ✅ **Multiple Loaders**: Browser (dynamic import), Node.js (static import), CDN (fetch)
- ✅ **Tree-Shakeable**: ESM + CJS builds with code splitting support
- ✅ **Zero Dependencies**: Only peer dependency on `echarts` 5.5+
- ✅ **Theme Metadata**: Rich metadata with colors, categories, descriptions

## Installation

```bash
npm install @ipai/echarts-themes echarts
# or
pnpm add @ipai/echarts-themes echarts
# or
yarn add @ipai/echarts-themes echarts
```

## Usage

### Browser (Dynamic Import)

Recommended for React/Vue/Angular apps with code splitting:

```typescript
import * as echarts from 'echarts';
import { loadTheme } from '@ipai/echarts-themes';

// Load theme dynamically
const { theme, metadata } = await loadTheme('dark');

// Register with ECharts
echarts.registerTheme('dark', theme);

// Use theme
const chart = echarts.init(container, 'dark');
chart.setOption({ /* your chart config */ });
```

### Node.js (Static Import)

For SSR, build tools, or when you need synchronous access:

```typescript
import * as echarts from 'echarts';
import { loadThemeSync, darkTheme } from '@ipai/echarts-themes/node';

// Option 1: Use loader
const { theme, metadata } = loadThemeSync('dark');
echarts.registerTheme('dark', theme);

// Option 2: Direct import
echarts.registerTheme('dark', darkTheme);
```

### CDN Fallback

For loading themes from external CDN:

```typescript
import { loadThemeFromCDN } from '@ipai/echarts-themes/cdn';

const { theme, metadata } = await loadThemeFromCDN('dark', {
  cdnUrl: 'https://cdn.jsdelivr.net/npm/@ipai/echarts-themes@1.0.0/dist/themes',
  timeout: 10000,
});

echarts.registerTheme('dark', theme);
```

### Direct Theme Import

For maximum performance when you know which theme you need:

```typescript
import * as echarts from 'echarts';
import { darkTheme, shineTheme, vintageTheme } from '@ipai/echarts-themes';

// Register themes
echarts.registerTheme('dark', darkTheme);
echarts.registerTheme('shine', shineTheme);
echarts.registerTheme('vintage', vintageTheme);

// Use theme
const chart = echarts.init(container, 'dark');
```

## Available Themes

| Theme | Category | Dark Mode | Description |
|-------|----------|-----------|-------------|
| `dark` | dark | ✅ | Modern dark mode with vibrant accent colors |
| `shine` | light | ❌ | Clean, professional theme with blue dominance |
| `vintage` | light | ❌ | Retro, muted colors with warm cream background |
| `roma` | colorful | ❌ | Elegant theme with sophisticated pink, navy, and sage |
| `macarons` | colorful | ❌ | Playful pastel colors for friendly dashboards |
| `infographic` | colorful | ❌ | Bright, colorful theme perfect for presentations |

## Theme Metadata

Access theme metadata for UI selectors, documentation, or theme management:

```typescript
import {
  getThemeIds,
  getThemeMetadata,
  getThemesByCategory,
  getDarkModeThemes,
  getLightModeThemes,
} from '@ipai/echarts-themes';

// Get all theme IDs
const themeIds = getThemeIds(); // ['dark', 'shine', 'vintage', ...]

// Get specific theme metadata
const darkMeta = getThemeMetadata('dark');
console.log(darkMeta.colors); // ['#4992ff', '#7cffb2', ...]

// Filter themes by category
const colorfulThemes = getThemesByCategory('colorful');

// Filter by dark mode
const darkThemes = getDarkModeThemes();
const lightThemes = getLightModeThemes();
```

## TypeScript

Full TypeScript support with type definitions:

```typescript
import type { ThemeId, ThemeMetadata, EChartsTheme } from '@ipai/echarts-themes';

const themeId: ThemeId = 'dark'; // Type-safe theme ID
const metadata: ThemeMetadata = getThemeMetadata(themeId)!;
const theme: EChartsTheme = darkTheme;
```

## Integration Examples

### React with Theme Selector

```typescript
import { useState, useEffect } from 'react';
import * as echarts from 'echarts';
import { loadTheme, getThemeIds } from '@ipai/echarts-themes';

function ChartWithThemeSelector() {
  const [theme, setTheme] = useState('dark');
  const themeIds = getThemeIds();

  useEffect(() => {
    const loadAndRegister = async () => {
      const { theme: themeObj } = await loadTheme(theme);
      echarts.registerTheme(theme, themeObj);

      const chart = echarts.init(container, theme);
      chart.setOption({ /* config */ });
    };
    loadAndRegister();
  }, [theme]);

  return (
    <div>
      <select value={theme} onChange={(e) => setTheme(e.target.value)}>
        {themeIds.map(id => (
          <option key={id} value={id}>{id}</option>
        ))}
      </select>
      <div ref={container} style={{ width: '100%', height: '400px' }} />
    </div>
  );
}
```

### Odoo/Python Integration

```python
# In Odoo controller or script
from pathlib import Path
import json

themes_pkg = Path(__file__).parent / "static/lib/echarts-themes"
with open(themes_pkg / "themes.json") as f:
    themes_metadata = json.load(f)

# Pass to template
theme_ids = [t["id"] for t in themes_metadata["themes"]]
```

### Superset Plugin

```python
# superset_config.py
CUSTOM_VIZ_MANIFEST = {
    "echarts_custom": {
        "id": "echarts_custom",
        "name": "ECharts Custom",
        "themes": ["dark", "shine", "vintage", "roma", "macarons", "infographic"]
    }
}
```

## Build Configuration

This package uses `tsup` for building. The build outputs:

- **ESM**: `dist/*.mjs` - Modern ES modules
- **CJS**: `dist/*.js` - CommonJS for Node.js
- **Types**: `dist/*.d.ts` - TypeScript definitions

## License

Apache License 2.0 (matches Apache ECharts official themes)

## Credits

- Themes based on [Apache ECharts Official Themes](https://echarts.apache.org/en/theme-builder.html)
- Maintained by InsightPulse AI

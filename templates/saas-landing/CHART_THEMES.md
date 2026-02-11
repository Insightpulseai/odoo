# ECharts Theme Library

Professional chart themes for SaaS landing page dashboards and analytics.

## 📊 Available Themes (6)

### 1. Infographic
**Best for**: Presentations, Reports, Marketing dashboards

**Color Palette**:
- Primary: `#C1232B` (Red) • `#27727B` (Teal) • `#FCCE10` (Yellow)
- Accent: `#E87C25` (Orange) • `#B5C334` (Lime) • `#FE8463` (Coral)
- Extended: `#9BCA63` • `#FAD860` • `#F3A43B` • `#60C0DD`

**Use Cases**: High-impact presentations, colorful reports, marketing analytics

---

### 2. Vintage
**Best for**: Historical data, Classic reports, Print-friendly

**Color Palette**:
- Muted: `#d87c7c` (Dusty Rose) • `#919e8b` (Sage) • `#d7ab82` (Tan)
- Neutral: `#6e7074` (Gray) • `#61a0a8` (Teal Gray)
- Background: `#fef8ef` (Cream)

**Use Cases**: Traditional reports, historical analysis, print documents

---

### 3. Dark ⭐
**Best for**: Modern dashboards, Night mode, Technical interfaces

**Color Palette**:
- Vibrant: `#4992ff` (Blue) • `#7cffb2` (Mint) • `#fddd60` (Yellow)
- Accent: `#ff6e76` (Pink) • `#58d9f9` (Cyan) • `#05c091` (Green)
- Background: `#100C2A` (Dark Purple)

**Dark Mode**: Yes
**Use Cases**: Modern SaaS dashboards, developer tools, night-mode analytics

---

### 4. Roma
**Best for**: Executive dashboards, Elegant presentations, Brand-focused

**Color Palette**:
- Signature: `#E01F54` (Pink) • `#001852` (Navy) • `#f5e8c8` (Cream)
- Sophisticated: `#b8d2c7` (Sage) • `#c6b38e` (Beige) • `#a4d8c2` (Mint)

**Use Cases**: Executive reporting, luxury brands, elegant presentations

---

### 5. Shine (Default)
**Best for**: Business dashboards, Financial reports, Clean interfaces

**Color Palette**:
- Professional: `#c12e34` (Red) • `#e6b600` (Gold) • `#0098d9` (Blue)
- Accent: `#2b821d` (Green) • `#005eaa` (Navy) • `#339ca8` (Teal)

**Use Cases**: Business intelligence, financial dashboards, clean corporate UIs

---

### 6. Macarons
**Best for**: User-friendly dashboards, SaaS platforms, Engaging reports

**Color Palette**:
- Pastel: `#2ec7c9` (Teal) • `#b6a2de` (Lavender) • `#5ab1ef` (Sky Blue)
- Friendly: `#ffb980` (Peach) • `#d87a80` (Rose) • `#8d98b3` (Blue Gray)

**Use Cases**: Consumer SaaS, user engagement dashboards, approachable analytics

---

## 🚀 Usage

### Basic Implementation

```typescript
import { CHART_THEMES, loadEChartsTheme } from '@/lib/chart-themes'

// Load a theme
await loadEChartsTheme('dark')

// Initialize ECharts with theme
const chart = echarts.init(container, 'dark')
```

### Theme Selector Component

```tsx
'use client'
import { useState } from 'react'
import { CHART_THEMES, loadEChartsTheme } from '@/lib/chart-themes'

export function ThemeSelector() {
  const [theme, setTheme] = useState('shine')

  const handleThemeChange = async (themeId: string) => {
    await loadEChartsTheme(themeId)
    setTheme(themeId)
    // Reinitialize charts with new theme
  }

  return (
    <select value={theme} onChange={(e) => handleThemeChange(e.target.value)}>
      {Object.values(CHART_THEMES).map(t => (
        <option key={t.id} value={t.id}>{t.name}</option>
      ))}
    </select>
  )
}
```

### Dashboard Integration

```tsx
'use client'
import { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import { loadEChartsTheme } from '@/lib/chart-themes'

export function DashboardChart({ theme = 'shine' }) {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const init = async () => {
      await loadEChartsTheme(theme)

      const chart = echarts.init(chartRef.current!, theme)
      chart.setOption({
        title: { text: 'Platform Metrics' },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: [150, 230, 224, 218, 135] }]
      })
    }

    init()
  }, [theme])

  return <div ref={chartRef} style={{ width: '100%', height: '400px' }} />
}
```

---

## 📁 File Structure

```
public/themes/echarts/
├── infographic.js    # Bright colorful theme
├── vintage.js        # Retro muted theme
├── dark.js           # Dark mode theme
├── roma.js           # Elegant sophisticated theme
├── shine.js          # Clean professional theme (default)
├── macarons.js       # Pastel friendly theme
└── themes.json       # Theme metadata

lib/
└── chart-themes.ts   # TypeScript configuration and helpers
```

---

## 🎨 Design System Integration

### Tailwind CSS Classes

Generate Tailwind classes from theme palettes:

```typescript
import { CHART_THEMES } from '@/lib/chart-themes'

const themeColors = Object.entries(CHART_THEMES).reduce((acc, [id, theme]) => {
  acc[id] = theme.colorPalette
  return acc
}, {} as Record<string, string[]>)

// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        chart: themeColors
      }
    }
  }
}
```

### CSS Custom Properties

```css
:root {
  --chart-color-1: #c12e34;
  --chart-color-2: #e6b600;
  --chart-color-3: #0098d9;
  /* ... */
}

[data-theme="dark"] {
  --chart-color-1: #4992ff;
  --chart-color-2: #7cffb2;
  --chart-color-3: #fddd60;
  /* ... */
}
```

---

## 🔧 Configuration

### Theme Metadata

Located at: `public/themes/echarts/themes.json`

```json
{
  "themes": [
    {
      "id": "dark",
      "name": "Dark",
      "file": "dark.js",
      "colors": ["#4992ff", "#7cffb2", "..."],
      "darkMode": true
    }
  ]
}
```

### TypeScript Types

```typescript
interface ChartTheme {
  id: string
  name: string
  description: string
  colorPalette: string[]
  backgroundColor?: string
  darkMode?: boolean
  category: 'light' | 'dark' | 'colorful' | 'minimal'
  bestFor: string[]
}
```

---

## 📊 Apache Superset Integration

### Custom Chart Themes

To use in Apache Superset:

1. Upload theme files to Superset static assets
2. Configure in `superset_config.py`:

```python
CHART_THEMES = {
    'default': 'shine',
    'available': [
        'infographic', 'vintage', 'dark',
        'roma', 'shine', 'macarons'
    ]
}
```

3. Reference theme in chart JSON:

```json
{
  "theme": "dark",
  "vizType": "echarts_timeseries"
}
```

---

## 🧪 Testing

### Preview All Themes

```bash
cd templates/saas-landing
npm run dev
# Navigate to: http://localhost:3000/dashboard?theme=dark
```

### Visual Comparison

```tsx
import { CHART_THEMES } from '@/lib/chart-themes'

export function ThemePreview() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {Object.values(CHART_THEMES).map(theme => (
        <div key={theme.id}>
          <h3>{theme.name}</h3>
          <div className="flex gap-1">
            {theme.colorPalette.slice(0, 5).map(color => (
              <div
                key={color}
                style={{ backgroundColor: color }}
                className="w-8 h-8 rounded"
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

---

## 📚 Resources

- **ECharts Documentation**: https://echarts.apache.org/en/theme-builder.html
- **Official Themes**: https://github.com/apache/echarts/tree/master/theme
- **Theme Builder**: https://echarts.apache.org/en/theme-builder.html
- **Apache License**: https://www.apache.org/licenses/LICENSE-2.0

---

## ✅ Next Steps

1. **Install ECharts**: `npm install echarts`
2. **Load Theme**: Use `loadEChartsTheme()` helper
3. **Initialize Chart**: `echarts.init(container, 'dark')`
4. **Add Theme Selector**: Dropdown in dashboard UI
5. **Persist Preference**: Save to localStorage or user settings
6. **Integrate with Odoo**: Sync theme preference via API

---

**Theme Library Version**: 1.0.0
**Last Updated**: 2026-02-11
**License**: Apache-2.0

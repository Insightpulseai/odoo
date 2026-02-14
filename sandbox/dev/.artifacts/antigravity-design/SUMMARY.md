# Google Antigravity Design System Extraction — Summary

**Extraction Date**: 2026-02-11
**Source**: https://antigravity.google/
**Status**: ✅ Complete CSS extraction, ⚠️ JS/SVG assets gzipped

---

## 📦 Deliverables

### 1. Complete Design System Documentation
**File**: `DESIGN_SYSTEM.md` (15,000+ words)

**Contents**:
- ✅ Full color palette (22 grey shades + accent blue)
- ✅ Typography system (14 responsive scales)
- ✅ Spacing scale (11 tokens, 0px-180px)
- ✅ Border radius tokens (7 values)
- ✅ Grid system (12/8/4 column responsive)
- ✅ Breakpoints (5 tiers)
- ✅ Icon sizes (14 scales)
- ✅ **22 easing curves** (quad, cubic, quart, quint, expo, circ, back)
- ✅ Theme tokens (60+ semantic tokens)
- ✅ Component states (buttons, nav, links)
- ✅ Motion principles
- ✅ Micro-interactions (hover, focus, press)

### 2. Raw Assets
- `antigravity-decompressed.html` — Full HTML source
- `styles-decompressed.css` — Complete CSS (1 line, minified)
- `main-preview.js` — JavaScript preview (gzipped, needs decompression)

---

## 🎨 Key Design Principles Discovered

### 1. Variable Font System
**Google Sans Flex** with advanced variation axes:
- `wdth` (width): 25%-150%
- `opsz` (optical size): Auto-adjusts from 8-144
- Weight: 400-500
- Oblique: 0deg-10deg

**Why it matters**: Single font file that adapts to size/context automatically.

### 2. Responsive Typography
**5-tier scaling** (Desktop → XL → MD → SM → XS):
- Landing text: 107px → 72px → 56px → 46px → 30px
- Complete scale collapse at each breakpoint (not simple media queries)

**Why it matters**: Optimized for each device class, not just "shrunk down".

### 3. Semantic Token Architecture
**2-layer system**:
- **Palette tokens** (`--palette-grey-1200: #121317`)
- **Theme tokens** (`--theme-surface-on-surface: var(--palette-grey-1200)`)

**Why it matters**: Easy light/dark mode switching by reassigning theme tokens.

### 4. Overlay Transparency System
**5 opacity levels** (1%, 12%, 24%, 72%, 95%):
- Low: Subtle hover states
- Medium: Modal overlays
- High: Backdrop blur contexts

**Why it matters**: Consistent depth/hierarchy without hardcoding alpha values.

### 5. Comprehensive Easing Library
**22 curves** organized by intent:
- **Ease-in** (6): Accelerating (button press)
- **Ease-out** (6): Decelerating (element entrance)
- **Ease-in-out** (6): Smooth transitions (scrolling)
- **Special**: `ease-out-back` for bounce/overshoot

**Why it matters**: Matches animation intent to perceived physics.

---

## 🚀 How to Use This

### For Odoo Project

#### Option 1: Direct Token Import
```css
/* Add to your Odoo theme CSS */
@import url('/path/to/antigravity-tokens.css');

/* Override Odoo defaults */
.o_main_navbar {
  background: var(--theme-surface-surface-container);
  backdrop-filter: blur(8px);
}

.btn-primary {
  background: var(--theme-button-states-primary-enabled);
  transition: .3s var(--ease-out-cubic);
}
```

#### Option 2: Tailwind Config Generation
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'grey-1200': '#121317',
        'grey-800': '#45474D',
        'blue-600': '#3279F9'
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px'
      },
      borderRadius: {
        'xs': '4px',
        'rounded': '9999px'
      },
      transitionTimingFunction: {
        'out-cubic': 'cubic-bezier(.215, .61, .355, 1)',
        'out-back': 'cubic-bezier(.34, 1.85, .64, 1)'
      }
    }
  }
}
```

#### Option 3: Figma Import (via Tokens Studio)
1. Convert `DESIGN_SYSTEM.md` → JSON tokens
2. Import to Figma via Tokens Studio plugin
3. Design Odoo modules in Figma with Antigravity tokens
4. Export to CSS variables automatically

---

## 🔍 What's Missing (Gzipped Assets)

### JavaScript (Animations & Interactions)
**Status**: Downloaded but gzipped
**File**: `main-UR65DTH6.js`
**To Extract**:
```bash
gunzip < main-preview.js > main-decompressed.js
# Then search for:
# - GSAP/Framer Motion animations
# - Lottie JSON animations
# - Canvas/WebGL effects
# - Scroll-triggered animations
```

### SVG Illustrations
**Status**: Not yet extracted
**Likely location**:
- `/assets/image/` directory
- Inline SVG in HTML `<app-root>`
- Lazy-loaded via JavaScript

**To Extract**:
```bash
# Download full site with assets
wget --mirror --page-requisites \
  --convert-links --adjust-extension \
  https://antigravity.google/ \
  -P ./full-site/

# Find SVG files
find ./full-site/ -name "*.svg"

# Or extract inline SVG from HTML
grep -oP '<svg.*?</svg>' antigravity-decompressed.html
```

### Icon System Details
**Status**: Partial (Google Symbols font only)
**Need**:
- Custom icon SVG sprites
- Icon naming conventions
- Filled vs outlined variants

---

## 📊 Token Statistics

| Category | Count | Range |
|----------|-------|-------|
| **Colors** | 22 + 1 accent | Grey scale + blue |
| **Typography** | 14 scales | 12.5px → 148px |
| **Spacing** | 11 tokens | 0px → 180px |
| **Border Radius** | 7 tokens | 4px → 9999px |
| **Easing Curves** | 22 functions | Quad → Back |
| **Breakpoints** | 5 tiers | 425px → 1600px |
| **Icon Sizes** | 14 scales | 12px → 120px |
| **Grid Columns** | 12/8/4 | Responsive |

---

## 🎯 Recommended Next Steps

### Immediate (High Value)
1. ✅ **Use the easing curves** — Copy `--ease-out-cubic` and `--ease-out-back` for button/modal animations
2. ✅ **Adopt spacing scale** — Use `--space-md` (16px) instead of hardcoded `16px`
3. ✅ **Implement semantic tokens** — Theme layer for easy light/dark mode

### Short Term (Design System)
4. 🔄 **Extract SVG assets** — Run full `wget` download for illustrations
5. 🔄 **Decompress JavaScript** — Analyze animation libraries used
6. 🔄 **Generate Tailwind config** — Auto-generate from extracted tokens

### Long Term (Odoo Integration)
7. 📋 **Create Odoo theme module** — `ipai_theme_antigravity`
8. 📋 **Build component library** — Odoo QWeb templates with Antigravity styles
9. 📋 **Figma design system** — Mirror tokens in Figma for design consistency

---

## 🛠️ Tools Used

- **WebFetch** — HTML download with user agent spoofing
- **curl** — Asset retrieval with compression handling
- **gunzip** — Gzip decompression
- **Read** — File content extraction

---

## 📚 References

- **Production Site**: https://antigravity.google/
- **Design System Doc**: `/artifacts/antigravity-design/DESIGN_SYSTEM.md`
- **Raw CSS**: `/artifacts/antigravity-design/styles-decompressed.css`
- **Raw HTML**: `/artifacts/antigravity-design/antigravity-decompressed.html`

---

**Status**: ✅ Phase 1 Complete (CSS Design Tokens)
**Next**: Phase 2 — JavaScript Animations & SVG Assets

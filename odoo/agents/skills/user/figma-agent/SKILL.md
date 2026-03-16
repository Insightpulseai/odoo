# Comprehensive Figma Agent Skill for Claude

**SKILL.md — Design-to-Production Code Pipeline v1.0**

This specification defines a unified Figma agent skill that maximizes design-to-code productivity through intelligent use of MCP tools, design system extraction, accessibility automation, and integration with existing frontend architectures including Odoo, React/Tailwind, and shadcn/ui component libraries.

---

## Summary

The complete skill operates across six interconnected workflows:

A production-ready Figma agent must bridge design intent and code reality through systematic extraction of design context, intelligent mapping to component libraries, and accessibility-compliant code generation. This skill leverages Figma's native MCP server tools alongside established design token pipelines to produce code that respects existing design system conventions while maintaining **100% design fidelity**.

The agent workflow follows a clear progression: **context acquisition → design system extraction → component mapping → code generation → accessibility validation**. Each phase has specific tool calls, decision points, and output formats optimized for the target framework.

---

## Workflow 1: Design Context Acquisition Strategy

### Available Figma MCP Tools and Optimal Usage Patterns

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_design_context` | Primary extraction of hierarchy, layout, styling | First call for any design implementation |
| `get_metadata` | Sparse XML outline for large designs | When `get_design_context` returns truncated/verbose results |
| `get_screenshot` | Visual reference capture | Always enable unless token-limited |
| `get_code_connect_map` | Figma-to-codebase component mapping | When target codebase has Code Connect configured |
| `get_variable_defs` | Design token extraction | For design system integration |
| `get_figjam` | FigJam diagram extraction | Architecture/flow documentation only |

### Decision Tree for Context Acquisition

```
START
  │
  ├─► Call get_design_context(nodeId/fileUrl)
  │     │
  │     ├─► Response complete? → Proceed to extraction
  │     │
  │     └─► Response truncated/verbose?
  │           │
  │           ├─► Call get_metadata() for structure overview
  │           │
  │           └─► Identify target child nodes → Call get_design_context on each
  │
  ├─► Call get_screenshot() for visual validation reference
  │
  └─► Call get_code_connect_map() if codebase integration exists
```

### Server Configuration

The agent should support both official and community MCP servers:

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/mcp",
      "type": "http"
    },
    "figma-desktop": {
      "url": "http://127.0.0.1:3845/mcp",
      "type": "http"
    },
    "framelink": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--stdio"],
      "env": { "FIGMA_API_KEY": "${FIGMA_API_KEY}" }
    }
  }
}
```

---

## Workflow 2: Design System Extraction Pipeline

### Token Extraction Hierarchy

The agent extracts tokens in a **three-tier architecture** that maps Figma Variables to production code:

**Tier 1 — Primitive tokens** (raw values)
```json
{
  "color": {
    "blue-500": { "$value": "#3B82F6", "$type": "color" },
    "blue-600": { "$value": "#2563EB", "$type": "color" }
  },
  "spacing": {
    "4": { "$value": "16px", "$type": "dimension" },
    "8": { "$value": "32px", "$type": "dimension" }
  }
}
```

**Tier 2 — Semantic tokens** (purpose-driven references)
```json
{
  "color-primary": { "$value": "{color.blue-500}" },
  "color-primary-hover": { "$value": "{color.blue-600}" },
  "spacing-card-padding": { "$value": "{spacing.4}" }
}
```

**Tier 3 — Component tokens** (context-specific)
```json
{
  "button-bg-primary": { "$value": "{color-primary}" },
  "button-bg-primary-hover": { "$value": "{color-primary-hover}" }
}
```

### Transformation to CSS Custom Properties

```css
:root {
  /* Primitives */
  --color-blue-500: #3B82F6;
  --spacing-4: 16px;

  /* Semantic (reference primitives) */
  --color-primary: var(--color-blue-500);
  --spacing-card-padding: var(--spacing-4);

  /* Component tokens */
  --button-bg-primary: var(--color-primary);
}

[data-theme="dark"] {
  --color-primary: var(--color-blue-400);
}
```

### Tailwind Configuration Generation

```javascript
// tailwind.config.js generated from Figma Variables
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--color-primary)',
          hover: 'var(--color-primary-hover)',
          light: 'var(--color-primary-light)',
        }
      },
      spacing: {
        'card': 'var(--spacing-card-padding)',
      },
      borderRadius: {
        'card': 'var(--radius-card)',
      }
    }
  }
}
```

---

## Workflow 3: Component Variant Mapping

### Figma Variants to TypeScript Props Transformation

The agent maps Figma component variants to strongly-typed React props:

**Figma Component Set:**
- `variant=Primary, Secondary, Outline, Ghost`
- `size=sm, md, lg`
- `disabled=True, False`
- `hasIcon=True, False`

**Generated TypeScript interface:**
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  icon?: React.ReactNode;
  children: React.ReactNode;
}
```

### CVA (Class Variance Authority) Pattern for Tailwind

```typescript
import { cva, type VariantProps } from 'class-variance-authority';

const button = cva(
  // Base styles from Figma component
  'inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        sm: 'h-8 px-3 text-sm rounded-md',
        md: 'h-10 px-4 text-base rounded-md',
        lg: 'h-12 px-6 text-lg rounded-lg',
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md'
    }
  }
);

export type ButtonProps = VariantProps<typeof button> & {
  children: React.ReactNode;
};
```

### Auto-Layout to CSS Flexbox/Grid Mapping

| Figma Auto Layout | CSS Equivalent |
|-------------------|----------------|
| Direction: Horizontal | `flex-row` |
| Direction: Vertical | `flex-col` |
| Gap: 16 | `gap-4` |
| Padding: 24 | `p-6` |
| Alignment: Center | `items-center justify-center` |
| Hug contents | `w-fit h-fit` |
| Fill container | `flex-1` or `w-full` |
| Space between | `justify-between` |

---

## Workflow 4: Code Generation by Framework Target

### React + Tailwind CSS Generation Template

```tsx
// Generated from Figma frame: "Card/Product"
// File: components/ProductCard.tsx

import { cn } from '@/lib/utils';

interface ProductCardProps {
  title: string;
  description: string;
  price: number;
  imageUrl: string;
  className?: string;
}

export function ProductCard({
  title,
  description,
  price,
  imageUrl,
  className
}: ProductCardProps) {
  return (
    <article
      className={cn(
        // Layout (from Auto Layout)
        "flex flex-col gap-4",
        // Sizing
        "w-full max-w-sm",
        // Spacing (from Figma padding)
        "p-6",
        // Visual (from Figma fills/effects)
        "bg-card text-card-foreground rounded-lg shadow-md",
        // Interactive
        "hover:shadow-lg transition-shadow",
        className
      )}
    >
      <img
        src={imageUrl}
        alt={title}
        className="w-full h-48 object-cover rounded-md"
      />
      <div className="flex flex-col gap-2">
        <h3 className="text-lg font-semibold text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        <span className="text-xl font-bold text-primary">{price.toLocaleString()}</span>
      </div>
    </article>
  );
}
```

### shadcn/ui Component Mapping

The agent maps Figma components to shadcn/ui primitives:

| Figma Component | shadcn/ui Implementation |
|-----------------|--------------------------|
| Button variants | `<Button variant="default\|destructive\|outline\|secondary\|ghost\|link">` |
| Input fields | `<Input>` with `<Label>` |
| Cards | `<Card>`, `<CardHeader>`, `<CardContent>`, `<CardFooter>` |
| Dialogs/Modals | `<Dialog>`, `<DialogTrigger>`, `<DialogContent>` |
| Dropdowns | `<DropdownMenu>` with Radix primitives |
| Tabs | `<Tabs>`, `<TabsList>`, `<TabsTrigger>`, `<TabsContent>` |
| Select | `<Select>`, `<SelectTrigger>`, `<SelectContent>`, `<SelectItem>` |

### Vanilla HTML/CSS Semantic Output

```html
<!-- Generated semantic HTML from Figma frame -->
<article class="product-card">
  <img src="product.jpg" alt="Product name" class="product-card__image">
  <div class="product-card__content">
    <h3 class="product-card__title">Product Title</h3>
    <p class="product-card__description">Description text here</p>
    <span class="product-card__price">1,299</span>
  </div>
</article>
```

```css
.product-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.product-card__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}
```

---

## Workflow 5: Accessibility Automation

### WCAG Compliance Checklist

The agent validates and generates accessible code against these requirements:

**Color contrast (WCAG 2.1 SC 1.4.3, 1.4.11)**
- Normal text: **4.5:1** minimum (AA), **7:1** (AAA)
- Large text (>=18pt or >=14pt bold): **3:1** minimum
- UI components and graphics: **3:1** minimum

**Touch targets (WCAG 2.2 SC 2.5.8)**
- Minimum size: **24x24 CSS pixels** (AA)
- Recommended: **44x44 CSS pixels** (AAA)

**Focus indicators (WCAG 2.1 SC 2.4.7)**
```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

### Semantic HTML Generation Rules

| Figma Frame Type | Semantic Element | ARIA Role |
|------------------|------------------|-----------|
| Page header with nav | `<header>` + `<nav>` | `banner`, `navigation` |
| Main content area | `<main>` | `main` |
| Independent content block | `<article>` | `article` |
| Sidebar/related content | `<aside>` | `complementary` |
| Page footer | `<footer>` | `contentinfo` |
| List of items | `<ul>`, `<ol>`, `<li>` | `list`, `listitem` |
| Form groups | `<fieldset>` + `<legend>` | `group` |

### ARIA Attribute Automation Patterns

```tsx
// Form field with error handling
<div className="form-group">
  <label htmlFor="email">
    Email <span aria-hidden="true">*</span>
  </label>
  <input
    type="email"
    id="email"
    aria-required="true"
    aria-invalid={hasError}
    aria-describedby="email-hint email-error"
  />
  <span id="email-hint" className="text-sm text-muted-foreground">
    We'll never share your email
  </span>
  {hasError && (
    <span id="email-error" role="alert" className="text-sm text-destructive">
      Please enter a valid email address
    </span>
  )}
</div>

// Modal with focus trap
<Dialog>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent
    aria-labelledby="dialog-title"
    aria-describedby="dialog-description"
  >
    <DialogHeader>
      <DialogTitle id="dialog-title">Confirm Action</DialogTitle>
      <DialogDescription id="dialog-description">
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

---

## Workflow 6: Code Connect Integration

### Code Connect Configuration File

```json
{
  "codeConnect": {
    "parser": "react",
    "include": ["src/components/**/*"],
    "exclude": ["test/**", "docs/**", "build/**"],
    "importPaths": {
      "src/components/*": "@/components"
    }
  }
}
```

### Component Mapping Definition

```typescript
// Button.figma.tsx
import figma from '@figma/code-connect/react';
import { Button } from './Button';

figma.connect(Button, 'https://figma.com/design/.../node-id=123', {
  props: {
    // String extraction
    label: figma.string('Label'),

    // Boolean with conditional rendering
    disabled: figma.boolean('Disabled'),
    icon: figma.boolean('Has Icon', {
      true: <Icon />,
      false: undefined,
    }),

    // Variant enum mapping
    variant: figma.enum('Variant', {
      'Primary': 'default',
      'Secondary': 'secondary',
      'Danger': 'destructive',
      'Outline': 'outline',
    }),

    // Size mapping
    size: figma.enum('Size', {
      'Small': 'sm',
      'Medium': 'default',
      'Large': 'lg',
    }),

    // Instance swap (icon slot)
    leadingIcon: figma.instance('Leading Icon'),
  },

  example: (props) => (
    <Button
      variant={props.variant}
      size={props.size}
      disabled={props.disabled}
    >
      {props.leadingIcon}
      {props.label}
    </Button>
  ),
});
```

---

## Plugin Patterns That Inform Agent Behavior

Analysis of **40+ production Figma plugins** reveals key architectural patterns the agent should incorporate:

### Pattern A: Layer Hierarchy to Code Structure

```
Figma Node Type    →  Code Output
─────────────────────────────────────
Frame              →  <div> / Container component
Text               →  <span> / <p> / <h1-h6>
Rectangle (styled) →  div with CSS classes
SVG/Icon           →  <Icon> component / <svg>
Group              →  Fragment or semantic wrapper
Auto Layout        →  Flexbox container
Component          →  Named React component
```

### Pattern B: Responsive Constraint Inference

The agent infers responsive behavior from Figma constraints:

```typescript
// Figma constraints
{
  horizontal: "SCALE",      // → w-full
  vertical: "FIXED",        // → h-48
  minWidth: 320,            // → min-w-[320px]
  maxWidth: 1200,           // → max-w-screen-xl
}

// Generated Tailwind classes
className="w-full h-48 min-w-[320px] max-w-screen-xl"
```

### Pattern C: Design System Introspection

From Builder.io and Locofy patterns, the agent should detect:

- Component library usage (identify main components vs instances)
- Shared styles/variables (global design tokens)
- Color palette statistics and usage frequency
- Typography scale consistency
- Spacing system enforcement (8pt grid validation)

---

## Odoo Frontend Integration Patterns

For Odoo integration, the agent generates code compatible with Odoo's OWL framework and QWeb templates:

### Form Field Detection Algorithm

```typescript
// Figma layer analysis → Odoo field type mapping
const fieldTypeMap = {
  // Text detection
  'date' in label → 'Date',
  'time' in label → 'Datetime',
  'email' in label → 'Char' + email_validator,
  'currency_symbol' in placeholder → 'Monetary',
  'number' in label → 'Integer' | 'Float',
  hasTextAreaHeight → 'Text',
  hasDropdownIcon → 'Selection',
  isCheckbox → 'Boolean',
  hasRedBorder → required: true,
};
```

### Generated Odoo Model Structure

```python
# Generated from Figma form frame
from odoo import models, fields, api

class CustomForm(models.Model):
    _name = 'custom.form'
    _description = 'Custom Form'

    # From Figma text input labeled "Customer Name"
    customer_name = fields.Char(
        required=True,  # Detected from red border/asterisk
        string='Customer Name'
    )

    # From Figma date picker
    invoice_date = fields.Date(
        required=True,
        string='Invoice Date'
    )

    # From Figma dropdown with currency symbol
    amount_total = fields.Monetary(
        string='Total Amount',
        currency_field='company_currency_id'
    )

    # From Figma checkbox
    is_approved = fields.Boolean(string='Approved')
```

---

## Smart Delta / ipai_* Architecture Compatibility

The agent integrates with the existing Smart Delta architecture for incremental updates:

### Change Detection Workflow

```typescript
interface SmartDeltaContext {
  previousSnapshot: FigmaSnapshot;
  currentSnapshot: FigmaSnapshot;
  changedNodes: string[];
  affectedComponents: ComponentRef[];
}

// Agent detects only changed elements
function calculateDelta(context: SmartDeltaContext) {
  const changes = context.changedNodes.map(nodeId => ({
    nodeId,
    changeType: detectChangeType(nodeId, context),
    affectedFiles: mapToCodeFiles(nodeId),
    suggestedUpdate: generatePatch(nodeId, context),
  }));

  return changes;
}
```

### ipai_* Function Integration

```typescript
// Integration with existing ipai_ pattern
export const ipai_figma_sync = {
  name: 'figma_sync',
  description: 'Sync Figma design changes to codebase',
  parameters: {
    figmaUrl: { type: 'string', required: true },
    targetPath: { type: 'string', required: true },
    framework: { type: 'enum', values: ['react', 'vue', 'html'] },
    includeTokens: { type: 'boolean', default: true },
  },
  execute: async (params) => {
    const context = await getDesignContext(params.figmaUrl);
    const tokens = params.includeTokens ? await getVariableDefs(params.figmaUrl) : null;
    const codeConnect = await getCodeConnectMap(params.figmaUrl);

    return generateCode({
      context,
      tokens,
      codeConnect,
      framework: params.framework,
      targetPath: params.targetPath,
    });
  }
};
```

---

## Icon Library Integration

### Unified Icon Component Pattern

```tsx
import { Icon as Iconify } from '@iconify/react';
import * as LucideIcons from 'lucide-react';

const iconProviders = {
  iconify: (name: string, props: IconProps) => (
    <Iconify icon={name} {...props} />
  ),
  lucide: (name: string, props: IconProps) => {
    const LucideIcon = LucideIcons[name as keyof typeof LucideIcons];
    return LucideIcon ? <LucideIcon {...props} /> : null;
  },
};

// Icon mapping from Figma component names
const figmaToIconMap: Record<string, { provider: string; name: string }> = {
  'icon/arrow-left': { provider: 'lucide', name: 'ArrowLeft' },
  'icon/check': { provider: 'lucide', name: 'Check' },
  'icon/menu': { provider: 'iconify', name: 'mdi:menu' },
};

export function Icon({ figmaName, ...props }: { figmaName: string } & IconProps) {
  const mapping = figmaToIconMap[figmaName];
  if (!mapping) return null;
  return iconProviders[mapping.provider](mapping.name, props);
}
```

---

## Agent Decision Tree for Complete Workflow

```
USER REQUEST: "Generate code from this Figma design"
│
├─► PHASE 1: Context Acquisition
│   ├─ Call get_design_context(url)
│   ├─ Call get_screenshot() for validation
│   ├─ Call get_code_connect_map() if available
│   └─ Call get_variable_defs() for tokens
│
├─► PHASE 2: Analysis
│   ├─ Identify component type (form, card, layout, etc.)
│   ├─ Detect design system patterns (spacing, colors, typography)
│   ├─ Map variants to props
│   └─ Check for existing component mappings in codebase
│
├─► PHASE 3: Framework Selection
│   ├─ React + Tailwind → Generate TSX with utility classes
│   ├─ shadcn/ui → Map to library primitives, extend with variants
│   ├─ Vanilla HTML → Generate semantic markup + CSS custom properties
│   └─ Odoo → Generate models.py + views.xml + security.xml
│
├─► PHASE 4: Code Generation
│   ├─ Apply semantic HTML rules
│   ├─ Map Auto Layout to Flexbox/Grid
│   ├─ Generate TypeScript interfaces from variants
│   ├─ Apply design tokens from get_variable_defs()
│   └─ Include responsive breakpoints
│
├─► PHASE 5: Accessibility Validation
│   ├─ Verify color contrast ratios
│   ├─ Add ARIA attributes
│   ├─ Ensure keyboard navigation support
│   ├─ Validate touch target sizes
│   └─ Generate alt text for images
│
└─► PHASE 6: Output
    ├─ Component code (TSX/HTML/Python)
    ├─ Styling (Tailwind/CSS/SCSS)
    ├─ Type definitions (TypeScript interfaces)
    ├─ Tests (Storybook stories / unit tests)
    └─ Code Connect mapping file (if applicable)
```

---

## Quality Gates Before Output

The agent validates all generated code against these criteria:

- **Design fidelity**: Visual comparison against `get_screenshot()` reference
- **Semantic correctness**: No div soup; proper heading hierarchy
- **Accessibility compliance**: WCAG 2.1 AA minimum
- **Type safety**: All props typed; no `any` types
- **Token usage**: Design values mapped to tokens, not hardcoded
- **Responsive behavior**: Mobile-first, all breakpoints covered
- **Component reuse**: Existing components from Code Connect used where mapped

---

## Usage

### Prerequisites

1. **Figma API Key**: Set `FIGMA_API_KEY` environment variable
2. **MCP Server**: Configure one of the supported MCP servers (see config above)
3. **Target Framework**: Ensure target framework dependencies are installed

### Basic Usage

```bash
# Set environment
export FIGMA_API_KEY="your-figma-api-key"

# Agent will use MCP tools to:
# 1. Extract design context from Figma URL
# 2. Generate code for specified framework
# 3. Validate accessibility compliance
```

### Example Agent Invocation

```
User: Generate a React component from this Figma frame:
      https://www.figma.com/design/ABC123/MyDesign?node-id=1234

Agent: [Executes 6-phase workflow]
       1. Calls get_design_context + get_screenshot
       2. Extracts design tokens via get_variable_defs
       3. Maps to React + Tailwind framework
       4. Generates ProductCard.tsx with TypeScript types
       5. Validates WCAG AA compliance
       6. Outputs component + styles + types
```

---

## Version History

- **1.0.0** (2025-01): Initial skill specification
  - 6-workflow pipeline
  - Multi-framework support (React, Vanilla, Odoo)
  - WCAG 2.1 AA accessibility automation
  - Design token extraction (3-tier architecture)
  - Code Connect integration

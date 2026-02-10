/**
 * IPAI Design Tokens - TypeScript Exports
 * Auto-generated from tokens/source/tokens.json
 * DO NOT EDIT MANUALLY - Run 'pnpm generate:tokens' to regenerate
 */

export const tokens = {
  "color": {
    "bg": "#E7EDF5",
    "surface": "#FFFFFF",
    "canvas": "#F5F8FA",
    "text": {
      "primary": "#0B1F33",
      "secondary": "#4A5F7A",
      "tertiary": "#7A8FA5",
      "onAccent": "#FFFFFF"
    },
    "primary": "#0F2A44",
    "primaryDeep": "#0A1E33",
    "primaryHover": "#1A3A5A",
    "accent": {
      "green": "#7BC043",
      "greenHover": "#6AA638",
      "teal": "#64B9CA",
      "tealHover": "#52A7B8",
      "amber": "#F6C445",
      "amberHover": "#E5B334"
    },
    "semantic": {
      "success": "#7BC043",
      "warning": "#F6C445",
      "error": "#E74C3C",
      "info": "#64B9CA"
    },
    "border": "#D1DCE5",
    "borderLight": "#E7EDF5",
    "borderDark": "#B8C7D6",
    "overlay": "rgba(11, 31, 51, 0.6)"
  },
  "spacing": {
    "gap": "16px",
    "gapSm": "12px",
    "gapLg": "24px"
  },
  "radius": {
    "default": "8px",
    "sm": "4px",
    "lg": "12px",
    "full": "9999px"
  },
  "shadow": {
    "default": "0 4px 12px rgba(11, 31, 51, 0.08)",
    "soft": "0 2px 8px rgba(11, 31, 51, 0.06)",
    "lg": "0 8px 24px rgba(11, 31, 51, 0.12)",
    "inner": "inset 0 2px 4px rgba(11, 31, 51, 0.06)"
  },
  "typography": {
    "fontFamily": {
      "base": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      "mono": "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace"
    }
  }
} as const;

export type Tokens = typeof tokens;

// Convenience type exports
export type ColorTokens = typeof tokens.color;
export type SpacingTokens = typeof tokens.spacing;
export type RadiusTokens = typeof tokens.radius;
export type ShadowTokens = typeof tokens.shadow;
export type TypographyTokens = typeof tokens.typography;

// Individual token access with type safety
export const color = tokens.color;
export const spacing = tokens.spacing;
export const radius = tokens.radius;
export const shadow = tokens.shadow;
export const typography = tokens.typography;

// Default export
export default tokens;

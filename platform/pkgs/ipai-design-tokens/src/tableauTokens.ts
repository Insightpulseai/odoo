/**
 * Tableau Design Tokens - TypeScript Module
 * ==========================================
 * Source: Figma Tableau UI Kit (Community)
 * Generated: 2026-01-21
 *
 * Usage:
 * ```tsx
 * import {
 *   tableauColors,
 *   tableauChartPalette,
 *   createTableauTheme
 * } from '@ipai/design-tokens/tableauTokens';
 *
 * // Use in chart libraries
 * <BarChart colors={tableauChartPalette.categorical} />
 *
 * // Apply to CSS custom properties
 * applyTableauTokensToDocument();
 * ```
 */

import tokensJson from "./tableauTokens.json";

export type TableauTokens = typeof tokensJson;

/** Full tokens object */
export const tableauTokens = tokensJson;

/** Tableau Classic 20 color palette - primary data viz palette */
export const tableauClassic20 = [
  "#1F77B4", // Blue
  "#FF7F0E", // Orange
  "#2CA02C", // Green
  "#D62728", // Red
  "#9467BD", // Purple
  "#8C564B", // Brown
  "#E377C2", // Pink
  "#7F7F7F", // Gray
  "#BCBD22", // Olive
  "#17BECF", // Cyan
] as const;

/** Color-blind safe palette - 16 distinguishable colors */
export const tableauColorBlindSafe = [
  "#EDC948",
  "#79706E",
  "#D4A6C8",
  "#FFB67D",
  "#499894",
  "#BAB0AC",
  "#9D7660",
  "#59A14F",
  "#86BCB6",
  "#4E79A7",
  "#F28E2B",
  "#B07AA1",
  "#E15759",
  "#FF9DA7",
  "#76B7B2",
  "#9C755F",
] as const;

/** Semantic status colors */
export const tableauStatus = {
  success: "#59A14F",
  warning: "#F28E2B",
  error: "#E15759",
  info: "#4E79A7",
  neutral: "#79706E",
} as const;

/** Chart color palettes for different use cases */
export const tableauChartPalette = {
  /** Default categorical palette (Tableau Classic 20) */
  categorical: tableauClassic20,

  /** Accessibility-first palette */
  colorBlindSafe: tableauColorBlindSafe,

  /** Diverging palette for variance/performance metrics */
  diverging: {
    negative: "#1F77B4",
    neutral: "#FFFFFF",
    positive: "#8C564B",
  },

  /** Status-based colors for KPIs */
  status: tableauStatus,

  /** Get N colors from categorical palette */
  getSeriesColors: (count: number): string[] => {
    return tableauClassic20.slice(0, Math.min(count, 10));
  },

  /** Get color-blind safe palette for N series */
  getAccessibleColors: (count: number): string[] => {
    return tableauColorBlindSafe.slice(0, Math.min(count, 16));
  },
} as const;

/** Semantic colors for UI elements */
export const tableauColors = {
  background: {
    default: "#FFFFFF",
    elevated: "#F8F8F8",
    overlay: "rgba(0, 0, 0, 0.5)",
  },
  surface: {
    default: "#FFFFFF",
    alt: "#F8F8F8",
  },
  text: {
    primary: "#000000",
    secondary: "#666666",
    disabled: "#CCCCCC",
    inverse: "#FFFFFF",
  },
  border: {
    default: "#D0D0D0",
    light: "#E8E8E8",
    dark: "#999999",
  },
  status: tableauStatus,
} as const;

/** Typography tokens */
export const tableauTypography = {
  fontFamily: {
    primary: '"Roboto", system-ui, -apple-system, sans-serif',
    monospace: '"Roboto Mono", monospace',
  },
  fontSize: {
    xs: "12px",
    sm: "14px",
    base: "16px",
    lg: "18px",
    xl: "20px",
    "2xl": "24px",
    "3xl": "32px",
  },
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
    loose: 2,
  },
} as const;

/** Spacing tokens */
export const tableauSpacing = {
  xs: "4px",
  sm: "8px",
  md: "16px",
  lg: "24px",
  xl: "32px",
  "2xl": "48px",
} as const;

/** Border radius tokens */
export const tableauRadius = {
  none: "0",
  sm: "2px",
  md: "4px",
  lg: "8px",
  xl: "12px",
  full: "9999px",
} as const;

/** Shadow tokens */
export const tableauShadow = {
  sm: "0 1px 2px rgba(0, 0, 0, 0.05)",
  md: "0 4px 6px rgba(0, 0, 0, 0.1)",
  lg: "0 10px 15px rgba(0, 0, 0, 0.1)",
  xl: "0 20px 25px rgba(0, 0, 0, 0.1)",
} as const;

/** Motion/animation tokens */
export const tableauMotion = {
  duration: {
    fast: "100ms",
    base: "200ms",
    slow: "300ms",
    slower: "500ms",
  },
  easing: {
    linear: "linear",
    easeIn: "cubic-bezier(0.4, 0, 1, 1)",
    easeOut: "cubic-bezier(0, 0, 0.2, 1)",
    easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
  },
} as const;

/**
 * Create a complete Tableau theme object
 * Useful for passing to chart libraries or theme providers
 */
export function createTableauTheme() {
  return {
    colors: tableauColors,
    chart: tableauChartPalette,
    typography: tableauTypography,
    spacing: tableauSpacing,
    radius: tableauRadius,
    shadow: tableauShadow,
    motion: tableauMotion,
  };
}

/**
 * Apply Tableau tokens as CSS custom properties to document
 * Useful for non-React contexts or global styling
 */
export function applyTableauTokensToDocument(): void {
  if (typeof document === "undefined") return;

  const root = document.documentElement;

  // Chart series colors
  tableauClassic20.forEach((color, i) => {
    root.style.setProperty(`--tableau-classic-${i + 1}`, color);
    root.style.setProperty(`--tableau-chart-series-${i + 1}`, color);
  });

  // Color blind safe palette
  tableauColorBlindSafe.forEach((color, i) => {
    root.style.setProperty(`--tableau-cb-${i + 1}`, color);
  });

  // Status colors
  Object.entries(tableauStatus).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-${key}`, value);
  });

  // Background/surface colors
  root.style.setProperty("--tableau-bg-default", tableauColors.background.default);
  root.style.setProperty("--tableau-bg-elevated", tableauColors.background.elevated);
  root.style.setProperty("--tableau-surface-default", tableauColors.surface.default);
  root.style.setProperty("--tableau-surface-alt", tableauColors.surface.alt);

  // Text colors
  Object.entries(tableauColors.text).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-text-${key}`, value);
  });

  // Border colors
  Object.entries(tableauColors.border).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-border-${key}`, value);
  });

  // Typography
  root.style.setProperty("--tableau-font-family-primary", tableauTypography.fontFamily.primary);
  root.style.setProperty("--tableau-font-family-monospace", tableauTypography.fontFamily.monospace);

  Object.entries(tableauTypography.fontSize).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-font-size-${key}`, value);
  });

  // Spacing
  Object.entries(tableauSpacing).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-spacing-${key}`, value);
  });

  // Radius
  Object.entries(tableauRadius).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-radius-${key}`, value);
  });

  // Shadows
  Object.entries(tableauShadow).forEach(([key, value]) => {
    root.style.setProperty(`--tableau-shadow-${key}`, value);
  });
}

/**
 * Get chart colors for a specific library format
 */
export const tableauChartColors = {
  /** For Recharts/Victory */
  recharts: tableauClassic20,

  /** For ECharts */
  echarts: {
    color: [...tableauClassic20],
  },

  /** For Chart.js */
  chartjs: {
    backgroundColor: tableauClassic20.map((c) => `${c}CC`), // 80% opacity
    borderColor: [...tableauClassic20],
  },

  /** For Plotly */
  plotly: {
    colorway: [...tableauClassic20],
  },

  /** For Vega/Vega-Lite */
  vega: {
    scheme: "tableau20",
    range: [...tableauClassic20],
  },

  /** For D3 */
  d3: tableauClassic20,
};

export default tableauTokens;

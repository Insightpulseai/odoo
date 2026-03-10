/**
 * @ipai/echarts-themes
 * Unified ECharts theme system for InsightPulse AI
 * Single source of truth for Superset, Odoo, React apps, and dev tools
 *
 * Apache License 2.0
 */

// Type exports
export type {
  ThemeId,
  ThemeCategory,
  ThemeMetadata,
  ThemesRegistry,
  EChartsTheme,
  ThemeLoaderResult,
  ThemeLoaderOptions,
} from './types';

// Theme object exports (for static imports)
export { default as darkTheme } from './themes/dark';
export { default as shineTheme } from './themes/shine';
export { default as vintageTheme } from './themes/vintage';
export { default as romaTheme } from './themes/roma';
export { default as macaronsTheme } from './themes/macarons';
export { default as infographicTheme } from './themes/infographic';

// Metadata export
export { default as themesMetadata } from './themes.json';

// Loader exports - use subpath imports to avoid conflicts
// Browser: import { loadTheme } from '@ipai/echarts-themes/browser'
// Node: import { loadThemeSync } from '@ipai/echarts-themes/node'
// CDN: import { loadThemeFromCDN } from '@ipai/echarts-themes/cdn'

// Convenience exports
import themesMetadata from './themes.json';
import type { ThemeId, ThemeMetadata } from './types';

/**
 * Get list of all available theme IDs
 */
export function getThemeIds(): ThemeId[] {
  return themesMetadata.themes.map((t) => t.id) as ThemeId[];
}

/**
 * Get theme metadata by ID
 */
export function getThemeMetadata(themeId: ThemeId): ThemeMetadata | undefined {
  return themesMetadata.themes.find((t) => t.id === themeId) as ThemeMetadata | undefined;
}

/**
 * Get all theme metadata
 */
export function getAllThemeMetadata(): ThemeMetadata[] {
  return themesMetadata.themes as ThemeMetadata[];
}

/**
 * Check if a theme ID is valid
 */
export function isValidThemeId(themeId: string): themeId is ThemeId {
  return themesMetadata.themes.some((t) => t.id === themeId);
}

/**
 * Get themes by category
 */
export function getThemesByCategory(category: 'dark' | 'light' | 'colorful'): ThemeMetadata[] {
  return themesMetadata.themes.filter((t) => t.category === category) as ThemeMetadata[];
}

/**
 * Get dark mode themes
 */
export function getDarkModeThemes(): ThemeMetadata[] {
  return themesMetadata.themes.filter((t) => t.darkMode) as ThemeMetadata[];
}

/**
 * Get light mode themes
 */
export function getLightModeThemes(): ThemeMetadata[] {
  return themesMetadata.themes.filter((t) => !t.darkMode) as ThemeMetadata[];
}

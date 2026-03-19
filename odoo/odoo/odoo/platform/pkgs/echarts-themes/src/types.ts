/**
 * ECharts Theme Type Definitions
 * Apache License 2.0
 */

import type { EChartsOption } from 'echarts';

/**
 * Theme ID (matches official Apache ECharts theme names)
 */
export type ThemeId = 'dark' | 'shine' | 'vintage' | 'roma' | 'macarons' | 'infographic';

/**
 * Theme category classification
 */
export type ThemeCategory = 'dark' | 'light' | 'colorful';

/**
 * Theme metadata structure
 */
export interface ThemeMetadata {
  id: ThemeId;
  name: string;
  file: string;
  description: string;
  colors: string[];
  backgroundColor?: string;
  category: ThemeCategory;
  darkMode: boolean;
}

/**
 * Themes registry structure
 */
export interface ThemesRegistry {
  themes: ThemeMetadata[];
  metadata: {
    version: string;
    source: string;
    license: string;
    lastUpdated: string;
  };
}

/**
 * ECharts theme object (compatible with echarts.registerTheme)
 */
export interface EChartsTheme {
  color?: string[];
  backgroundColor?: string;
  darkMode?: boolean;
  // Full theme structure matches EChartsOption but theme-specific
  [key: string]: any;
}

/**
 * Theme loader result
 */
export interface ThemeLoaderResult {
  theme: EChartsTheme;
  metadata: ThemeMetadata;
}

/**
 * Theme loader options
 */
export interface ThemeLoaderOptions {
  /** Load theme dynamically (browser) or statically (node) */
  mode?: 'browser' | 'node' | 'cdn';
  /** CDN URL for theme files (only used in cdn mode) */
  cdnUrl?: string;
}

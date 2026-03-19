/**
 * CDN Theme Loader
 * For loading themes from CDN or external URLs
 */

import type { ThemeId, EChartsTheme, ThemeLoaderResult, ThemeMetadata } from '../types';
import themesMetadata from '../themes.json';

export interface CDNLoaderOptions {
  /** CDN base URL (e.g., 'https://cdn.jsdelivr.net/npm/@ipai/echarts-themes@1.0.0/dist/themes') */
  cdnUrl: string;
  /** Timeout in milliseconds */
  timeout?: number;
}

/**
 * Load theme from CDN
 */
export async function loadThemeFromCDN(
  themeId: ThemeId,
  options: CDNLoaderOptions
): Promise<ThemeLoaderResult> {
  const metadata = themesMetadata.themes.find((t) => t.id === themeId) as ThemeMetadata;

  if (!metadata) {
    throw new Error(`Theme "${themeId}" not found`);
  }

  const { cdnUrl, timeout = 10000 } = options;
  const themeUrl = `${cdnUrl}/${themeId}.js`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(themeUrl, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Failed to load theme from CDN: ${response.statusText}`);
    }

    const themeModule = (await response.json()) as { default?: EChartsTheme } | EChartsTheme;
    const theme: EChartsTheme =
      'default' in themeModule ? themeModule.default || themeModule : themeModule;

    return {
      theme,
      metadata,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`CDN theme load failed: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Preload theme from CDN
 */
export function preloadThemeFromCDN(
  themeId: ThemeId,
  options: CDNLoaderOptions
): Promise<ThemeLoaderResult> {
  return loadThemeFromCDN(themeId, options);
}

/**
 * Load all themes from CDN
 */
export async function loadAllThemesFromCDN(
  options: CDNLoaderOptions
): Promise<Map<ThemeId, ThemeLoaderResult>> {
  const themeIds: ThemeId[] = ['dark', 'shine', 'vintage', 'roma', 'macarons', 'infographic'];
  const themes = new Map<ThemeId, ThemeLoaderResult>();

  await Promise.all(
    themeIds.map(async (id) => {
      const result = await loadThemeFromCDN(id, options);
      themes.set(id, result);
    })
  );

  return themes;
}

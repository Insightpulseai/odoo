/**
 * Browser Theme Loader (Dynamic Import)
 * For use in browser environments with code splitting
 */

import type { ThemeId, ThemeLoaderResult, ThemeMetadata } from '../types';
import themesMetadata from '../themes.json';

/**
 * Load theme dynamically in browser environment
 * Uses dynamic import for code splitting
 */
export async function loadTheme(themeId: ThemeId): Promise<ThemeLoaderResult> {
  const metadata = themesMetadata.themes.find((t) => t.id === themeId) as ThemeMetadata;

  if (!metadata) {
    throw new Error(`Theme "${themeId}" not found`);
  }

  // Dynamic import for code splitting
  const themeModule = await import(`../themes/${themeId}.ts`);
  const theme = themeModule.default || themeModule[`${themeId}Theme`];

  return {
    theme,
    metadata,
  };
}

/**
 * Preload theme (browser) - useful for eager loading
 */
export function preloadTheme(themeId: ThemeId): Promise<ThemeLoaderResult> {
  return loadTheme(themeId);
}

/**
 * Load all themes (browser) - for applications that need all themes upfront
 */
export async function loadAllThemes(): Promise<Map<ThemeId, ThemeLoaderResult>> {
  const themeIds: ThemeId[] = ['dark', 'shine', 'vintage', 'roma', 'macarons', 'infographic'];
  const themes = new Map<ThemeId, ThemeLoaderResult>();

  await Promise.all(
    themeIds.map(async (id) => {
      const result = await loadTheme(id);
      themes.set(id, result);
    })
  );

  return themes;
}

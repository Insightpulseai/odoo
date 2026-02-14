/**
 * Node.js Theme Loader (Static Import)
 * For use in Node.js environments, SSR, build tools
 */

import type { ThemeId, ThemeLoaderResult, ThemeMetadata } from '../types';
import themesMetadata from '../themes.json';
import darkTheme from '../themes/dark';
import shineTheme from '../themes/shine';
import vintageTheme from '../themes/vintage';
import romaTheme from '../themes/roma';
import macaronsTheme from '../themes/macarons';
import infographicTheme from '../themes/infographic';

const themeMap = {
  dark: darkTheme,
  shine: shineTheme,
  vintage: vintageTheme,
  roma: romaTheme,
  macarons: macaronsTheme,
  infographic: infographicTheme,
} as const;

/**
 * Load theme synchronously in Node.js environment
 */
export function loadThemeSync(themeId: ThemeId): ThemeLoaderResult {
  const metadata = themesMetadata.themes.find((t) => t.id === themeId) as ThemeMetadata;

  if (!metadata) {
    throw new Error(`Theme "${themeId}" not found`);
  }

  const theme = themeMap[themeId];

  return {
    theme,
    metadata,
  };
}

/**
 * Load theme async (Node.js) - for consistency with browser loader
 */
export async function loadTheme(themeId: ThemeId): Promise<ThemeLoaderResult> {
  return loadThemeSync(themeId);
}

/**
 * Load all themes (Node.js)
 */
export function loadAllThemesSync(): Map<ThemeId, ThemeLoaderResult> {
  const themes = new Map<ThemeId, ThemeLoaderResult>();
  const themeIds: ThemeId[] = ['dark', 'shine', 'vintage', 'roma', 'macarons', 'infographic'];

  themeIds.forEach((id) => {
    themes.set(id, loadThemeSync(id));
  });

  return themes;
}

/**
 * Load all themes async (Node.js) - for consistency with browser loader
 */
export async function loadAllThemes(): Promise<Map<ThemeId, ThemeLoaderResult>> {
  return loadAllThemesSync();
}

/**
 * Get theme object directly (Node.js)
 */
export function getTheme(themeId: ThemeId) {
  return themeMap[themeId];
}

/**
 * Get all theme objects directly (Node.js)
 */
export function getAllThemes() {
  return { ...themeMap };
}

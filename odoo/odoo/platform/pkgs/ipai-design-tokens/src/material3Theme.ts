/**
 * Material 3 "Expressive" Theme Utilities
 * ========================================
 *
 * TypeScript utilities for working with the M3 Expressive theme.
 * Provides type-safe access to theme tokens and helper functions.
 *
 * Usage:
 * ```tsx
 * import {
 *   M3Theme,
 *   getM3ColorToken,
 *   applyM3Theme,
 *   toggleM3Theme
 * } from '@ipai/design-tokens/material3Theme';
 * ```
 */

/* =============================================================================
 * Type Definitions
 * ============================================================================= */

export type M3ThemeMode = 'light' | 'dark' | 'system';

export interface M3ColorTokens {
  // Primary
  primary: string;
  onPrimary: string;
  primaryContainer: string;
  onPrimaryContainer: string;

  // Secondary
  secondary: string;
  onSecondary: string;
  secondaryContainer: string;
  onSecondaryContainer: string;

  // Tertiary
  tertiary: string;
  onTertiary: string;
  tertiaryContainer: string;
  onTertiaryContainer: string;

  // Error
  error: string;
  onError: string;
  errorContainer: string;
  onErrorContainer: string;

  // Surface
  surface: string;
  onSurface: string;
  onSurfaceVariant: string;
  surfaceDim: string;
  surfaceBright: string;
  surfaceContainerLowest: string;
  surfaceContainerLow: string;
  surfaceContainer: string;
  surfaceContainerHigh: string;
  surfaceContainerHighest: string;

  // Inverse
  inverseSurface: string;
  inverseOnSurface: string;
  inversePrimary: string;

  // Outline
  outline: string;
  outlineVariant: string;

  // Background (deprecated)
  background: string;
  onBackground: string;

  // Status
  success: string;
  onSuccess: string;
  successContainer: string;
  onSuccessContainer: string;
  warning: string;
  onWarning: string;
  warningContainer: string;
  onWarningContainer: string;
  info: string;
  onInfo: string;
  infoContainer: string;
  onInfoContainer: string;

  // Utility
  shadow: string;
  scrim: string;
}

export interface M3UIColorTokens {
  muted: string;
  subtle: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  scrim: string;
}

export interface M3StateTokens {
  hover: number;
  pressed: number;
  focus: number;
}

export interface M3ShapeTokens {
  cornerNone: string;
  cornerExtraSmall: string;
  cornerSmall: string;
  cornerMedium: string;
  cornerLarge: string;
  cornerExtraLarge: string;
  cornerFull: string;
}

export interface M3ElevationTokens {
  level0: string;
  level1: string;
  level2: string;
  level3: string;
  level4: string;
  level5: string;
}

export interface M3TypographyTokens {
  fontFamilyBrand: string;
  fontFamilyPlain: string;
  fontFamilyMono: string;
  displayLarge: string;
  displayMedium: string;
  displaySmall: string;
  headlineLarge: string;
  headlineMedium: string;
  headlineSmall: string;
  titleLarge: string;
  titleMedium: string;
  titleSmall: string;
  bodyLarge: string;
  bodyMedium: string;
  bodySmall: string;
  labelLarge: string;
  labelMedium: string;
  labelSmall: string;
}

export interface M3Theme {
  mode: M3ThemeMode;
  colors: M3ColorTokens;
  ui: M3UIColorTokens;
  state: M3StateTokens;
  shape: M3ShapeTokens;
  elevation: M3ElevationTokens;
  typography: M3TypographyTokens;
}

/* =============================================================================
 * CSS Variable Mapping
 * ============================================================================= */

const colorVarMap: Record<keyof M3ColorTokens, string> = {
  primary: '--md-sys-color-primary',
  onPrimary: '--md-sys-color-on-primary',
  primaryContainer: '--md-sys-color-primary-container',
  onPrimaryContainer: '--md-sys-color-on-primary-container',
  secondary: '--md-sys-color-secondary',
  onSecondary: '--md-sys-color-on-secondary',
  secondaryContainer: '--md-sys-color-secondary-container',
  onSecondaryContainer: '--md-sys-color-on-secondary-container',
  tertiary: '--md-sys-color-tertiary',
  onTertiary: '--md-sys-color-on-tertiary',
  tertiaryContainer: '--md-sys-color-tertiary-container',
  onTertiaryContainer: '--md-sys-color-on-tertiary-container',
  error: '--md-sys-color-error',
  onError: '--md-sys-color-on-error',
  errorContainer: '--md-sys-color-error-container',
  onErrorContainer: '--md-sys-color-on-error-container',
  surface: '--md-sys-color-surface',
  onSurface: '--md-sys-color-on-surface',
  onSurfaceVariant: '--md-sys-color-on-surface-variant',
  surfaceDim: '--md-sys-color-surface-dim',
  surfaceBright: '--md-sys-color-surface-bright',
  surfaceContainerLowest: '--md-sys-color-surface-container-lowest',
  surfaceContainerLow: '--md-sys-color-surface-container-low',
  surfaceContainer: '--md-sys-color-surface-container',
  surfaceContainerHigh: '--md-sys-color-surface-container-high',
  surfaceContainerHighest: '--md-sys-color-surface-container-highest',
  inverseSurface: '--md-sys-color-inverse-surface',
  inverseOnSurface: '--md-sys-color-inverse-on-surface',
  inversePrimary: '--md-sys-color-inverse-primary',
  outline: '--md-sys-color-outline',
  outlineVariant: '--md-sys-color-outline-variant',
  background: '--md-sys-color-background',
  onBackground: '--md-sys-color-on-background',
  success: '--md-sys-color-success',
  onSuccess: '--md-sys-color-on-success',
  successContainer: '--md-sys-color-success-container',
  onSuccessContainer: '--md-sys-color-on-success-container',
  warning: '--md-sys-color-warning',
  onWarning: '--md-sys-color-on-warning',
  warningContainer: '--md-sys-color-warning-container',
  onWarningContainer: '--md-sys-color-on-warning-container',
  info: '--md-sys-color-info',
  onInfo: '--md-sys-color-on-info',
  infoContainer: '--md-sys-color-info-container',
  onInfoContainer: '--md-sys-color-on-info-container',
  shadow: '--md-sys-color-shadow',
  scrim: '--md-sys-color-scrim',
};

const uiColorVarMap: Record<keyof M3UIColorTokens, string> = {
  muted: '--ui-color-muted',
  subtle: '--ui-color-subtle',
  success: '--ui-color-success',
  warning: '--ui-color-warning',
  danger: '--ui-color-danger',
  info: '--ui-color-info',
  scrim: '--ui-color-scrim',
};

const stateVarMap: Record<keyof M3StateTokens, string> = {
  hover: '--ui-hover',
  pressed: '--ui-pressed',
  focus: '--ui-focus',
};

/* =============================================================================
 * Utility Functions
 * ============================================================================= */

/**
 * Get the current theme mode from the document
 */
export function getCurrentM3ThemeMode(): M3ThemeMode {
  if (typeof window === 'undefined') return 'light';

  const root = document.documentElement;
  if (root.classList.contains('dark') || root.dataset.theme === 'dark') {
    return 'dark';
  }
  return 'light';
}

/**
 * Get a color token value from CSS variables
 */
export function getM3ColorToken(token: keyof M3ColorTokens): string {
  if (typeof window === 'undefined') return '';

  const varName = colorVarMap[token];
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();

  // Convert space-separated RGB to rgb() format
  if (value.match(/^\d+ \d+ \d+$/)) {
    return `rgb(${value.replace(/ /g, ', ')})`;
  }

  return value;
}

/**
 * Get all color tokens as an object
 */
export function getM3ColorTokens(): M3ColorTokens {
  const tokens = {} as M3ColorTokens;

  for (const key of Object.keys(colorVarMap) as Array<keyof M3ColorTokens>) {
    tokens[key] = getM3ColorToken(key);
  }

  return tokens;
}

/**
 * Get a UI color token value from CSS variables
 */
export function getM3UIColorToken(token: keyof M3UIColorTokens): string {
  if (typeof window === 'undefined') return '';

  const varName = uiColorVarMap[token];
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(varName)
    .trim();

  if (value.match(/^\d+ \d+ \d+$/)) {
    return `rgb(${value.replace(/ /g, ', ')})`;
  }

  return value;
}

/**
 * Get all UI color tokens as an object
 */
export function getM3UIColorTokens(): M3UIColorTokens {
  const tokens = {} as M3UIColorTokens;

  for (const key of Object.keys(uiColorVarMap) as Array<keyof M3UIColorTokens>) {
    tokens[key] = getM3UIColorToken(key);
  }

  return tokens;
}

/**
 * Get state opacity values
 */
export function getM3StateTokens(): M3StateTokens {
  if (typeof window === 'undefined') {
    return { hover: 0.06, pressed: 0.10, focus: 0.22 };
  }

  const root = document.documentElement;
  const style = getComputedStyle(root);

  return {
    hover: parseFloat(style.getPropertyValue('--ui-hover')) || 0.06,
    pressed: parseFloat(style.getPropertyValue('--ui-pressed')) || 0.10,
    focus: parseFloat(style.getPropertyValue('--ui-focus')) || 0.22,
  };
}

/**
 * Apply M3 theme mode to the document
 */
export function applyM3Theme(mode: M3ThemeMode): void {
  if (typeof window === 'undefined') return;

  const root = document.documentElement;

  // Remove existing theme classes
  root.classList.remove('dark', 'light');
  delete root.dataset.theme;

  if (mode === 'system') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
      root.classList.add('dark');
      root.dataset.theme = 'dark';
    }
  } else if (mode === 'dark') {
    root.classList.add('dark');
    root.dataset.theme = 'dark';
  }

  // Store preference
  try {
    localStorage.setItem('m3-theme-mode', mode);
  } catch {
    // localStorage not available
  }

  // Dispatch custom event for components to react
  window.dispatchEvent(new CustomEvent('m3-theme-change', { detail: { mode } }));
}

/**
 * Toggle between light and dark themes
 */
export function toggleM3Theme(): M3ThemeMode {
  const current = getCurrentM3ThemeMode();
  const next: M3ThemeMode = current === 'dark' ? 'light' : 'dark';
  applyM3Theme(next);
  return next;
}

/**
 * Initialize theme from stored preference or system preference
 */
export function initM3Theme(): M3ThemeMode {
  if (typeof window === 'undefined') return 'light';

  // Check stored preference
  try {
    const stored = localStorage.getItem('m3-theme-mode') as M3ThemeMode | null;
    if (stored) {
      applyM3Theme(stored);
      return stored;
    }
  } catch {
    // localStorage not available
  }

  // Fall back to system preference
  applyM3Theme('system');
  return 'system';
}

/**
 * Listen for theme changes
 */
export function onM3ThemeChange(
  callback: (mode: M3ThemeMode) => void
): () => void {
  if (typeof window === 'undefined') return () => {};

  const handler = (e: Event) => {
    const detail = (e as CustomEvent).detail;
    callback(detail.mode);
  };

  window.addEventListener('m3-theme-change', handler);

  // Also listen for system preference changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const mediaHandler = () => {
    try {
      const stored = localStorage.getItem('m3-theme-mode');
      if (stored === 'system') {
        applyM3Theme('system');
      }
    } catch {
      // localStorage not available
    }
  };

  mediaQuery.addEventListener('change', mediaHandler);

  return () => {
    window.removeEventListener('m3-theme-change', handler);
    mediaQuery.removeEventListener('change', mediaHandler);
  };
}

/* =============================================================================
 * CSS Helper Functions
 * ============================================================================= */

/**
 * Generate a CSS color value from a token with optional opacity
 */
export function m3Color(token: keyof M3ColorTokens, opacity?: number): string {
  const varName = colorVarMap[token];

  if (opacity !== undefined) {
    return `rgb(var(${varName}) / ${opacity})`;
  }

  return `rgb(var(${varName}))`;
}

/**
 * Generate a state layer color (hover/focus/pressed states)
 */
export function m3StateLayer(
  token: keyof M3ColorTokens,
  state: 'hover' | 'focus' | 'pressed' | 'dragged'
): string {
  const opacityMap = {
    hover: 0.08,
    focus: 0.12,
    pressed: 0.12,
    dragged: 0.16,
  };

  return m3Color(token, opacityMap[state]);
}

/**
 * Generate elevation shadow CSS
 */
export function m3Elevation(level: 0 | 1 | 2 | 3 | 4 | 5): string {
  return `var(--md-sys-elevation-${level})`;
}

/**
 * Generate border radius CSS
 */
export function m3Shape(
  size: 'none' | 'extra-small' | 'small' | 'medium' | 'large' | 'extra-large' | 'full'
): string {
  const sizeMap = {
    none: 'none',
    'extra-small': 'extra-small',
    small: 'small',
    medium: 'medium',
    large: 'large',
    'extra-large': 'extra-large',
    full: 'full',
  };

  return `var(--md-sys-shape-corner-${sizeMap[size]})`;
}

/* =============================================================================
 * Default Export
 * ============================================================================= */

export default {
  getCurrentM3ThemeMode,
  getM3ColorToken,
  getM3ColorTokens,
  getM3UIColorToken,
  getM3UIColorTokens,
  getM3StateTokens,
  applyM3Theme,
  toggleM3Theme,
  initM3Theme,
  onM3ThemeChange,
  m3Color,
  m3StateLayer,
  m3Elevation,
  m3Shape,
};

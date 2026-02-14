/**
 * ChartThemeProvider
 * React Context provider for ECharts theme management with localStorage persistence
 */

'use client';

import React, { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import * as echarts from 'echarts';
import { loadTheme } from '@ipai/echarts-themes/browser';
import { getAllThemeMetadata, type ThemeId, type ThemeMetadata } from '@ipai/echarts-themes';

const STORAGE_KEY = 'ipai.chart_theme';
const DEFAULT_THEME_ID: ThemeId = 'shine';

export interface ChartThemeContextValue {
  /** Current theme ID */
  themeId: ThemeId;
  /** Set theme ID (persists to localStorage) */
  setThemeId: (id: ThemeId) => void;
  /** All available themes with metadata */
  themes: ThemeMetadata[];
  /** Whether theme is currently loading */
  loading: boolean;
}

export const ChartThemeContext = createContext<ChartThemeContextValue | null>(null);

export interface ChartThemeProviderProps {
  children: React.ReactNode;
  /** Default theme ID (defaults to 'shine') */
  defaultThemeId?: ThemeId;
  /** localStorage key (defaults to 'ipai.chart_theme') */
  storageKey?: string;
}

export function ChartThemeProvider({
  children,
  defaultThemeId = DEFAULT_THEME_ID,
  storageKey = STORAGE_KEY,
}: ChartThemeProviderProps) {
  const [themeId, _setThemeId] = useState<ThemeId>(defaultThemeId);
  const [loading, setLoading] = useState(false);

  // Get all theme metadata
  const themes = useMemo(() => getAllThemeMetadata(), []);

  const setThemeId = useCallback(
    (id: ThemeId) => {
      _setThemeId(id);
      try {
        localStorage.setItem(storageKey, id);
      } catch {
        // Ignore storage failures (private mode, etc.)
      }
    },
    [storageKey]
  );

  // Load persisted theme on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey) as ThemeId | null;
      if (stored && themes.find((t) => t.id === stored)) {
        _setThemeId(stored);
      }
    } catch {
      // Ignore storage read failures
    }
  }, [storageKey, themes]);

  // Load and register theme whenever themeId changes
  useEffect(() => {
    let cancelled = false;

    const loadAndRegisterTheme = async () => {
      setLoading(true);

      try {
        const { theme } = await loadTheme(themeId);

        if (!cancelled) {
          // Register theme with ECharts
          echarts.registerTheme(themeId, theme);
          setLoading(false);
        }
      } catch (error) {
        console.error(`Failed to load ECharts theme "${themeId}":`, error);

        if (!cancelled) {
          setLoading(false);

          // Fallback to default theme if current theme fails
          if (themeId !== defaultThemeId) {
            _setThemeId(defaultThemeId);
          }
        }
      }
    };

    loadAndRegisterTheme();

    return () => {
      cancelled = true;
    };
  }, [themeId, defaultThemeId]);

  const value: ChartThemeContextValue = useMemo(
    () => ({
      themeId,
      setThemeId,
      themes,
      loading,
    }),
    [themeId, setThemeId, themes, loading]
  );

  return <ChartThemeContext.Provider value={value}>{children}</ChartThemeContext.Provider>;
}

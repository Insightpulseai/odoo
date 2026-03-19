/**
 * ChartThemeSelector
 * UI component for selecting ECharts themes
 */

'use client';

import React from 'react';
import { useChartTheme } from '../hooks/useChartTheme';
import type { ThemeId } from '@ipai/echarts-themes';

export interface ChartThemeSelectorProps {
  /** Custom className for styling */
  className?: string;
  /** Custom label */
  label?: string;
  /** Show theme descriptions in dropdown */
  showDescriptions?: boolean;
}

export function ChartThemeSelector({
  className,
  label = 'Theme',
  showDescriptions = false,
}: ChartThemeSelectorProps) {
  const { themeId, setThemeId, themes, loading } = useChartTheme();

  return (
    <div className={className || 'flex items-center gap-2'}>
      {label && <label className="text-sm text-gray-500">{label}</label>}

      <select
        className="rounded-md border border-gray-200 bg-white px-2 py-1 text-sm shadow-sm disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900"
        value={themeId}
        onChange={(e) => setThemeId(e.target.value as ThemeId)}
        disabled={loading}
      >
        {themes.map((theme) => (
          <option key={theme.id} value={theme.id}>
            {theme.name}
            {showDescriptions && theme.description ? ` - ${theme.description}` : ''}
          </option>
        ))}
      </select>

      {loading && <span className="text-xs text-gray-400">Loading...</span>}
    </div>
  );
}

/**
 * @ipai/echarts-react
 * React components for Apache ECharts with theme support
 */

'use client';

// Components
export { ChartThemeProvider } from './components/ChartThemeProvider';
export type { ChartThemeProviderProps, ChartThemeContextValue } from './components/ChartThemeProvider';

export { ChartThemeSelector } from './components/ChartThemeSelector';
export type { ChartThemeSelectorProps } from './components/ChartThemeSelector';

export { EChart } from './components/EChart';
export type { EChartProps } from './components/EChart';

// Hooks
export { useChartTheme } from './hooks/useChartTheme';

// Types (re-export from echarts-themes)
export type {
  ThemeId,
  ThemeCategory,
  ThemeMetadata,
  EChartsTheme,
} from '@ipai/echarts-themes';

export type { EChartsOption, EChartsType } from 'echarts';

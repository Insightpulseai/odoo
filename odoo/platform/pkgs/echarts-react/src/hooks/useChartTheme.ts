/**
 * useChartTheme hook
 * Access chart theme context
 */

import { useContext } from 'react';
import { ChartThemeContext } from '../components/ChartThemeProvider';

export function useChartTheme() {
  const context = useContext(ChartThemeContext);

  if (!context) {
    throw new Error('useChartTheme must be used within a ChartThemeProvider');
  }

  return context;
}

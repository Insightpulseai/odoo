/**
 * EChart Component
 * React wrapper for Apache ECharts with theme support
 */

'use client';

import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { useChartTheme } from '../hooks/useChartTheme';
import type { EChartsOption, EChartsType } from 'echarts';

export interface EChartProps {
  /** ECharts option configuration */
  option: EChartsOption;
  /** Custom className for container */
  className?: string;
  /** Chart width (CSS value or 'auto') */
  width?: string | number;
  /** Chart height (CSS value or 'auto') */
  height?: string | number;
  /** Callback when chart instance is initialized */
  onInit?: (chart: EChartsType) => void;
  /** Whether to auto-resize on window resize */
  autoResize?: boolean;
}

export function EChart({
  option,
  className,
  width = '100%',
  height = '400px',
  onInit,
  autoResize = true,
}: EChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<EChartsType | null>(null);
  const { themeId } = useChartTheme();

  // Initialize chart with current theme
  useEffect(() => {
    if (!containerRef.current) return;

    // Dispose previous instance when theme changes
    if (chartRef.current) {
      chartRef.current.dispose();
      chartRef.current = null;
    }

    // Initialize chart with theme
    chartRef.current = echarts.init(containerRef.current, themeId);
    chartRef.current.setOption(option, { notMerge: true });

    // Call onInit callback if provided
    if (onInit) {
      onInit(chartRef.current);
    }

    // Setup resize handler
    const handleResize = () => chartRef.current?.resize();

    if (autoResize) {
      window.addEventListener('resize', handleResize);
    }

    return () => {
      if (autoResize) {
        window.removeEventListener('resize', handleResize);
      }
      chartRef.current?.dispose();
      chartRef.current = null;
    };
  }, [themeId, onInit, autoResize]); // Re-init when theme changes

  // Update chart when option changes
  useEffect(() => {
    if (chartRef.current && option) {
      chartRef.current.setOption(option, { notMerge: true });
    }
  }, [option]);

  // Apply width/height styles
  const style: React.CSSProperties = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return <div ref={containerRef} className={className} style={style} />;
}

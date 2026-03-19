'use client'

import { useState, useEffect } from 'react'
import type { EChartsOption } from 'echarts'

interface EChartsWrapperProps {
  option: EChartsOption
  height?: string | number
  style?: React.CSSProperties
  onEvents?: Record<string, (params: any) => void>
}

export function EChartsWrapper({ option, height = 300, style, onEvents }: EChartsWrapperProps) {
  const [mounted, setMounted] = useState(false)
  const [Chart, setChart] = useState<any>(null)

  useEffect(() => {
    // Dynamic import to avoid SSR issues with canvas
    Promise.all([
      import('echarts-for-react/lib/core'),
      import('echarts/core'),
      import('echarts/charts'),
      import('echarts/components'),
      import('echarts/renderers'),
    ]).then(([ReactEChartsCore, echarts, charts, components, renderers]) => {
      echarts.use([
        charts.BarChart, charts.GaugeChart, charts.GraphChart,
        charts.HeatmapChart, charts.TreemapChart, charts.CustomChart,
        components.GridComponent, components.TooltipComponent,
        components.LegendComponent, components.TitleComponent,
        components.VisualMapComponent, components.CalendarComponent,
        renderers.CanvasRenderer,
      ])
      setChart({ Component: ReactEChartsCore.default, echarts: echarts })
      setMounted(true)
    })
  }, [])

  if (!mounted || !Chart) {
    return <div style={{ height, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8A8886' }}>Loading chart...</div>
  }

  return (
    <Chart.Component
      echarts={Chart.echarts}
      option={option}
      style={{ height, width: '100%', ...style }}
      opts={{ renderer: 'canvas' }}
      onEvents={onEvents}
      notMerge={true}
    />
  )
}

// Shared color palette matching Copilot design
export const COPILOT_COLORS = {
  primary: '#7B2FF2',
  secondary: '#2264D1',
  success: '#0E7A0D',
  warning: '#EAA300',
  danger: '#D13438',
  info: '#0078D4',
  neutral: '#8A8886',
  gradient: ['#7B2FF2', '#2264D1'],
}

export const CHART_PALETTE = [
  '#7B2FF2', '#2264D1', '#0E7A0D', '#EAA300', '#D13438',
  '#00B7C3', '#8764B8', '#038387', '#CA5010', '#4F6BED',
]

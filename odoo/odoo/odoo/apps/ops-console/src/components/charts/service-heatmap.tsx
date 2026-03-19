'use client'

import { EChartsWrapper, COPILOT_COLORS } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface ServiceStatus {
  name: string
  status: string
  responseTime?: number
}

interface ServiceHeatmapProps {
  services: ServiceStatus[]
  height?: number
}

const STATUS_VALUE: Record<string, number> = {
  live: 3, operational: 3, active: 3, completed: 3, success: 3,
  degraded: 2, warning: 2, stub: 2, partial: 2, paused: 2,
  down: 1, error: 1, failure: 1,
  planned: 0, scaffolded: 0, queued: 0, pending: 0,
}

export function ServiceHeatmap({ services, height = 200 }: ServiceHeatmapProps) {
  if (!services.length) return null

  const data = services.map((s, i) => [i, 0, STATUS_VALUE[s.status] ?? 0])

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        const svc = services[params.data[0]]
        return `<b>${svc.name}</b><br/>Status: ${svc.status}${svc.responseTime != null ? `<br/>Response: ${svc.responseTime}ms` : ''}`
      },
    },
    grid: { left: 10, right: 10, top: 10, bottom: 40 },
    xAxis: {
      type: 'category',
      data: services.map(s => s.name),
      axisLabel: { fontSize: 10, rotate: 30, interval: 0 },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'category',
      data: ['Health'],
      axisLabel: { show: false },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: 3,
      show: false,
      inRange: {
        color: [COPILOT_COLORS.neutral, COPILOT_COLORS.danger, COPILOT_COLORS.warning, COPILOT_COLORS.success],
      },
    },
    series: [{
      type: 'heatmap',
      data,
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      label: {
        show: true,
        formatter: (params: any) => services[params.data[0]]?.status || '',
        fontSize: 10,
        color: '#fff',
      },
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

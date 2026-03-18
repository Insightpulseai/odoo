'use client'

import { EChartsWrapper, COPILOT_COLORS } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface DeployEntry {
  id: string
  environment: string
  status: string
  sha: string
  ref: string
  createdAt: string
}

interface DeployTimelineProps {
  deployments: DeployEntry[]
  height?: number
}

export function DeployTimeline({ deployments, height = 200 }: DeployTimelineProps) {
  if (!deployments.length) return null

  const statusColors: Record<string, string> = {
    success: COPILOT_COLORS.success,
    completed: COPILOT_COLORS.success,
    failure: COPILOT_COLORS.danger,
    error: COPILOT_COLORS.danger,
    in_progress: COPILOT_COLORS.primary,
    running: COPILOT_COLORS.primary,
    queued: COPILOT_COLORS.info,
    pending: COPILOT_COLORS.neutral,
  }

  const recent = deployments.slice(0, 15).reverse()

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        const d = recent[p.dataIndex]
        return `<b>${d.ref}</b> (${d.sha})<br/>Env: ${d.environment}<br/>Status: ${d.status}<br/>${new Date(d.createdAt).toLocaleString()}`
      },
    },
    grid: { left: 10, right: 10, top: 10, bottom: 30 },
    xAxis: {
      type: 'category',
      data: recent.map(d => d.sha),
      axisLabel: { fontSize: 9, color: '#8A8886' },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      show: false,
      max: 1,
    },
    series: [{
      type: 'bar',
      data: recent.map(d => ({
        value: 1,
        itemStyle: {
          color: statusColors[d.status] || COPILOT_COLORS.neutral,
          borderRadius: [3, 3, 0, 0],
        },
      })),
      barWidth: '70%',
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

'use client'

import { EChartsWrapper, COPILOT_COLORS } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface ReadinessGaugeProps {
  score: number | null | undefined
  label?: string
  height?: number
}

export function ReadinessGauge({ score, label = 'Readiness', height = 200 }: ReadinessGaugeProps) {
  const safeScore = score != null && !isNaN(score) ? Math.round(score * 100) : null

  if (safeScore === null) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8A8886' }}>
        Score unavailable
      </div>
    )
  }

  const color = safeScore >= 75 ? COPILOT_COLORS.success
    : safeScore >= 50 ? COPILOT_COLORS.warning
    : safeScore >= 25 ? '#CA5010'
    : COPILOT_COLORS.danger

  const option: EChartsOption = {
    series: [{
      type: 'gauge',
      startAngle: 220,
      endAngle: -40,
      min: 0,
      max: 100,
      pointer: { show: false },
      progress: {
        show: true,
        width: 14,
        roundCap: true,
        itemStyle: { color },
      },
      axisLine: {
        lineStyle: { width: 14, color: [[1, '#E8E8E8']] },
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      detail: {
        valueAnimation: true,
        fontSize: 28,
        fontWeight: 'bold',
        formatter: '{value}%',
        color,
        offsetCenter: [0, '0%'],
      },
      title: {
        show: true,
        offsetCenter: [0, '35%'],
        fontSize: 13,
        color: '#8A8886',
      },
      data: [{ value: safeScore, name: label }],
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

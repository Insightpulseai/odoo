'use client'

import { EChartsWrapper, COPILOT_COLORS } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface DomainScore {
  domain: string
  score: number
  maturity?: string
  evidencePassed?: number
  evidenceTotal?: number
  trend?: number
}

interface DomainBarsProps {
  scores: DomainScore[]
  height?: number
}

/** Canonical maturity color: 0-24 red, 25-49 amber, 50-74 warning, 75-89 green, 90-100 deep green */
function maturityColor(score: number): string {
  const pct = score * 100
  if (pct >= 90) return '#0E7A0D'        // hardened — deep green
  if (pct >= 75) return COPILOT_COLORS.success  // operational
  if (pct >= 50) return COPILOT_COLORS.warning  // partial — yellow
  if (pct >= 25) return '#CA5010'               // scaffolded — amber
  return COPILOT_COLORS.danger                  // missing — red
}

export function DomainBars({ scores, height = 300 }: DomainBarsProps) {
  if (!scores.length) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8A8886' }}>No data</div>
  }

  const sorted = [...scores].sort((a, b) => a.score - b.score)

  const option: EChartsOption = {
    grid: { left: '30%', right: '10%', top: 8, bottom: 8 },
    xAxis: {
      type: 'value',
      max: 1,
      axisLabel: { formatter: (v: number) => `${Math.round(v * 100)}%`, fontSize: 11 },
      splitLine: { lineStyle: { type: 'dashed', color: '#E8E8E8' } },
    },
    yAxis: {
      type: 'category',
      data: sorted.map(s => s.domain),
      axisLabel: { fontSize: 11, color: '#323130' },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const p = params[0]
        const src = sorted.find(s => s.domain === p.name)
        const lines = [`<b>${p.name}</b>`, `Score: ${Math.round(p.value * 100)}%`]
        if (src?.maturity) lines.push(`Maturity: ${src.maturity}`)
        if (src?.evidenceTotal) lines.push(`Evidence: ${src.evidencePassed ?? 0}/${src.evidenceTotal} checks`)
        if (src?.trend !== undefined && src.trend !== 0) {
          const sign = src.trend > 0 ? '+' : ''
          lines.push(`Trend: ${sign}${Math.round(src.trend * 100)}%`)
        }
        return lines.join('<br/>')
      },
    },
    series: [{
      type: 'bar',
      data: sorted.map(s => ({
        value: s.score,
        itemStyle: {
          color: maturityColor(s.score),
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barWidth: '60%',
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

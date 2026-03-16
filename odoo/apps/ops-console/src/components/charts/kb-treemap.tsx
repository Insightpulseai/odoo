'use client'

import { EChartsWrapper, COPILOT_COLORS, CHART_PALETTE } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface KBNode {
  name: string
  chunks: number
  status: string
}

interface KBTreemapProps {
  knowledgeBases: KBNode[]
  height?: number
}

export function KBTreemap({ knowledgeBases, height = 250 }: KBTreemapProps) {
  if (!knowledgeBases.length) return null

  const data = knowledgeBases.map(kb => ({
    name: kb.name,
    value: Math.max(kb.chunks, 1), // min 1 so scaffolded items still show
    chunks: kb.chunks,
    status: kb.status,
    itemStyle: {
      color: kb.status === 'operational' ? COPILOT_COLORS.success
        : kb.status === 'error' ? COPILOT_COLORS.danger
        : '#E1DFDD',
      borderColor: '#fff',
      borderWidth: 2,
    },
  }))

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        const d = params.data
        return `<b>${d.name}</b><br/>Chunks: ${d.chunks.toLocaleString()}<br/>Status: ${d.status}`
      },
    },
    series: [{
      type: 'treemap',
      data,
      width: '100%',
      height: '100%',
      roam: false,
      nodeClick: false,
      breadcrumb: { show: false },
      label: {
        show: true,
        formatter: (params: any) => `${params.data.name}\n${params.data.chunks.toLocaleString()} chunks`,
        fontSize: 11,
        color: '#323130',
      },
      levels: [{
        itemStyle: { borderRadius: 6 },
      }],
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

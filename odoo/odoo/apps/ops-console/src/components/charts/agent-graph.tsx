'use client'

import { EChartsWrapper, COPILOT_COLORS, CHART_PALETTE } from './echarts-wrapper'
import type { EChartsOption } from 'echarts'

interface AgentNode {
  name: string
  status: 'live' | 'degraded' | 'down' | 'stub' | string
  category?: string
  messageCount?: number
}

interface AgentEdge {
  source: string
  target: string
  label?: string
}

interface AgentGraphProps {
  nodes: AgentNode[]
  edges: AgentEdge[]
  height?: number
}

const STATUS_COLORS: Record<string, string> = {
  live: COPILOT_COLORS.success,
  operational: COPILOT_COLORS.success,
  active: COPILOT_COLORS.success,
  completed: COPILOT_COLORS.success,
  degraded: COPILOT_COLORS.warning,
  stub: COPILOT_COLORS.warning,
  down: COPILOT_COLORS.danger,
  error: COPILOT_COLORS.danger,
}

export function AgentGraph({ nodes, edges, height = 400 }: AgentGraphProps) {
  if (!nodes.length) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#8A8886' }}>No topology data</div>
  }

  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<b>${params.data.name}</b><br/>Status: ${params.data.status || 'unknown'}${params.data.messageCount != null ? `<br/>Messages: ${params.data.messageCount}` : ''}`
        }
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}${params.data.label ? `<br/>${params.data.label}` : ''}`
        }
        return ''
      },
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      force: {
        repulsion: 300,
        edgeLength: [100, 200],
        gravity: 0.1,
      },
      label: {
        show: true,
        position: 'bottom',
        fontSize: 11,
        color: '#323130',
      },
      edgeLabel: {
        show: false,
      },
      lineStyle: {
        color: '#C8C6C4',
        width: 1.5,
        curveness: 0.1,
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: COPILOT_COLORS.primary },
      },
      data: nodes.map((n, i) => ({
        name: n.name,
        status: n.status,
        messageCount: n.messageCount,
        symbolSize: n.name === 'MCP Coordinator' ? 55 : 40,
        itemStyle: {
          color: n.name === 'MCP Coordinator'
            ? COPILOT_COLORS.primary
            : STATUS_COLORS[n.status] || COPILOT_COLORS.neutral,
          borderColor: '#fff',
          borderWidth: 2,
          shadowBlur: 5,
          shadowColor: 'rgba(0,0,0,0.1)',
        },
      })),
      edges: edges.map(e => ({
        source: e.source,
        target: e.target,
        label: e.label ? { show: true, formatter: e.label, fontSize: 9 } : undefined,
      })),
    }],
  }

  return <EChartsWrapper option={option} height={height} />
}

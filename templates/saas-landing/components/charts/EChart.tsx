'use client'

import React, { useEffect, useRef } from 'react'
import * as echarts from 'echarts'
import { useChartTheme } from '@/components/theme/ChartThemeProvider'
import type { EChartsOption } from 'echarts'

type Props = {
  option: EChartsOption
  className?: string
}

export function EChart({ option, className }: Props) {
  const ref = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<echarts.EChartsType | null>(null)
  const { themeId } = useChartTheme()

  useEffect(() => {
    if (!ref.current) return

    // Dispose previous instance (theme changes require re-init)
    if (chartRef.current) {
      chartRef.current.dispose()
      chartRef.current = null
    }

    chartRef.current = echarts.init(ref.current, themeId)
    chartRef.current.setOption(option, { notMerge: true })

    const onResize = () => chartRef.current?.resize()
    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      chartRef.current?.dispose()
      chartRef.current = null
    }
  }, [themeId]) // re-init on theme changes

  useEffect(() => {
    chartRef.current?.setOption(option, { notMerge: true })
  }, [option])

  return <div ref={ref} className={className ?? 'h-64 w-full'} />
}

'use client'

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { loadEChartsTheme, CHART_THEMES } from '@/lib/chart-themes'

const STORAGE_KEY = 'ipai.chart_theme'

export type ChartThemeId = keyof typeof CHART_THEMES

const DEFAULT_CHART_THEME_ID: ChartThemeId = 'shine'

type Ctx = {
  themeId: ChartThemeId
  setThemeId: (id: ChartThemeId) => void
  themes: { id: ChartThemeId; name: string; description?: string; darkMode?: boolean }[]
}

const ChartThemeContext = createContext<Ctx | null>(null)

export function ChartThemeProvider({ children }: { children: React.ReactNode }) {
  const [themeId, _setThemeId] = useState<ChartThemeId>(DEFAULT_CHART_THEME_ID)

  const themes = useMemo(
    () =>
      Object.values(CHART_THEMES).map((t) => ({
        id: t.id as ChartThemeId,
        name: t.name,
        description: t.description,
        darkMode: t.darkMode,
      })),
    []
  )

  const setThemeId = useCallback((id: ChartThemeId) => {
    _setThemeId(id)
    try {
      localStorage.setItem(STORAGE_KEY, id)
    } catch {
      // ignore storage failures (private mode, etc.)
    }
  }, [])

  // Load persisted theme on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY) as ChartThemeId | null
      if (stored && CHART_THEMES[stored]) _setThemeId(stored)
    } catch {
      // ignore
    }
  }, [])

  // Ensure the current theme JS is loaded (registers echarts theme)
  useEffect(() => {
    loadEChartsTheme(themeId).catch(() => {
      // fallback to default if theme load fails
      if (themeId !== DEFAULT_CHART_THEME_ID) {
        _setThemeId(DEFAULT_CHART_THEME_ID)
      }
    })
  }, [themeId])

  const value: Ctx = useMemo(() => ({ themeId, setThemeId, themes }), [themeId, setThemeId, themes])

  return <ChartThemeContext.Provider value={value}>{children}</ChartThemeContext.Provider>
}

export function useChartTheme() {
  const ctx = useContext(ChartThemeContext)
  if (!ctx) throw new Error('useChartTheme must be used within ChartThemeProvider')
  return ctx
}

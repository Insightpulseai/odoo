'use client'

import React from 'react'
import { useChartTheme, type ChartThemeId } from './ChartThemeProvider'

export function ChartThemeSelector() {
  const { themeId, setThemeId, themes } = useChartTheme()

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-500">Theme</label>
      <select
        className="rounded-md border border-gray-200 bg-white px-2 py-1 text-sm shadow-sm dark:border-gray-700 dark:bg-gray-900"
        value={themeId}
        onChange={(e) => setThemeId(e.target.value as ChartThemeId)}
      >
        {themes.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}
          </option>
        ))}
      </select>
    </div>
  )
}

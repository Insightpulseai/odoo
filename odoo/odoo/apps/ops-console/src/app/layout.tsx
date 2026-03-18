'use client'

import { useState, useCallback } from 'react'
import {
  FluentProvider,
  webLightTheme,
  webDarkTheme,
} from '@fluentui/react-components'
import { Sidebar } from '@/components/shell/sidebar'
import { Header } from '@/components/shell/header'
import { CopilotChat } from '@/components/chat/copilot-chat'
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isDark, setIsDark] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const handleThemeToggle = useCallback((dark: boolean) => {
    setIsDark(dark)
  }, [])

  const handleSidebarToggle = useCallback(() => {
    setSidebarCollapsed((prev) => !prev)
  }, [])

  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>IPAI Ops Console</title>
        <meta
          name="description"
          content="Agent development and deployment readiness dashboard"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <FluentProvider theme={isDark ? webDarkTheme : webLightTheme}>
          <div className="app-shell">
            <Sidebar
              collapsed={sidebarCollapsed}
              onToggle={handleSidebarToggle}
            />
            <div className="app-main">
              <Header isDark={isDark} onThemeToggle={handleThemeToggle} />
              <main className="app-content">{children}</main>
            </div>
            <CopilotChat />
          </div>
        </FluentProvider>
      </body>
    </html>
  )
}

import type { Metadata } from 'next'
import { ThemeProvider } from '@primer/react'
import './globals.css'

export const metadata: Metadata = {
  title: 'Odoo Documentation - IPAI Platform',
  description: 'Comprehensive documentation for Odoo 18/19 with IPAI Platform extensions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>
        <ThemeProvider colorMode="auto">
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}

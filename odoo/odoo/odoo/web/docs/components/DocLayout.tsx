'use client'

import { PageLayout, Box } from '@primer/react'
import { DocNavigation } from './DocNavigation'

export function DocLayout({ children }: { children: React.ReactNode }) {
  return (
    <PageLayout>
      <PageLayout.Pane position="start" sticky>
        <DocNavigation />
      </PageLayout.Pane>

      <PageLayout.Content>
        <Box sx={{ maxWidth: 900, margin: '0 auto', padding: 4 }}>
          {children}
        </Box>
      </PageLayout.Content>
    </PageLayout>
  )
}

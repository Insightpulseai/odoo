'use client'

import type { ReactNode } from 'react'

export default function Providers({ children }: { children: ReactNode }) {
  // Put anything that touches window/localStorage/extensions/theme here.
  return <>{children}</>
}

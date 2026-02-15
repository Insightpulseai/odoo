'use client'

import { useState } from 'react'
import { useIsMobile } from '@/hooks/use-mobile'
import SupabaseManagerDialog from '@/components/supabase-manager'

export default function Home() {
  const isMobile = useIsMobile()
  const [isOpen, setIsOpen] = useState(true)

  return (
    <main className="h-screen w-screen overflow-hidden">
      <SupabaseManagerDialog
        projectRef="default"
        open={isOpen}
        onOpenChange={setIsOpen}
        isMobile={isMobile}
      />
    </main>
  )
}

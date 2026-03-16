'use client'

import { useState, useEffect } from 'react'
import { useMobile } from '@/hooks/use-mobile'
import SupabaseManagerDialog from '@/components/supabase-manager'
import { OdooStyleLanding } from '@/components/OdooStyleLanding'
import { getProjectRefConfig } from '@/lib/supabase-config'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

export default function HomePage({ searchParams }: { searchParams: { ref?: string } }) {
  const [open, setOpen] = useState(false)
  const isMobile = useMobile()

  // Deterministic project ref resolution
  const [projectConfig, setProjectConfig] = useState<ReturnType<typeof getProjectRefConfig>>({
    projectRef: null,
    isValid: false,
    source: 'none',
  })

  useEffect(() => {
    // Priority: env > searchParams (handled by getProjectRefConfig internally usually, or passed here)
    setProjectConfig(getProjectRefConfig())
  }, [])

  const projectRef = projectConfig.projectRef || ''
  const hasValidProject = projectConfig.isValid

  return (
    <>
      {/* Show configuration error as a floating toast-like alert if missing */}
      {!hasValidProject && (
        <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 w-full max-w-2xl px-6">
          <Alert variant="destructive" className="shadow-2xl border-2">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle className="font-bold">Configuration Required</AlertTitle>
            <AlertDescription className="mt-2 text-sm">
              <p className="font-medium text-white/90">{projectConfig.error}</p>
              <div className="mt-3 flex gap-4 opacity-80">
                <code>?ref=your_ref</code>
                <span>- or -</span>
                <code>NEXT_PUBLIC_SUPABASE_PROJECT_REF</code>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      )}

      <OdooStyleLanding onOpenManager={() => setOpen(true)} />

      {/* Manager Dialog - Opens when onOpenManager is triggered */}
      <SupabaseManagerDialog
        projectRef={projectRef}
        open={open}
        onOpenChange={setOpen}
        isMobile={isMobile}
      />
    </>
  )
}

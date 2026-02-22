'use client'

import { useState } from 'react'
import { toast } from 'sonner'
import SupabaseManagerDialog from '@/components/supabase-manager'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Database, KeyRound, RefreshCw } from 'lucide-react'

export default function SupabaseManagerClient({ projectRef }: { projectRef: string }) {
  const [open, setOpen] = useState(false)
  const [syncing, setSyncing] = useState(false)

  const syncFromKeychain = async () => {
    setSyncing(true)
    try {
      const res = await fetch('/api/secrets/sync', { method: 'POST' })
      const data = await res.json()
      if (!res.ok) {
        toast.error(data.error ?? 'Sync failed')
      } else if (data.synced?.length === 0) {
        toast.warning(data.message)
      } else {
        toast.success(
          `Synced: ${data.synced.join(', ')} → Supabase Vault`,
          { description: 'Open the Manager → Secrets tab to verify.' }
        )
      }
    } catch (e: any) {
      toast.error(e.message ?? 'Network error')
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Keychain sync banner */}
      <div className="bg-white rounded-lg border shadow-sm p-5 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <KeyRound className="h-5 w-5 text-muted-foreground flex-shrink-0" />
          <div>
            <p className="text-sm font-medium">Sync secrets from macOS Keychain</p>
            <p className="text-xs text-muted-foreground">
              Pushes{' '}
              <code className="bg-muted px-1 rounded">AI_GATEWAY_API_KEY</code>,{' '}
              <code className="bg-muted px-1 rounded">OPENAI_API_KEY</code>, and{' '}
              <code className="bg-muted px-1 rounded">VERCEL_API_TOKEN</code> to
              Supabase Vault. Management token stays local only.
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={syncFromKeychain}
          disabled={syncing || !projectRef}
        >
          {syncing ? (
            <RefreshCw className="mr-2 h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-3.5 w-3.5" />
          )}
          {syncing ? 'Syncing…' : 'Sync from Keychain'}
        </Button>
      </div>

      {/* Manager card */}
      <div className="bg-white rounded-lg border shadow-sm p-8 flex flex-col items-center gap-6">
        <div className="text-center">
          <Database className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold mb-1">Supabase Platform Kit</h3>
          <p className="text-sm text-gray-500 mb-1">
            Database · Auth · Storage · Users · Secrets · Logs · Suggestions
          </p>
          <p className="text-xs text-muted-foreground mb-4">
            Project:{' '}
            <code className="bg-gray-100 px-1 rounded">{projectRef || 'not configured'}</code>
            {projectRef && (
              <Badge variant="secondary" className="ml-2 text-[10px]">
                ACTIVE_HEALTHY
              </Badge>
            )}
          </p>
          <Button onClick={() => setOpen(true)} disabled={!projectRef}>
            Open Manager
          </Button>
        </div>

        {projectRef && (
          <SupabaseManagerDialog
            projectRef={projectRef}
            open={open}
            onOpenChange={setOpen}
            isMobile={false}
          />
        )}
      </div>
    </div>
  )
}

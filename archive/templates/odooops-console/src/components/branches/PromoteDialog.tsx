'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react'
import type { BranchCardDTO, Stage } from '@/lib/types/branches'

interface PromoteDialogProps {
  open: boolean
  fromStage: Stage
  toStage: Stage
  branch: BranchCardDTO | null
  onConfirm: (reason?: string) => Promise<void>
  onCancel: () => void
}

const stageLabels: Record<Stage, string> = {
  dev: 'Development',
  staging: 'Staging',
  production: 'Production'
}

export function PromoteDialog({
  open,
  fromStage,
  toStage,
  branch,
  onConfirm,
  onCancel
}: PromoteDialogProps) {
  const [reason, setReason] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleConfirm = async () => {
    setIsSubmitting(true)
    try {
      await onConfirm(reason || undefined)
      setReason('')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setReason('')
    onCancel()
  }

  if (!branch) return null

  // Policy checks
  const buildStatus = branch.latest_build?.status
  const hasSuccessfulBuild = buildStatus === 'green'
  const isProduction = toStage === 'production'
  const canPromote = branch.permissions.can_promote

  // Determine validation state
  const validations = [
    {
      label: 'Successful build required',
      passed: hasSuccessfulBuild,
      critical: isProduction
    },
    {
      label: 'Promotion permission',
      passed: canPromote,
      critical: true
    }
  ]

  const allCriticalPassed = validations
    .filter(v => v.critical)
    .every(v => v.passed)

  return (
    <Dialog open={open} onOpenChange={handleCancel}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Promote Branch</DialogTitle>
          <DialogDescription>
            Promote <strong>{branch.name}</strong> from{' '}
            <strong>{stageLabels[fromStage]}</strong> to{' '}
            <strong>{stageLabels[toStage]}</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Policy Checks */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Policy Checks</Label>
            {validations.map((validation, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                {validation.passed ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : validation.critical ? (
                  <XCircle className="h-4 w-4 text-red-600" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                )}
                <span className={validation.passed ? 'text-gray-700' : 'text-gray-500'}>
                  {validation.label}
                </span>
              </div>
            ))}
          </div>

          {/* Warning for production */}
          {isProduction && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                This will deploy to production. Ensure all tests have passed.
              </AlertDescription>
            </Alert>
          )}

          {/* Build Status */}
          {branch.latest_build && (
            <div className="space-y-1 text-sm">
              <Label className="text-sm font-medium">Latest Build</Label>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">Status:</span>
                <span className="font-medium">
                  {buildStatus === 'green' && '✅ Success'}
                  {buildStatus === 'yellow' && '⚠️ Warning'}
                  {buildStatus === 'red' && '❌ Failed'}
                  {buildStatus === 'running' && '🔄 Running'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500">Commit:</span>
                <span className="font-mono text-xs">
                  {branch.latest_build.commit_sha.substring(0, 7)}
                </span>
              </div>
            </div>
          )}

          {/* Optional Reason */}
          <div className="space-y-2">
            <Label htmlFor="reason">
              Reason {isProduction && <span className="text-red-500">*</span>}
            </Label>
            <Input
              id="reason"
              placeholder={
                isProduction
                  ? 'Required: Why are you promoting to production?'
                  : 'Optional: Add a reason for this promotion'
              }
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={
              !allCriticalPassed ||
              isSubmitting ||
              (isProduction && !reason.trim())
            }
          >
            {isSubmitting ? 'Promoting...' : 'Confirm Promotion'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

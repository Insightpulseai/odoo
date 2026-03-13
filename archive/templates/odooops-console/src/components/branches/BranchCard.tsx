'use client'

import { useState } from 'react'
import { useDraggable } from '@dnd-kit/core'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreVertical, ExternalLink, RefreshCw, ArrowRight, Pin } from 'lucide-react'
import type { BranchCardDTO, BuildStatus } from '@/lib/types/branches'

interface BranchCardProps {
  branch: BranchCardDTO
  onPromote: (branch: BranchCardDTO) => void
  onRebuild: (branchId: string) => void
  onOpen: (url: string) => void
}

const statusConfig: Record<BuildStatus, { label: string; className: string }> = {
  green: { label: 'Success', className: 'bg-green-100 text-green-800' },
  yellow: { label: 'Warning', className: 'bg-yellow-100 text-yellow-800' },
  red: { label: 'Failed', className: 'bg-red-100 text-red-800' },
  running: { label: 'Running', className: 'bg-blue-100 text-blue-800' }
}

function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return 'N/A'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
}

function formatTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (days > 0) return `${days}d ago`
  if (hours > 0) return `${hours}h ago`
  return 'Recently'
}

export function BranchCard({ branch, onPromote, onRebuild, onOpen }: BranchCardProps) {
  const [isRebuilding, setIsRebuilding] = useState(false)

  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: branch.id,
    data: branch
  })

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
        opacity: isDragging ? 0.5 : 1
      }
    : undefined

  const handleRebuild = async () => {
    setIsRebuilding(true)
    try {
      await onRebuild(branch.id)
    } finally {
      setIsRebuilding(false)
    }
  }

  const build = branch.latest_build
  const statusInfo = build?.status ? statusConfig[build.status] : null

  return (
    <Card
      ref={setNodeRef}
      style={style}
      className={`p-4 cursor-grab active:cursor-grabbing transition-all ${
        isDragging ? 'shadow-lg ring-2 ring-blue-400' : 'hover:shadow-md'
      }`}
      {...attributes}
      {...listeners}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-sm truncate">{branch.name}</h3>
            {branch.pinned && <Pin className="h-3 w-3 text-gray-400" />}
          </div>
          {build?.commit_sha && (
            <p className="text-xs text-gray-500 font-mono">
              {build.commit_sha.substring(0, 7)}
            </p>
          )}
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {build?.url && (
              <DropdownMenuItem onClick={() => onOpen(build.url!)}>
                <ExternalLink className="mr-2 h-4 w-4" />
                Open Build
              </DropdownMenuItem>
            )}
            {branch.pr_url && (
              <DropdownMenuItem onClick={() => onOpen(branch.pr_url!)}>
                <ExternalLink className="mr-2 h-4 w-4" />
                View PR
              </DropdownMenuItem>
            )}
            {branch.permissions.can_rebuild && (
              <DropdownMenuItem onClick={handleRebuild} disabled={isRebuilding}>
                <RefreshCw className={`mr-2 h-4 w-4 ${isRebuilding ? 'animate-spin' : ''}`} />
                Rebuild
              </DropdownMenuItem>
            )}
            {branch.permissions.can_promote && (
              <DropdownMenuItem onClick={() => onPromote(branch)}>
                <ArrowRight className="mr-2 h-4 w-4" />
                Promote
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Build Status */}
      {statusInfo && (
        <Badge className={`${statusInfo.className} mb-3`} variant="secondary">
          {statusInfo.label}
        </Badge>
      )}

      {/* Build Info */}
      <div className="space-y-1 text-xs text-gray-600">
        <div className="flex justify-between">
          <span className="text-gray-500">Duration</span>
          <span>{formatDuration(build?.duration_s)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Last build</span>
          <span>{formatTimestamp(build?.finished_at || build?.started_at)}</span>
        </div>
      </div>
    </Card>
  )
}

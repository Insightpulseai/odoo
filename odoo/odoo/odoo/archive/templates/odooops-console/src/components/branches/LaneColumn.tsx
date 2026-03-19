'use client'

import { useDroppable } from '@dnd-kit/core'
import { BranchCard } from './BranchCard'
import type { BranchCardDTO, Stage } from '@/lib/types/branches'

interface LaneColumnProps {
  stage: Stage
  branches: BranchCardDTO[]
  onPromote: (branch: BranchCardDTO) => void
  onRebuild: (branchId: string) => void
  onOpen: (url: string) => void
}

const stageConfig: Record<Stage, { title: string; description: string; color: string }> = {
  production: {
    title: 'Production',
    description: 'Live environment',
    color: 'border-green-200 bg-green-50/50'
  },
  staging: {
    title: 'Staging',
    description: 'Pre-production testing',
    color: 'border-yellow-200 bg-yellow-50/50'
  },
  dev: {
    title: 'Development',
    description: 'Feature branches',
    color: 'border-blue-200 bg-blue-50/50'
  }
}

export function LaneColumn({ stage, branches, onPromote, onRebuild, onOpen }: LaneColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: stage,
    data: { stage }
  })

  const config = stageConfig[stage]

  return (
    <div className="flex flex-col h-full">
      {/* Lane Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-lg font-semibold">{config.title}</h2>
          <span className="text-sm text-gray-500">{branches.length}</span>
        </div>
        <p className="text-xs text-gray-500">{config.description}</p>
      </div>

      {/* Drop Zone */}
      <div
        ref={setNodeRef}
        className={`
          flex-1 rounded-lg border-2 border-dashed p-4 transition-all
          ${config.color}
          ${isOver ? 'ring-2 ring-blue-400 border-blue-400 bg-blue-50' : 'border-gray-200'}
          ${branches.length === 0 ? 'flex items-center justify-center' : ''}
        `}
      >
        {branches.length === 0 ? (
          <div className="text-center text-sm text-gray-400">
            No branches
          </div>
        ) : (
          <div className="space-y-3">
            {branches.map((branch) => (
              <BranchCard
                key={branch.id}
                branch={branch}
                onPromote={onPromote}
                onRebuild={onRebuild}
                onOpen={onOpen}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

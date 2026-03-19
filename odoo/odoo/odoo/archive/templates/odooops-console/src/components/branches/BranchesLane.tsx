'use client'

import { useState, useCallback } from 'react'
import { DndContext, DragEndEvent, DragOverlay, closestCenter } from '@dnd-kit/core'
import { toast } from 'sonner'
import { LaneColumn } from './LaneColumn'
import { BranchCard } from './BranchCard'
import { PromoteDialog } from './PromoteDialog'
import { requestPromotion, requestRebuild } from '@/lib/rpc/branches'
import type { BranchCardDTO, Stage } from '@/lib/types/branches'

interface BranchesLaneProps {
  initialData: BranchCardDTO[]
  projectId: string
}

export function BranchesLane({ initialData, projectId }: BranchesLaneProps) {
  const [branches, setBranches] = useState<BranchCardDTO[]>(initialData)
  const [activeBranch, setActiveBranch] = useState<BranchCardDTO | null>(null)
  const [promoteDialogOpen, setPromoteDialogOpen] = useState(false)
  const [promotionDetails, setPromotionDetails] = useState<{
    branch: BranchCardDTO
    fromStage: Stage
    toStage: Stage
  } | null>(null)

  // Group branches by stage
  const getBranchesByStage = (stage: Stage) =>
    branches.filter((b) => b.stage === stage)

  const productionBranches = getBranchesByStage('production')
  const stagingBranches = getBranchesByStage('staging')
  const devBranches = getBranchesByStage('dev')

  // Handle drag start
  const handleDragStart = (event: DragEndEvent) => {
    const branch = event.active.data.current as BranchCardDTO
    setActiveBranch(branch)
  }

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    setActiveBranch(null)

    const { active, over } = event

    if (!over) return

    const branch = active.data.current as BranchCardDTO
    const targetStage = over.id as Stage

    // Don't allow drop in same stage
    if (branch.stage === targetStage) return

    // Validate promotion direction
    const stageOrder: Record<Stage, number> = { dev: 0, staging: 1, production: 2 }
    const fromOrder = stageOrder[branch.stage]
    const toOrder = stageOrder[targetStage]

    if (toOrder < fromOrder) {
      toast.error('Cannot demote branches. Use rollback instead.')
      return
    }

    // Check if can promote
    if (!branch.permissions.can_promote) {
      toast.error('You do not have permission to promote this branch')
      return
    }

    // Open promotion dialog
    setPromotionDetails({
      branch,
      fromStage: branch.stage,
      toStage: targetStage
    })
    setPromoteDialogOpen(true)
  }

  // Handle promotion confirmation
  const handlePromoteConfirm = async (reason?: string) => {
    if (!promotionDetails) return

    const { branch, toStage } = promotionDetails

    // Optimistic update
    const optimisticBranches = branches.map((b) =>
      b.id === branch.id ? { ...b, stage: toStage } : b
    )
    setBranches(optimisticBranches)

    try {
      const result = await requestPromotion(projectId, branch.id, toStage, reason)

      if (result.success) {
        toast.success(result.message || 'Branch promoted successfully')
        setPromoteDialogOpen(false)
        setPromotionDetails(null)
      } else {
        // Revert on failure
        setBranches(branches)
        toast.error(result.message || 'Failed to promote branch')
      }
    } catch (error) {
      // Revert on error
      setBranches(branches)
      toast.error('An error occurred while promoting the branch')
      console.error('Promotion error:', error)
    }
  }

  // Handle promotion cancel
  const handlePromoteCancel = () => {
    setPromoteDialogOpen(false)
    setPromotionDetails(null)
  }

  // Handle manual promote button
  const handlePromote = (branch: BranchCardDTO) => {
    const stageOrder: Stage[] = ['dev', 'staging', 'production']
    const currentIndex = stageOrder.indexOf(branch.stage)
    const nextStage = stageOrder[currentIndex + 1]

    if (!nextStage) {
      toast.error('Branch is already in production')
      return
    }

    setPromotionDetails({
      branch,
      fromStage: branch.stage,
      toStage: nextStage
    })
    setPromoteDialogOpen(true)
  }

  // Handle rebuild
  const handleRebuild = async (branchId: string) => {
    try {
      const result = await requestRebuild(projectId, branchId)

      if (result.success) {
        toast.success('Build started successfully')
        // In a real app, you'd update the branch's build status
      } else {
        toast.error(result.message || 'Failed to start build')
      }
    } catch (error) {
      toast.error('An error occurred while starting the build')
      console.error('Rebuild error:', error)
    }
  }

  // Handle open URL
  const handleOpen = useCallback((url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer')
  }, [])

  return (
    <>
      <DndContext
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-12rem)]">
          <LaneColumn
            stage="production"
            branches={productionBranches}
            onPromote={handlePromote}
            onRebuild={handleRebuild}
            onOpen={handleOpen}
          />
          <LaneColumn
            stage="staging"
            branches={stagingBranches}
            onPromote={handlePromote}
            onRebuild={handleRebuild}
            onOpen={handleOpen}
          />
          <LaneColumn
            stage="dev"
            branches={devBranches}
            onPromote={handlePromote}
            onRebuild={handleRebuild}
            onOpen={handleOpen}
          />
        </div>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeBranch ? (
            <BranchCard
              branch={activeBranch}
              onPromote={handlePromote}
              onRebuild={handleRebuild}
              onOpen={handleOpen}
            />
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Promotion Dialog */}
      {promotionDetails && (
        <PromoteDialog
          open={promoteDialogOpen}
          fromStage={promotionDetails.fromStage}
          toStage={promotionDetails.toStage}
          branch={promotionDetails.branch}
          onConfirm={handlePromoteConfirm}
          onCancel={handlePromoteCancel}
        />
      )}
    </>
  )
}

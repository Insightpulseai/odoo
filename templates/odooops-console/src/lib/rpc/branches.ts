import { createClient } from "@/lib/supabase/client";
import type { Stage } from "@/lib/types/branches";

interface RpcResult {
  success: boolean;
  message?: string;
  build_id?: string;
}

/**
 * Request promotion of a branch to a target stage.
 * Calls the ops.request_promotion Supabase RPC function.
 */
export async function requestPromotion(
  projectId: string,
  branchId: string,
  targetStage: Stage,
  reason?: string
): Promise<RpcResult> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc("request_promotion", {
    p_project_id: projectId,
    p_branch_id: branchId,
    p_target_stage: targetStage,
    p_reason: reason ?? "",
  });

  if (error) {
    return { success: false, message: error.message };
  }

  return (data as RpcResult) ?? { success: true };
}

/**
 * Request a rebuild of a branch.
 * Calls the ops.request_rebuild Supabase RPC function.
 */
export async function requestRebuild(
  projectId: string,
  branchId: string
): Promise<RpcResult> {
  const supabase = createClient();
  const { data, error } = await supabase.rpc("request_rebuild", {
    p_project_id: projectId,
    p_branch_id: branchId,
  });

  if (error) {
    return { success: false, message: error.message };
  }

  return (data as RpcResult) ?? { success: true };
}

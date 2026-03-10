export type Stage = "dev" | "staging" | "production";

export type BuildStatus = "green" | "yellow" | "red" | "running";

export interface BranchBuildDTO {
  id: string;
  status: BuildStatus;
  commit_sha: string | null;
  started_at: string | null;
  finished_at: string | null;
  duration_s: number | null;
  url: string | null;
}

export interface BranchPermissions {
  can_promote: boolean;
  can_rebuild: boolean;
  can_rollback: boolean;
}

export interface BranchCardDTO {
  id: string;
  name: string;
  stage: Stage;
  pinned: boolean;
  pr_url: string | null;
  latest_build: BranchBuildDTO | null;
  permissions: BranchPermissions;
}

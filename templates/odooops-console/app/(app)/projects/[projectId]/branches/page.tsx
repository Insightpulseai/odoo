import { createSupabaseServerClient } from "@/lib/supabase/server";
import Link from "next/link";

interface Branch {
  id: string;
  name: string;
  stage: "production" | "staging" | "development";
  status: string;
  last_build_status: string | null;
  last_build_at: string | null;
  git_ref: string | null;
  last_build_id: string | null;
  build_count: number;
}

function formatRelativeTime(date: string | null): string {
  if (!date) return "Never";
  const ms = Date.now() - new Date(date).getTime();
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(ms / 3600000);
  const days = Math.floor(ms / 86400000);

  if (days > 0) return `${days}d ago`;
  if (hours > 0) return `${hours}h ago`;
  if (minutes > 0) return `${minutes}m ago`;
  return "Just now";
}

function getBranchStatus(branch: Branch): "healthy" | "building" | "failed" | "unknown" {
  if (branch.status === "building") return "building";
  if (branch.status === "error") return "failed";

  switch (branch.last_build_status) {
    case "success":
      return "healthy";
    case "running":
      return "building";
    case "failed":
      return "failed";
    default:
      return "unknown";
  }
}

export default async function BranchesPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;

  const supabase = createSupabaseServerClient();

  const { data: branches, error } = await supabase.rpc("ops.project_branches", {
    p_project_id: projectId,
  });

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-md bg-red-50 p-4">
          <h3 className="text-sm font-medium text-red-800">Error loading branches</h3>
          <p className="mt-2 text-sm text-red-700">{error.message}</p>
        </div>
      </div>
    );
  }

  const productionBranches = (branches || []).filter((b: Branch) => b.stage === "production");
  const stagingBranches = (branches || []).filter((b: Branch) => b.stage === "staging");
  const developmentBranches = (branches || []).filter((b: Branch) => b.stage === "development");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Branches</h1>
        <p className="text-sm text-gray-600 mt-1">
          3-stage deployment pipeline: Production → Staging → Development
        </p>
      </div>

      {/* 3-Lane Deployment Pipeline */}
      <div className="grid grid-cols-3 gap-6">
        {/* Production Lane */}
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold">Production</h2>
            <p className="text-xs text-gray-500">Live environment</p>
          </div>
          <div className="space-y-3">
            {productionBranches.map((branch: Branch) => (
              <BranchCard
                key={branch.id}
                branch={branch}
                projectId={projectId}
              />
            ))}
          </div>
        </div>

        {/* Staging Lane */}
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold">Staging</h2>
            <p className="text-xs text-gray-500">Pre-production testing</p>
          </div>
          <div className="space-y-3">
            {stagingBranches.map((branch: Branch) => (
              <BranchCard
                key={branch.id}
                branch={branch}
                projectId={projectId}
              />
            ))}
          </div>
        </div>

        {/* Development Lane */}
        <div>
          <div className="mb-4">
            <h2 className="text-lg font-semibold">Development</h2>
            <p className="text-xs text-gray-500">Feature branches</p>
          </div>
          <div className="space-y-3">
            {developmentBranches.map((branch: Branch) => (
              <BranchCard
                key={branch.id}
                branch={branch}
                projectId={projectId}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function BranchCard({
  branch,
  projectId,
}: {
  branch: Branch;
  projectId: string;
}) {
  const status = getBranchStatus(branch);

  const statusColors = {
    healthy: "bg-green-100 text-green-800",
    building: "bg-yellow-100 text-yellow-800",
    failed: "bg-red-100 text-red-800",
    unknown: "bg-gray-100 text-gray-800",
  };

  const content = (
    <div className="rounded-lg border border-gray-200 bg-white p-4 hover:border-gray-300 transition">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-sm truncate flex-1">{branch.name}</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs ${statusColors[status]}`}>
          {status}
        </span>
      </div>
      <div className="space-y-1 text-xs text-gray-600">
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Builds</span>
          <span>{branch.build_count || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-500">Last deploy</span>
          <span>{formatRelativeTime(branch.last_build_at)}</span>
        </div>
      </div>
    </div>
  );

  // If last build exists, make clickable to build detail
  if (branch.last_build_id) {
    return (
      <Link href={`/app/projects/${projectId}/builds/${branch.last_build_id}/logs`}>
        {content}
      </Link>
    );
  }

  return <div>{content}</div>;
}

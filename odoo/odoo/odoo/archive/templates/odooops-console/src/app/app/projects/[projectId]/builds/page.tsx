import { createClient } from "@/lib/supabase/server";
import Link from "next/link";

interface Build {
  id: string;
  branchName: string;
  commitSha: string;
  status: "success" | "building" | "failed";
  createdAt: string;
  duration?: string;
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

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}m ${secs}s`;
}

export default async function BuildsPage({
  params,
}: {
  params: { projectId: string };
}) {
  const supabase = createClient();

  // Get all branches for this project
  const { data: branches, error: branchesError } = await supabase.rpc(
    "ops.project_branches",
    { p_project_id: params.projectId }
  );

  if (branchesError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Builds</h1>
        </div>
        <div className="rounded-md bg-red-50 p-4">
          <h3 className="text-sm font-medium text-red-800">
            Error loading builds
          </h3>
          <p className="mt-2 text-sm text-red-700">{branchesError.message}</p>
        </div>
      </div>
    );
  }

  if (!branches || branches.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Builds</h1>
        </div>
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
          <h3 className="text-lg font-medium text-gray-900">No branches yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Create a branch to start building.
          </p>
        </div>
      </div>
    );
  }

  // Fetch builds for all branches
  const branchBuildsPromises = branches.map((branch: any) =>
    supabase
      .rpc("ops.branch_builds", { p_branch_id: branch.id })
      .then((res) => ({
        branchId: branch.id,
        branchName: branch.name,
        builds: res.data || [],
      }))
  );

  const branchBuildsResults = await Promise.all(branchBuildsPromises);
  const buildsByBranch: Record<string, any[]> = {};
  branchBuildsResults.forEach((result) => {
    buildsByBranch[result.branchName] = result.builds;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Builds</h1>
        <p className="text-sm text-gray-600 mt-1">
          Build history grid (rows = branches, cells = builds)
        </p>
      </div>

      {/* Builds Grid */}
      <div className="space-y-4">
        {branches.map((branch: any) => (
          <div key={branch.id} className="border border-gray-200 rounded-lg">
            {/* Branch Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <h3 className="font-semibold text-sm">
                {branch.name}
                <span className="ml-2 text-xs text-gray-500">
                  ({branch.stage})
                </span>
              </h3>
            </div>

            {/* Build Cells */}
            <div className="p-4">
              <div className="flex gap-3 overflow-x-auto">
                {buildsByBranch[branch.name]?.length > 0 ? (
                  buildsByBranch[branch.name].map((build: any) => (
                    <BuildCell
                      key={build.id}
                      build={{
                        id: build.id,
                        branchName: branch.name,
                        commitSha:
                          build.commit_sha?.substring(0, 7) || "unknown",
                        status: build.status,
                        createdAt: formatRelativeTime(build.created_at),
                        duration: formatDuration(build.duration_seconds),
                      }}
                      projectId={params.projectId}
                    />
                  ))
                ) : (
                  <div className="text-sm text-gray-500">
                    No builds for this branch
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function BuildCell({
  build,
  projectId,
}: {
  build: Build;
  projectId: string;
}) {
  const statusColors: Record<string, string> = {
    success: "border-green-500 bg-green-50",
    running: "border-yellow-500 bg-yellow-50 animate-pulse",
    building: "border-yellow-500 bg-yellow-50 animate-pulse",
    failed: "border-red-500 bg-red-50",
    queued: "border-gray-300 bg-gray-50",
    cancelled: "border-gray-400 bg-gray-100",
  };

  const statusIcons: Record<string, string> = {
    success: "✓",
    running: "⟳",
    building: "⟳",
    failed: "✗",
    queued: "⏳",
    cancelled: "⊘",
  };

  return (
    <Link
      href={`/app/projects/${projectId}/builds/${build.id}/logs`}
      className={`flex-shrink-0 w-32 border-2 rounded-lg p-3 hover:shadow-md transition ${
        statusColors[build.status] || "border-gray-300 bg-gray-50"
      }`}
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold">
            {statusIcons[build.status] || "?"}
          </span>
          <span className="text-xs text-gray-600">{build.createdAt}</span>
        </div>
        <div className="space-y-1">
          <div className="text-xs font-mono truncate">{build.commitSha}</div>
          {build.duration && build.duration !== "—" && (
            <div className="text-xs text-gray-600">{build.duration}</div>
          )}
          {(build.status === "building" || build.status === "running") && (
            <div className="text-xs text-gray-600">In progress...</div>
          )}
        </div>
      </div>
    </Link>
  );
}

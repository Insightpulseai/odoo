import { createClient } from "@/lib/supabase/server";
import Link from "next/link";
import { BuildTabs } from "@/components/odoo-sh/BuildTabs";

export default async function BuildLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ projectId: string; buildId: string }>;
}) {
  const { projectId, buildId } = await params;
  const supabase = createClient();

  // Call RPC: ops.ui_build_detail(p_build_id)
  // For now, use demo data until RPC is implemented
  const buildDetail = {
    id: buildId,
    branchName: "main",
    commitSha: "a3f2d91",
    commitMessage: "feat(auth): implement JWT authentication",
    status: "success",
    createdAt: "2024-02-12 14:30:00",
    duration: "3m 45s",
  };

  const projectName = "Production ERP"; // In production, fetch from project

  const statusColors = {
    success: "bg-green-100 text-green-800",
    building: "bg-yellow-100 text-yellow-800",
    failed: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2 text-sm">
          <li>
            <Link href="/app/projects" className="text-blue-600 hover:underline">
              Projects
            </Link>
          </li>
          <li>
            <span className="text-gray-400">/</span>
          </li>
          <li>
            <Link
              href={`/app/projects/${projectId}/branches`}
              className="text-blue-600 hover:underline"
            >
              {projectName}
            </Link>
          </li>
          <li>
            <span className="text-gray-400">/</span>
          </li>
          <li>
            <Link
              href={`/app/projects/${projectId}/builds`}
              className="text-blue-600 hover:underline"
            >
              Builds
            </Link>
          </li>
          <li>
            <span className="text-gray-400">/</span>
          </li>
          <li>
            <span className="font-medium">{buildDetail.commitSha}</span>
          </li>
        </ol>
      </nav>

      {/* Build Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold font-mono">
                {buildDetail.commitSha}
              </h1>
              <span
                className={`rounded-full px-3 py-1 text-sm font-medium ${
                  statusColors[buildDetail.status as keyof typeof statusColors]
                }`}
              >
                {buildDetail.status}
              </span>
            </div>
            <p className="text-gray-700">{buildDetail.commitMessage}</p>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div>
                <span className="text-gray-500">Branch:</span>{" "}
                <span className="font-medium">{buildDetail.branchName}</span>
              </div>
              <div>
                <span className="text-gray-500">Created:</span>{" "}
                <span>{buildDetail.createdAt}</span>
              </div>
              {buildDetail.duration && (
                <div>
                  <span className="text-gray-500">Duration:</span>{" "}
                  <span>{buildDetail.duration}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Build Tools Tabs */}
      <BuildTabs projectId={projectId} buildId={buildId} />

      {/* Page Content */}
      <div>{children}</div>
    </div>
  );
}

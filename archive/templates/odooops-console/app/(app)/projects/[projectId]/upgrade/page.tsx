import { createClient } from "@/lib/supabase/server";

export default async function UpgradePage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = await params;

  const supabase = createClient();

  // Current and available versions
  const currentVersion = "19.0";
  const availableVersions = ["19.0.1", "19.1.0", "20.0"];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Version Upgrade</h1>
        <p className="text-sm text-gray-600 mt-1">
          Manage Odoo version upgrades and migrations
        </p>
      </div>

      {/* Current Version */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Current Version</h2>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              Odoo {currentVersion}
            </p>
            <p className="text-sm text-gray-600 mt-1">Last updated: 2024-01-15</p>
          </div>
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Available Upgrades */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold">Available Upgrades</h2>
        </div>

        <div className="divide-y divide-gray-200">
          {availableVersions.map((version) => (
            <div key={version} className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Odoo {version}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {version === "19.0.1"
                      ? "Patch release with bug fixes and security improvements"
                      : version === "19.1.0"
                      ? "Minor release with new features and improvements"
                      : "Major release with breaking changes"}
                  </p>

                  {/* What's New */}
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      What's New
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                      <li>Performance improvements in accounting module</li>
                      <li>New dashboard widgets for sales analytics</li>
                      <li>Enhanced mobile responsiveness</li>
                      {version === "20.0" && (
                        <>
                          <li className="text-orange-600">
                            ⚠️ Requires PostgreSQL 16+
                          </li>
                          <li className="text-orange-600">
                            ⚠️ Breaking changes in API
                          </li>
                        </>
                      )}
                    </ul>
                  </div>
                </div>

                <div className="ml-6">
                  <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                    Upgrade to {version}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upgrade Process */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-yellow-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div>
            <h3 className="text-sm font-semibold text-yellow-900">
              Before Upgrading
            </h3>
            <ul className="list-disc list-inside space-y-1 text-sm text-yellow-800 mt-2">
              <li>Automatic backup will be created before upgrade</li>
              <li>Estimated downtime: 15-30 minutes</li>
              <li>Test in staging environment first</li>
              <li>Review module compatibility</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

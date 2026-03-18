"use client";

import { useState } from "react";
// TODO: Restore when UI components are available
// import { SupabaseManagerDialog } from "@/components/SupabaseManagerDialog";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    projectName: "Production ERP",
    domain: "erp.insightpulseai.com",
    autoBackup: true,
    backupSchedule: "daily",
    retentionDays: 30,
    maintenanceWindow: "02:00-04:00 UTC",
    autoUpdates: false,
    notificationEmail: "ops@insightpulseai.com",
  });

  // TODO: Fetch from ops.projects.supabase_project_ref
  const supabaseProjectRef = "spdtwktxdalcfigzeqrz"; // Placeholder

  const [showSupabaseManager, setShowSupabaseManager] = useState(false);

  const handleSave = () => {
    // In production, call ops.ui_update_project_settings
    console.log("Saving settings:", settings);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Project Settings</h1>
        <p className="text-sm text-gray-600 mt-1">
          Configure project settings and preferences
        </p>
      </div>

      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">General</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Project Name
              </label>
              <input
                type="text"
                value={settings.projectName}
                onChange={(e) =>
                  setSettings({ ...settings, projectName: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Domain
              </label>
              <input
                type="text"
                value={settings.domain}
                onChange={(e) =>
                  setSettings({ ...settings, domain: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notification Email
              </label>
              <input
                type="email"
                value={settings.notificationEmail}
                onChange={(e) =>
                  setSettings({ ...settings, notificationEmail: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Backup Settings */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Backups</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Automatic Backups
                </label>
                <p className="text-xs text-gray-500 mt-0.5">
                  Enable scheduled database backups
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoBackup}
                  onChange={(e) =>
                    setSettings({ ...settings, autoBackup: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Backup Schedule
              </label>
              <select
                value={settings.backupSchedule}
                onChange={(e) =>
                  setSettings({ ...settings, backupSchedule: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retention Period (days)
              </label>
              <input
                type="number"
                value={settings.retentionDays}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    retentionDays: parseInt(e.target.value),
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Maintenance Settings */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Maintenance</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Maintenance Window (UTC)
              </label>
              <input
                type="text"
                value={settings.maintenanceWindow}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    maintenanceWindow: e.target.value,
                  })
                }
                placeholder="HH:MM-HH:MM UTC"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Preferred time window for automatic updates and maintenance
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Auto Updates
                </label>
                <p className="text-xs text-gray-500 mt-0.5">
                  Automatically apply security patches
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.autoUpdates}
                  onChange={(e) =>
                    setSettings({ ...settings, autoUpdates: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Supabase Integration */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Supabase Integration</h2>

          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Manage your Supabase project database, storage, authentication, Edge Functions, and more.
            </p>

            {supabaseProjectRef ? (
              <button
                onClick={() => setShowSupabaseManager(true)}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 inline-flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                Manage Supabase
              </button>
            ) : (
              <div className="text-sm text-gray-500">
                <p>No Supabase project linked to this OdooOps project.</p>
                <p className="mt-1">Contact your administrator to configure Supabase integration.</p>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-3">
          <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50">
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Save Changes
          </button>
        </div>
      </div>

      {/* Supabase Manager Dialog - TODO: Restore when UI components available */}
      {/* {supabaseProjectRef && (
        <SupabaseManagerDialog
          open={showSupabaseManager}
          onOpenChange={setShowSupabaseManager}
          projectRef={supabaseProjectRef}
        />
      )} */}
    </div>
  );
}

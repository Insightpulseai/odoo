import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'OdooOps Documentation',
  description: 'Platform documentation for Odoo 19 + OdooOps Console',
};

export default function DocsIndexPage() {
  return (
    <div className="prose max-w-none p-8">
      <h1>OdooOps Platform Documentation</h1>
      <p>Select a topic from the sidebar.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-8">
        <div className="border p-4 rounded-lg hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold mb-2">Apps</h2>
          <ul className="list-disc pl-5">
            <li><a href="/docs/apps/odoo" className="text-blue-600 hover:underline">Odoo Runtime</a></li>
            <li><a href="/docs/apps/odooops" className="text-blue-600 hover:underline">Console Manual</a></li>
          </ul>
        </div>

        <div className="border p-4 rounded-lg hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold mb-2">How-to</h2>
          <ul className="list-disc pl-5">
            <li><a href="/docs/howto/deploy" className="text-blue-600 hover:underline">Deploy Modules</a></li>
            <li><a href="/docs/howto/backup" className="text-blue-600 hover:underline">Backup & Restore</a></li>
          </ul>
        </div>

        <div className="border p-4 rounded-lg hover:shadow-md transition-shadow">
          <h2 className="text-xl font-bold mb-2">Reference</h2>
          <p className="text-sm text-gray-500 mb-2">Auto-generated from runtime snapshot</p>
          <ul className="list-disc pl-5">
            <li><a href="/docs/stack/runtime" className="text-blue-600 hover:underline">Runtime Snapshot</a></li>
            <li><a href="/docs/stack/skills" className="text-blue-600 hover:underline">Agent Skills</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
}

'use client';

import { TablesBrowser } from '@/components/tables-browser';

export default function TablesPage() {
  return (
    <div className="min-h-screen bg-surface-900 p-6">
      <div className="max-w-7xl mx-auto">
        <TablesBrowser />
      </div>
    </div>
  );
}

'use client';

import { ReactNode } from 'react';

interface PageContainerProps {
  children: ReactNode;
}

export function PageContainer({ children }: PageContainerProps) {
  return (
    <div className="min-h-screen bg-surface-950 pl-64">
      <div className="flex flex-col min-h-screen">{children}</div>
    </div>
  );
}

export function PageContent({ children }: PageContainerProps) {
  return <main className="flex-1 p-6">{children}</main>;
}

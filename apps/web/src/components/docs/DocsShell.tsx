'use client';

import React, { useState } from 'react';
import { DocsHeader } from './DocsHeader';
import { DocsSidebar } from './DocsSidebar';
import { DocsToc } from './DocsToc';
import { DocsFooter } from './DocsFooter';
import { cn } from '@/lib/utils';

export interface TocHeading {
  id: string;
  text: string;
  level: 2 | 3;
}

export interface DocsShellProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  headings?: TocHeading[];
  editUrl?: string;
  showToc?: boolean;
  showFooter?: boolean;
}

export function DocsShell({
  children,
  title,
  description,
  headings = [],
  editUrl,
  showToc = true,
  showFooter = true,
}: DocsShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <DocsHeader onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main layout */}
      <div className="flex">
        {/* Sidebar */}
        <aside
          className={cn(
            'fixed top-14 z-40 h-[calc(100vh-56px)] w-[280px] border-r border-border bg-background transition-transform duration-200 lg:sticky lg:block lg:w-[280px]',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
          )}
        >
          <DocsSidebar onNavigate={() => setSidebarOpen(false)} />
        </aside>

        {/* Content area */}
        <main className="flex-1 min-w-0">
          <div className="flex">
            {/* Main content */}
            <article className="flex-1 min-w-0 px-6 py-8 lg:px-8 lg:py-10 max-w-4xl">
              {/* Page header */}
              {(title || description) && (
                <header className="mb-8">
                  {title && (
                    <h1 className="text-3xl font-bold tracking-tight text-foreground lg:text-4xl">
                      {title}
                    </h1>
                  )}
                  {description && (
                    <p className="mt-2 text-lg text-foreground-light">
                      {description}
                    </p>
                  )}
                </header>
              )}

              {/* Page content */}
              <div className="prose prose-slate dark:prose-invert max-w-none">
                {children}
              </div>

              {/* Edit link */}
              {editUrl && (
                <div className="mt-12 border-t border-border pt-6">
                  <a
                    href={editUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-foreground-light hover:text-foreground"
                  >
                    <EditIcon className="h-4 w-4" />
                    Edit this page on GitHub
                  </a>
                </div>
              )}

              {/* Feedback widget */}
              <div className="mt-6 flex items-center gap-4">
                <span className="text-sm text-foreground-light">
                  Is this helpful?
                </span>
                <div className="flex gap-2">
                  <button
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm text-foreground-light hover:bg-muted hover:text-foreground"
                    aria-label="No, this is not helpful"
                  >
                    <ThumbsDownIcon className="h-4 w-4" />
                    No
                  </button>
                  <button
                    className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm text-foreground-light hover:bg-muted hover:text-foreground"
                    aria-label="Yes, this is helpful"
                  >
                    <ThumbsUpIcon className="h-4 w-4" />
                    Yes
                  </button>
                </div>
              </div>
            </article>

            {/* Table of Contents */}
            {showToc && headings.length > 0 && (
              <aside className="hidden w-64 shrink-0 xl:block">
                <DocsToc headings={headings} />
              </aside>
            )}
          </div>

          {/* Footer */}
          {showFooter && <DocsFooter />}
        </main>
      </div>
    </div>
  );
}

function EditIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

function ThumbsUpIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M7 10v12" />
      <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z" />
    </svg>
  );
}

function ThumbsDownIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M17 14V2" />
      <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z" />
    </svg>
  );
}

export default DocsShell;

'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export interface NavItem {
  id: string;
  title: string;
  href: string;
}

export interface DocsHeaderProps {
  logo?: React.ReactNode;
  docsLabel?: string;
  navItems?: NavItem[];
  searchPlaceholder?: string;
  dashboardUrl?: string;
  onMenuToggle?: () => void;
}

const defaultNavItems: NavItem[] = [
  { id: 'start', title: 'Start', href: '/docs/guides/getting-started' },
  { id: 'products', title: 'Products', href: '/docs/guides/database' },
  { id: 'build', title: 'Build', href: '/docs/guides/local-development' },
  { id: 'manage', title: 'Manage', href: '/docs/guides/platform' },
  { id: 'reference', title: 'Reference', href: '/docs/reference' },
];

export function DocsHeader({
  logo,
  docsLabel = 'DOCS',
  navItems = defaultNavItems,
  searchPlaceholder = 'Search docs...',
  dashboardUrl = '/dashboard',
  onMenuToggle,
}: DocsHeaderProps) {
  const [searchOpen, setSearchOpen] = useState(false);

  // Handle keyboard shortcut for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen(true);
      }
      if (e.key === 'Escape') {
        setSearchOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-50 h-14 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-full items-center px-4 lg:px-6">
          {/* Mobile menu button */}
          <button
            onClick={onMenuToggle}
            className="mr-4 inline-flex items-center justify-center rounded-md p-2 text-foreground-light hover:bg-muted hover:text-foreground lg:hidden"
            aria-label="Toggle menu"
          >
            <MenuIcon className="h-5 w-5" />
          </button>

          {/* Logo */}
          <Link href="/docs" className="flex items-center gap-2">
            {logo || <DefaultLogo />}
            <span className="font-mono text-xs font-medium uppercase tracking-wider text-foreground-light">
              {docsLabel}
            </span>
          </Link>

          {/* Primary navigation - desktop */}
          <nav className="ml-8 hidden lg:flex">
            <ul className="flex items-center gap-1">
              {navItems.map((item) => (
                <li key={item.id}>
                  <Link
                    href={item.href}
                    className="rounded-md px-3 py-2 text-sm font-medium text-foreground-light hover:bg-muted hover:text-foreground"
                  >
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          {/* Spacer */}
          <div className="flex-1" />

          {/* Search button */}
          <button
            onClick={() => setSearchOpen(true)}
            className="flex items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-1.5 text-sm text-foreground-light hover:bg-muted hover:text-foreground"
          >
            <SearchIcon className="h-4 w-4" />
            <span className="hidden md:inline">{searchPlaceholder}</span>
            <kbd className="ml-2 hidden rounded border border-border bg-background px-1.5 py-0.5 font-mono text-xs md:inline">
              <span className="text-xs">⌘</span>K
            </kbd>
          </button>

          {/* Dashboard link */}
          <Link
            href={dashboardUrl}
            className="ml-4 hidden items-center gap-1 rounded-md px-3 py-2 text-sm font-medium text-foreground-light hover:bg-muted hover:text-foreground md:flex"
          >
            Dashboard
            <ExternalLinkIcon className="h-3 w-3" />
          </Link>
        </div>
      </header>

      {/* Search modal */}
      {searchOpen && (
        <SearchModal
          placeholder={searchPlaceholder}
          onClose={() => setSearchOpen(false)}
        />
      )}
    </>
  );
}

interface SearchModalProps {
  placeholder: string;
  onClose: () => void;
}

function SearchModal({ placeholder, onClose }: SearchModalProps) {
  const [query, setQuery] = useState('');

  return (
    <div className="fixed inset-0 z-[100]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative mx-auto mt-20 w-full max-w-xl px-4">
        <div className="overflow-hidden rounded-lg border border-border bg-background shadow-lg">
          {/* Search input */}
          <div className="flex items-center border-b border-border px-4">
            <SearchIcon className="h-5 w-5 text-foreground-light" />
            <input
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent px-4 py-4 text-foreground outline-none placeholder:text-foreground-light"
              autoFocus
            />
            <button
              onClick={onClose}
              className="rounded border border-border px-2 py-1 text-xs text-foreground-light hover:text-foreground"
            >
              ESC
            </button>
          </div>

          {/* Results */}
          <div className="max-h-80 overflow-y-auto p-2">
            {query ? (
              <p className="p-4 text-center text-sm text-foreground-light">
                No results for &quot;{query}&quot;
              </p>
            ) : (
              <p className="p-4 text-center text-sm text-foreground-light">
                Start typing to search...
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-border px-4 py-2 text-xs text-foreground-light">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="rounded border border-border px-1">↵</kbd>
                to select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="rounded border border-border px-1">↑</kbd>
                <kbd className="rounded border border-border px-1">↓</kbd>
                to navigate
              </span>
            </div>
            <span className="flex items-center gap-1">
              <kbd className="rounded border border-border px-1">esc</kbd>
              to close
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function DefaultLogo() {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 109 113"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-foreground"
    >
      <path
        d="M63.7076 110.284C60.8481 113.885 55.0502 111.912 54.9813 107.314L53.9738 40.0627L99.1935 40.0627C107.384 40.0627 111.952 49.5228 106.859 55.9374L63.7076 110.284Z"
        fill="url(#paint0_linear)"
      />
      <path
        d="M63.7076 110.284C60.8481 113.885 55.0502 111.912 54.9813 107.314L53.9738 40.0627L99.1935 40.0627C107.384 40.0627 111.952 49.5228 106.859 55.9374L63.7076 110.284Z"
        fill="url(#paint1_linear)"
        fillOpacity="0.2"
      />
      <path
        d="M45.317 2.07103C48.1765 -1.53037 53.9745 0.442937 54.0434 5.041L54.4849 72.2922H9.83113C1.64038 72.2922 -2.92775 62.8321 2.1655 56.4175L45.317 2.07103Z"
        fill="currentColor"
      />
      <defs>
        <linearGradient
          id="paint0_linear"
          x1="53.9738"
          y1="54.974"
          x2="94.1635"
          y2="71.8295"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#249361" />
          <stop offset="1" stopColor="#3ECF8E" />
        </linearGradient>
        <linearGradient
          id="paint1_linear"
          x1="36.1558"
          y1="30.578"
          x2="54.4844"
          y2="65.0806"
          gradientUnits="userSpaceOnUse"
        >
          <stop />
          <stop offset="1" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function MenuIcon({ className }: { className?: string }) {
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
      <line x1="4" x2="20" y1="12" y2="12" />
      <line x1="4" x2="20" y1="6" y2="6" />
      <line x1="4" x2="20" y1="18" y2="18" />
    </svg>
  );
}

function SearchIcon({ className }: { className?: string }) {
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
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  );
}

function ExternalLinkIcon({ className }: { className?: string }) {
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
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" x2="21" y1="14" y2="3" />
    </svg>
  );
}

export default DocsHeader;

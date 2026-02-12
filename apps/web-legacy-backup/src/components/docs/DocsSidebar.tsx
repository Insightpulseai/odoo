'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';

export interface NavItem {
  title: string;
  href: string;
  icon?: string;
  children?: NavItem[];
  isExternal?: boolean;
}

export interface NavSection {
  id: string;
  title: string;
  icon?: string;
  items: NavItem[];
}

export interface DocsSidebarProps {
  sections?: NavSection[];
  onNavigate?: () => void;
}

// Default sections matching Supabase Platform + Integrations structure
const defaultSections: NavSection[] = [
  {
    id: 'platform',
    title: 'Platform',
    icon: 'settings',
    items: [
      { title: 'Platform Overview', href: '/docs/guides/platform' },
      {
        title: 'Add-ons',
        href: '/docs/guides/platform/add-ons',
        children: [
          { title: 'Compute Add-ons', href: '/docs/guides/platform/add-ons/compute' },
          { title: 'IPv4 Add-on', href: '/docs/guides/platform/add-ons/ipv4' },
          { title: 'PITR Add-on', href: '/docs/guides/platform/add-ons/pitr' },
        ],
      },
      { title: 'Custom Domains', href: '/docs/guides/platform/custom-domains' },
      {
        title: 'Database Backups',
        href: '/docs/guides/platform/backups',
        children: [
          { title: 'Daily Backups', href: '/docs/guides/platform/backups/daily-backups' },
          { title: 'Point-in-Time Recovery', href: '/docs/guides/platform/backups/pitr' },
        ],
      },
      { title: 'Database Size', href: '/docs/guides/platform/database-size' },
      { title: 'Log Drains', href: '/docs/guides/platform/log-drains' },
      { title: 'Metrics', href: '/docs/guides/platform/metrics' },
      { title: 'Permissions', href: '/docs/guides/platform/permissions' },
    ],
  },
  {
    id: 'integrations',
    title: 'Integrations',
    icon: 'plug',
    items: [
      { title: 'Integrations Overview', href: '/docs/guides/platform/integrations' },
      {
        title: 'Vercel Marketplace',
        href: '/docs/guides/platform/integrations/vercel-marketplace',
        children: [
          { title: 'Vercel + Supabase', href: '/docs/guides/platform/integrations/vercel' },
        ],
      },
      {
        title: 'Auth Providers',
        href: '/docs/guides/platform/integrations/auth-providers',
        children: [
          { title: 'GitHub', href: '/docs/guides/auth/social-login/auth-github' },
          { title: 'Google', href: '/docs/guides/auth/social-login/auth-google' },
          { title: 'Discord', href: '/docs/guides/auth/social-login/auth-discord' },
        ],
      },
      {
        title: 'ORMs & Libraries',
        href: '/docs/guides/platform/integrations/orms',
        children: [
          { title: 'Drizzle', href: '/docs/guides/database/connecting-to-postgres/drizzle' },
          { title: 'Prisma', href: '/docs/guides/database/connecting-to-postgres/prisma' },
        ],
      },
    ],
  },
  {
    id: 'billing',
    title: 'Billing',
    icon: 'credit-card',
    items: [
      { title: 'Billing Overview', href: '/docs/guides/platform/billing' },
      { title: 'Compute Usage', href: '/docs/guides/platform/billing/compute' },
      { title: 'Invoices', href: '/docs/guides/platform/billing/invoices' },
    ],
  },
];

export function DocsSidebar({
  sections = defaultSections,
  onNavigate,
}: DocsSidebarProps) {
  const pathname = usePathname();
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  // Auto-expand sections containing the current path
  useEffect(() => {
    const sectionsToExpand: string[] = [];
    const itemsToExpand: string[] = [];

    sections.forEach((section) => {
      section.items.forEach((item) => {
        if (pathname === item.href || pathname?.startsWith(item.href + '/')) {
          sectionsToExpand.push(section.id);
        }
        if (item.children) {
          item.children.forEach((child) => {
            if (pathname === child.href) {
              sectionsToExpand.push(section.id);
              itemsToExpand.push(item.href);
            }
          });
        }
      });
    });

    setExpandedSections((prev) => [...new Set([...prev, ...sectionsToExpand])]);
    setExpandedItems((prev) => [...new Set([...prev, ...itemsToExpand])]);
  }, [pathname, sections]);

  const toggleSection = (sectionId: string) => {
    setExpandedSections((prev) =>
      prev.includes(sectionId)
        ? prev.filter((id) => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  const toggleItem = (itemHref: string) => {
    setExpandedItems((prev) =>
      prev.includes(itemHref)
        ? prev.filter((href) => href !== itemHref)
        : [...prev, itemHref]
    );
  };

  const isActive = (href: string) => pathname === href;
  const isActiveParent = (href: string) =>
    pathname?.startsWith(href + '/') || false;

  return (
    <nav className="h-full overflow-y-auto px-4 py-6">
      <div className="space-y-6">
        {sections.map((section) => (
          <div key={section.id}>
            {/* Section header */}
            <button
              onClick={() => toggleSection(section.id)}
              className="flex w-full items-center justify-between py-1.5 text-sm font-semibold text-foreground"
            >
              <span className="flex items-center gap-2">
                <SectionIcon icon={section.icon} />
                {section.title}
              </span>
              <ChevronIcon
                className={cn(
                  'h-4 w-4 text-foreground-light transition-transform duration-200',
                  expandedSections.includes(section.id) && 'rotate-90'
                )}
              />
            </button>

            {/* Section items */}
            {expandedSections.includes(section.id) && (
              <ul className="ml-2 mt-2 space-y-1 border-l border-border pl-4">
                {section.items.map((item) => (
                  <li key={item.href}>
                    {item.children ? (
                      // Item with children
                      <div>
                        <button
                          onClick={() => toggleItem(item.href)}
                          className={cn(
                            'flex w-full items-center justify-between rounded-md px-2 py-1.5 text-sm',
                            isActive(item.href) || isActiveParent(item.href)
                              ? 'bg-muted text-brand-link font-medium'
                              : 'text-foreground-light hover:bg-muted hover:text-foreground'
                          )}
                        >
                          <span>{item.title}</span>
                          <ChevronIcon
                            className={cn(
                              'h-3 w-3 transition-transform duration-200',
                              expandedItems.includes(item.href) && 'rotate-90'
                            )}
                          />
                        </button>

                        {/* Children */}
                        {expandedItems.includes(item.href) && (
                          <ul className="ml-4 mt-1 space-y-1">
                            {item.children.map((child) => (
                              <li key={child.href}>
                                <Link
                                  href={child.href}
                                  onClick={onNavigate}
                                  className={cn(
                                    'block rounded-md px-2 py-1.5 text-sm',
                                    isActive(child.href)
                                      ? 'bg-muted text-brand-link font-medium'
                                      : 'text-foreground-light hover:bg-muted hover:text-foreground'
                                  )}
                                >
                                  {child.title}
                                </Link>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ) : (
                      // Simple item
                      <Link
                        href={item.href}
                        onClick={onNavigate}
                        className={cn(
                          'block rounded-md px-2 py-1.5 text-sm',
                          isActive(item.href)
                            ? 'bg-muted text-brand-link font-medium'
                            : 'text-foreground-light hover:bg-muted hover:text-foreground'
                        )}
                      >
                        {item.title}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </nav>
  );
}

function SectionIcon({ icon }: { icon?: string }) {
  const iconMap: Record<string, React.ReactNode> = {
    settings: <SettingsIcon className="h-4 w-4" />,
    plug: <PlugIcon className="h-4 w-4" />,
    'credit-card': <CreditCardIcon className="h-4 w-4" />,
    shield: <ShieldIcon className="h-4 w-4" />,
    rocket: <RocketIcon className="h-4 w-4" />,
    'help-circle': <HelpCircleIcon className="h-4 w-4" />,
  };

  return iconMap[icon || ''] || null;
}

function ChevronIcon({ className }: { className?: string }) {
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
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}

function SettingsIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

function PlugIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 22v-5"/>
      <path d="M9 8V2"/>
      <path d="M15 8V2"/>
      <path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>
    </svg>
  );
}

function CreditCardIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <rect width="20" height="14" x="2" y="5" rx="2"/>
      <line x1="2" x2="22" y1="10" y2="10"/>
    </svg>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/>
    </svg>
  );
}

function RocketIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/>
      <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>
      <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>
      <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>
    </svg>
  );
}

function HelpCircleIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="12" cy="12" r="10"/>
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
      <path d="M12 17h.01"/>
    </svg>
  );
}

export default DocsSidebar;

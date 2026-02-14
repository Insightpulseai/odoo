'use client';

import React from 'react';
import Link from 'next/link';

export interface FooterLink {
  label: string;
  href: string;
  icon?: string;
  description?: string;
}

export interface SocialLink {
  platform: 'twitter' | 'github' | 'discord' | 'youtube';
  href: string;
}

export interface DocsFooterProps {
  primaryLinks?: FooterLink[];
  secondaryLinks?: FooterLink[];
  socialLinks?: SocialLink[];
  copyright?: string;
}

const defaultPrimaryLinks: FooterLink[] = [
  {
    label: 'Need some help?',
    description: 'Contact support',
    href: '/support',
    icon: 'life-buoy',
  },
  {
    label: 'Latest updates',
    description: 'View changelog',
    href: '/changelog',
    icon: 'newspaper',
  },
];

const defaultSecondaryLinks: FooterLink[] = [
  { label: 'Contributing', href: '/docs/guides/resources/contributing' },
  { label: 'Author Styleguide', href: '/docs/guides/resources/styleguide' },
  { label: 'Open Source', href: 'https://github.com/supabase/supabase' },
];

const defaultSocialLinks: SocialLink[] = [
  { platform: 'twitter', href: 'https://twitter.com/supabase' },
  { platform: 'github', href: 'https://github.com/supabase' },
  { platform: 'discord', href: 'https://discord.supabase.com' },
  { platform: 'youtube', href: 'https://youtube.com/c/supabase' },
];

export function DocsFooter({
  primaryLinks = defaultPrimaryLinks,
  secondaryLinks = defaultSecondaryLinks,
  socialLinks = defaultSocialLinks,
  copyright = 'Supabase Inc',
}: DocsFooterProps) {
  return (
    <footer
      className="border-t border-border bg-background px-6 py-8 lg:px-8"
      aria-label="footer"
      role="contentinfo"
    >
      {/* Primary links */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {primaryLinks.map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="group flex items-start gap-3 rounded-lg border border-border p-4 hover:bg-muted"
          >
            <FooterIcon icon={link.icon} />
            <div>
              <span className="block text-sm font-medium text-foreground group-hover:text-brand-link">
                {link.label}
              </span>
              {link.description && (
                <span className="text-sm text-foreground-light">
                  {link.description}
                </span>
              )}
            </div>
          </a>
        ))}
      </div>

      {/* Divider */}
      <hr className="my-8 border-border" />

      {/* Secondary section */}
      <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
        {/* Copyright and links */}
        <div className="flex flex-col items-center gap-4 md:flex-row">
          <span className="text-sm text-foreground-light">
            &copy; {new Date().getFullYear()} {copyright}
          </span>
          <span className="hidden text-foreground-light md:inline">|</span>
          <nav className="flex flex-wrap items-center gap-4">
            {secondaryLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                target={link.href.startsWith('http') ? '_blank' : undefined}
                rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                className="text-sm text-foreground-light hover:text-foreground hover:underline"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Social links */}
        <div className="flex items-center gap-4">
          {socialLinks.map((link) => (
            <a
              key={link.platform}
              href={link.href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground-light hover:text-foreground"
              aria-label={link.platform}
            >
              <SocialIcon platform={link.platform} />
              <span className="sr-only">{link.platform}</span>
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}

function FooterIcon({ icon }: { icon?: string }) {
  const icons: Record<string, React.ReactNode> = {
    'life-buoy': (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-foreground-light">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="4"/>
        <line x1="4.93" x2="9.17" y1="4.93" y2="9.17"/>
        <line x1="14.83" x2="19.07" y1="14.83" y2="19.07"/>
        <line x1="14.83" x2="19.07" y1="9.17" y2="4.93"/>
        <line x1="4.93" x2="9.17" y1="19.07" y2="14.83"/>
      </svg>
    ),
    newspaper: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-foreground-light">
        <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
        <path d="M18 14h-8"/>
        <path d="M15 18h-5"/>
        <path d="M10 6h8v4h-8V6Z"/>
      </svg>
    ),
  };

  return icons[icon || ''] || null;
}

function SocialIcon({ platform }: { platform: string }) {
  const icons: Record<string, React.ReactNode> = {
    twitter: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    ),
    github: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
        <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.87 8.17 6.84 9.5.5.08.66-.23.66-.5v-1.69c-2.77.6-3.36-1.34-3.36-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.87 1.52 2.34 1.07 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.92 0-1.11.38-2 1.03-2.71-.1-.25-.45-1.29.1-2.64 0 0 .84-.27 2.75 1.02.79-.22 1.65-.33 2.5-.33.85 0 1.71.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.35.2 2.39.1 2.64.65.71 1.03 1.6 1.03 2.71 0 3.82-2.34 4.66-4.57 4.91.36.31.69.92.69 1.85V21c0 .27.16.59.67.5C19.14 20.16 22 16.42 22 12A10 10 0 0012 2z"/>
      </svg>
    ),
    discord: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
      </svg>
    ),
    youtube: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
        <path fillRule="evenodd" clipRule="evenodd" d="M19.812 5.418c.861.23 1.538.907 1.768 1.768C21.998 8.746 22 12 22 12s0 3.255-.418 4.814a2.504 2.504 0 0 1-1.768 1.768c-1.56.419-7.814.419-7.814.419s-6.255 0-7.814-.419a2.505 2.505 0 0 1-1.768-1.768C2 15.255 2 12 2 12s0-3.255.417-4.814a2.507 2.507 0 0 1 1.768-1.768C5.744 5 11.998 5 11.998 5s6.255 0 7.814.418ZM15.194 12 10 15V9l5.194 3Z"/>
      </svg>
    ),
  };

  return icons[platform] || null;
}

export default DocsFooter;

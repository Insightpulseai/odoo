'use client';

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

export interface TocHeading {
  id: string;
  text: string;
  level: 2 | 3;
}

export interface DocsTocProps {
  headings: TocHeading[];
  videoUrl?: string;
  showFeedback?: boolean;
  title?: string;
}

export function DocsToc({
  headings,
  videoUrl,
  showFeedback = false,
  title = 'On this page',
}: DocsTocProps) {
  const [activeId, setActiveId] = useState<string>('');

  // Scroll spy effect
  useEffect(() => {
    if (headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      {
        rootMargin: '-80px 0px -80% 0px',
        threshold: 0,
      }
    );

    headings.forEach((heading) => {
      const element = document.getElementById(heading.id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => {
      headings.forEach((heading) => {
        const element = document.getElementById(heading.id);
        if (element) {
          observer.unobserve(element);
        }
      });
    };
  }, [headings]);

  const scrollToHeading = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      const yOffset = -80; // Account for sticky header
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  if (headings.length === 0) {
    return null;
  }

  return (
    <div className="sticky top-20 h-[calc(100vh-80px)] overflow-y-auto py-8 pl-4">
      <div className="space-y-6">
        {/* Video preview */}
        {videoUrl && (
          <div className="mb-6">
            <VideoPreview url={videoUrl} />
          </div>
        )}

        {/* Table of contents */}
        <div className="border-l border-border pl-4">
          <h4 className="mb-3 font-mono text-xs font-medium uppercase tracking-wider text-foreground-light">
            {title}
          </h4>
          <nav>
            <ul className="space-y-2">
              {headings.map((heading) => (
                <li key={heading.id}>
                  <button
                    onClick={() => scrollToHeading(heading.id)}
                    className={cn(
                      'block w-full text-left text-sm transition-colors',
                      heading.level === 3 && 'ml-3',
                      activeId === heading.id
                        ? 'text-brand-link font-medium'
                        : 'text-foreground-light hover:text-foreground'
                    )}
                  >
                    {heading.text}
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* Feedback widget */}
        {showFeedback && (
          <div className="border-l border-border pl-4 pt-4">
            <FeedbackWidget />
          </div>
        )}

        {/* Quick links */}
        <div className="border-l border-border pl-4 pt-4">
          <QuickLinks />
        </div>
      </div>
    </div>
  );
}

interface VideoPreviewProps {
  url: string;
}

function VideoPreview({ url }: VideoPreviewProps) {
  const [expanded, setExpanded] = useState(false);

  // Extract YouTube video ID
  const videoId = url.includes('youtube.com')
    ? new URL(url).searchParams.get('v')
    : url.includes('youtu.be')
      ? url.split('/').pop()
      : null;

  if (!videoId) return null;

  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 text-sm text-foreground-light hover:text-foreground"
      >
        <VideoIcon className="h-4 w-4" />
        <span>{expanded ? 'Hide video' : 'Watch video'}</span>
        <ChevronIcon
          className={cn(
            'h-3 w-3 transition-transform',
            expanded && 'rotate-180'
          )}
        />
      </button>
      {expanded && (
        <div className="mt-3 overflow-hidden rounded-lg">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="block"
          >
            <img
              src={thumbnailUrl}
              alt="Video thumbnail"
              className="w-full"
            />
          </a>
        </div>
      )}
    </div>
  );
}

function FeedbackWidget() {
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);

  if (feedback) {
    return (
      <p className="text-sm text-foreground-light">
        Thanks for your feedback!
      </p>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-foreground-light">Was this helpful?</p>
      <div className="flex gap-2">
        <button
          onClick={() => setFeedback('negative')}
          className="inline-flex items-center gap-1.5 rounded-md border border-border px-2 py-1 text-xs text-foreground-light hover:bg-muted hover:text-foreground"
        >
          <ThumbsDownIcon className="h-3 w-3" />
          No
        </button>
        <button
          onClick={() => setFeedback('positive')}
          className="inline-flex items-center gap-1.5 rounded-md border border-border px-2 py-1 text-xs text-foreground-light hover:bg-muted hover:text-foreground"
        >
          <ThumbsUpIcon className="h-3 w-3" />
          Yes
        </button>
      </div>
    </div>
  );
}

function QuickLinks() {
  const links = [
    { label: 'Need some help?', href: '/support', icon: 'life-buoy' },
    { label: 'Changelog', href: '/changelog', icon: 'newspaper' },
    { label: 'System status', href: 'https://status.supabase.com', icon: 'activity' },
  ];

  return (
    <ul className="space-y-2">
      {links.map((link) => (
        <li key={link.href}>
          <a
            href={link.href}
            target={link.href.startsWith('http') ? '_blank' : undefined}
            rel={link.href.startsWith('http') ? 'noopener noreferrer' : undefined}
            className="flex items-center gap-2 text-sm text-foreground-light hover:text-foreground"
          >
            <QuickLinkIcon icon={link.icon} />
            {link.label}
          </a>
        </li>
      ))}
    </ul>
  );
}

function QuickLinkIcon({ icon }: { icon: string }) {
  const icons: Record<string, React.ReactNode> = {
    'life-buoy': (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="4"/>
        <line x1="4.93" x2="9.17" y1="4.93" y2="9.17"/>
        <line x1="14.83" x2="19.07" y1="14.83" y2="19.07"/>
        <line x1="14.83" x2="19.07" y1="9.17" y2="4.93"/>
        <line x1="14.83" x2="18.36" y1="9.17" y2="5.64"/>
        <line x1="4.93" x2="9.17" y1="19.07" y2="14.83"/>
      </svg>
    ),
    newspaper: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
        <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
        <path d="M18 14h-8"/>
        <path d="M15 18h-5"/>
        <path d="M10 6h8v4h-8V6Z"/>
      </svg>
    ),
    activity: (
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
      </svg>
    ),
  };

  return icons[icon] || null;
}

function VideoIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m22 8-6 4 6 4V8Z"/>
      <rect width="14" height="12" x="2" y="6" rx="2" ry="2"/>
    </svg>
  );
}

function ChevronIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m6 9 6 6 6-6"/>
    </svg>
  );
}

function ThumbsUpIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M7 10v12"/>
      <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/>
    </svg>
  );
}

function ThumbsDownIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M17 14V2"/>
      <path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22h0a3.13 3.13 0 0 1-3-3.88Z"/>
    </svg>
  );
}

export default DocsToc;

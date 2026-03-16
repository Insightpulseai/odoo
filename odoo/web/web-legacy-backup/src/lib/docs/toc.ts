/**
 * Table of Contents utilities for documentation pages
 * Extracts headings from content and provides scroll-spy functionality
 */

export interface TocHeading {
  id: string;
  text: string;
  level: 2 | 3;
}

/**
 * Extract headings from HTML content
 * @param content - HTML string to extract headings from
 * @returns Array of heading objects
 */
export function extractHeadingsFromHtml(content: string): TocHeading[] {
  const headings: TocHeading[] = [];
  const headingRegex = /<h([23])[^>]*id="([^"]*)"[^>]*>([^<]*)</g;

  let match;
  while ((match = headingRegex.exec(content)) !== null) {
    headings.push({
      level: parseInt(match[1], 10) as 2 | 3,
      id: match[2],
      text: match[3].trim(),
    });
  }

  return headings;
}

/**
 * Extract headings from MDX content (server-side)
 * @param content - MDX/Markdown string
 * @returns Array of heading objects
 */
export function extractHeadingsFromMdx(content: string): TocHeading[] {
  const headings: TocHeading[] = [];
  const lines = content.split('\n');

  for (const line of lines) {
    // Match ## and ### headings
    const match = line.match(/^(#{2,3})\s+(.+)$/);
    if (match) {
      const level = match[1].length as 2 | 3;
      const text = match[2].trim();
      // Generate slug from heading text
      const id = slugify(text);

      headings.push({ id, text, level });
    }
  }

  return headings;
}

/**
 * Extract headings from DOM elements (client-side)
 * @param container - DOM element containing the content
 * @returns Array of heading objects
 */
export function extractHeadingsFromDom(
  container: HTMLElement
): TocHeading[] {
  const headings: TocHeading[] = [];
  const elements = container.querySelectorAll('h2, h3');

  elements.forEach((el) => {
    const level = parseInt(el.tagName[1], 10) as 2 | 3;
    const id = el.id || slugify(el.textContent || '');
    const text = el.textContent?.trim() || '';

    if (id && text) {
      headings.push({ id, text, level });
    }
  });

  return headings;
}

/**
 * Generate a URL-friendly slug from text
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .trim();
}

/**
 * Scroll to a heading with offset for sticky header
 */
export function scrollToHeading(
  id: string,
  offset: number = 80
): void {
  const element = document.getElementById(id);
  if (element) {
    const y =
      element.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({ top: y, behavior: 'smooth' });
  }
}

/**
 * Create an intersection observer for scroll-spy functionality
 */
export function createScrollSpyObserver(
  headingIds: string[],
  onActiveChange: (activeId: string) => void,
  options: {
    rootMargin?: string;
    threshold?: number;
  } = {}
): IntersectionObserver {
  const {
    rootMargin = '-80px 0px -80% 0px',
    threshold = 0,
  } = options;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          onActiveChange(entry.target.id);
        }
      });
    },
    { rootMargin, threshold }
  );

  // Observe all heading elements
  headingIds.forEach((id) => {
    const element = document.getElementById(id);
    if (element) {
      observer.observe(element);
    }
  });

  return observer;
}

/**
 * React hook for scroll-spy functionality
 * Usage: const activeId = useTocScrollSpy(headings);
 */
export function useTocScrollSpyInit(
  headings: TocHeading[],
  setActiveId: (id: string) => void
): () => void {
  const headingIds = headings.map((h) => h.id);
  const observer = createScrollSpyObserver(headingIds, setActiveId);

  return () => {
    observer.disconnect();
  };
}

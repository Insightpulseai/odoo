/**
 * Navigation utilities for documentation site
 * Loads and processes nav_schema.json for sidebar and header navigation
 */

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
  basePath?: string;
  items: NavItem[];
}

export interface GlobalNavItem {
  id: string;
  title: string;
  href: string;
}

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

export interface NavSchema {
  version: string;
  lastUpdated: string;
  globalNav: {
    items: GlobalNavItem[];
  };
  sections: NavSection[];
  footer: {
    primaryLinks: FooterLink[];
    secondaryLinks: FooterLink[];
    socialLinks: SocialLink[];
    copyright: string;
  };
}

/**
 * Find the active section based on the current path
 */
export function findActiveSection(
  sections: NavSection[],
  pathname: string
): NavSection | undefined {
  return sections.find((section) => {
    if (section.basePath && pathname.startsWith(section.basePath)) {
      return true;
    }
    return section.items.some(
      (item) =>
        pathname === item.href ||
        pathname.startsWith(item.href + '/') ||
        item.children?.some((child) => pathname === child.href)
    );
  });
}

/**
 * Find the active item based on the current path
 */
export function findActiveItem(
  items: NavItem[],
  pathname: string
): NavItem | undefined {
  for (const item of items) {
    if (pathname === item.href) {
      return item;
    }
    if (item.children) {
      const activeChild = item.children.find(
        (child) => pathname === child.href
      );
      if (activeChild) {
        return activeChild;
      }
    }
  }
  return undefined;
}

/**
 * Build breadcrumbs from the current path
 */
export function buildBreadcrumbs(
  sections: NavSection[],
  pathname: string
): Array<{ title: string; href?: string }> {
  const breadcrumbs: Array<{ title: string; href?: string }> = [];

  const activeSection = findActiveSection(sections, pathname);
  if (!activeSection) {
    return breadcrumbs;
  }

  breadcrumbs.push({
    title: activeSection.title,
    href: activeSection.basePath || activeSection.items[0]?.href,
  });

  for (const item of activeSection.items) {
    if (pathname === item.href) {
      breadcrumbs.push({ title: item.title });
      break;
    }
    if (item.children) {
      for (const child of item.children) {
        if (pathname === child.href) {
          breadcrumbs.push({ title: item.title, href: item.href });
          breadcrumbs.push({ title: child.title });
          break;
        }
      }
    }
  }

  return breadcrumbs;
}

/**
 * Get all navigation items flattened (for search indexing)
 */
export function flattenNavItems(sections: NavSection[]): NavItem[] {
  const items: NavItem[] = [];

  for (const section of sections) {
    for (const item of section.items) {
      items.push(item);
      if (item.children) {
        items.push(...item.children);
      }
    }
  }

  return items;
}

/**
 * Generate edit URL for a documentation page
 */
export function generateEditUrl(
  pathname: string,
  options: {
    org?: string;
    repo?: string;
    branch?: string;
    contentPath?: string;
  } = {}
): string {
  const {
    org = 'supabase',
    repo = 'supabase',
    branch = 'master',
    contentPath = 'apps/docs/content',
  } = options;

  // Remove leading /docs from pathname
  const cleanPath = pathname.replace(/^\/docs/, '');

  return `https://github.com/${org}/${repo}/edit/${branch}/${contentPath}${cleanPath}.mdx`;
}

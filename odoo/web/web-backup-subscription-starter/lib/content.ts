import fs from 'node:fs';
import path from 'node:path';
import yaml from 'yaml';

/**
 * Load and parse a YAML content file
 */
export function loadContent<T>(relativePath: string): T {
  const fullPath = path.join(process.cwd(), 'content', relativePath);
  const raw = fs.readFileSync(fullPath, 'utf8');
  return yaml.parse(raw) as T;
}

/**
 * Type definitions for solution page content
 */
export interface SolutionContent {
  slug: string;
  title: string;
  subtitle: string;
  kicker?: string;
  primaryCta?: { label: string; href: string };
  secondaryCta?: { label: string; href: string };
  hero?: {
    backgroundImage?: string;
    heroImages?: Array<{
      src: string;
      alt: string;
      width?: number;
      height?: number;
    }>;
  };
  customerLogos?: Array<{ name: string; src: string }>;
  pillars?: Array<{
    id?: string;
    title: string;
    description?: string;
    icon: string;
    points: string[];
  }>;
  deploymentOptions?: {
    title?: string;
    items: Array<{
      id: string;
      title: string;
      description: string;
      icon: string;
    }>;
  };
  useCases?: Array<{
    id?: string;
    title: string;
    description: string;
    image?: string;
    steps?: string[];
    artifacts?: Array<{
      label: string;
      meta?: string;
      href?: string;
    }>;
  }>;
  resources?: Array<{
    type: 'guide' | 'blog' | 'brief' | 'case-study';
    title: string;
    description?: string;
    href: string;
    thumb?: string;
  }>;
  partners?: {
    title?: string;
    items: Array<{
      name: string;
      src: string;
      href?: string;
    }>;
  };
  finalCta?: {
    title: string;
    subtitle?: string;
    primaryCta?: { label: string; href: string };
    secondaryCta?: { label: string; href: string };
  };
  seo?: {
    title?: string;
    description?: string;
    ogImage?: string;
    keywords?: string[];
  };
  analytics?: {
    enable: boolean;
    providers?: Array<{
      id: string;
      name: string;
      trackingIdEnv?: string;
      domainEnv?: string;
    }>;
  };
  chatWidget?: {
    enable: boolean;
    provider: string;
    widgetKeyEnv: string;
  };
}

/**
 * Load a solution page content file
 */
export function loadSolution(slug: string): SolutionContent {
  return loadContent<SolutionContent>(`solutions/${slug}.yaml`);
}

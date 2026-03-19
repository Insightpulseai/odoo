import type { ScreenProposal } from '@repo/fluent-designer-contract';

export function buildHeroProposal(): ScreenProposal {
  return {
    pageType: 'hero-landing',
    hierarchy: ['Hero Section', 'Value Propositions', 'CTA Section'],
    sections: [
      {
        id: 'hero',
        title: 'Hero Section',
        purpose: 'Primary message and visual',
        components: [
          { slot: 'hero', fluentComponent: 'Display + Subtitle1 + Button (primary)', rationale: 'Microsoft-native hero with clear CTA' },
        ],
      },
      {
        id: 'values',
        title: 'Value Propositions',
        purpose: 'Feature highlights',
        components: [
          { slot: 'values', fluentComponent: 'Card + bundleIcon + Text', rationale: 'Feature cards with icons and descriptions' },
        ],
      },
    ],
    accessibilityNotes: ['Hero image must have alt text', 'CTA buttons must be descriptive'],
    tokenGuidance: ['Restrained animation on hero', 'Use colorBrandBackground for primary CTA'],
  };
}

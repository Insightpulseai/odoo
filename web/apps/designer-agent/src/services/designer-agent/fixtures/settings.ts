import type { ScreenProposal } from '@repo/fluent-designer-contract';

export function buildSettingsProposal(): ScreenProposal {
  return {
    pageType: 'settings',
    hierarchy: ['Page Header', 'Navigation Tabs', 'Settings Groups', 'Save Actions'],
    sections: [
      {
        id: 'header',
        title: 'Settings Header',
        purpose: 'Page title and breadcrumb',
        components: [
          { slot: 'header', fluentComponent: 'Breadcrumb + Title2', rationale: 'Standard settings page orientation' },
        ],
      },
      {
        id: 'nav',
        title: 'Settings Navigation',
        purpose: 'Category selection',
        components: [
          { slot: 'nav', fluentComponent: 'TabList (vertical)', rationale: 'Category tabs for settings groups' },
        ],
      },
      {
        id: 'form',
        title: 'Settings Form',
        purpose: 'Configuration inputs',
        components: [
          { slot: 'form', fluentComponent: 'Field + Input + Switch + Dropdown', rationale: 'Standard form controls for settings' },
        ],
      },
    ],
    accessibilityNotes: ['Form labels for all inputs', 'Keyboard-navigable tab list'],
    tokenGuidance: ['Use spacingVerticalM between form fields'],
  };
}

import type { ScreenProposal } from '@repo/fluent-designer-contract';

export function buildAdminListDetailProposal(): ScreenProposal {
  return {
    pageType: 'admin-list-detail',
    hierarchy: ['Command Bar', 'List View', 'Detail Panel'],
    sections: [
      {
        id: 'command',
        title: 'Command Bar',
        purpose: 'Primary actions and search',
        components: [
          { slot: 'command', fluentComponent: 'Toolbar + SearchBox + Button + MenuButton', rationale: 'Standard admin command surface' },
        ],
      },
      {
        id: 'list',
        title: 'List View',
        purpose: 'Record listing with selection',
        components: [
          { slot: 'list', fluentComponent: 'DataGrid + DataGridSelectionCell', rationale: 'Enterprise list with selection support' },
        ],
      },
      {
        id: 'detail',
        title: 'Detail Panel',
        purpose: 'Selected record detail',
        components: [
          { slot: 'detail', fluentComponent: 'DrawerBody + Field + Text + Badge', rationale: 'Side panel for record inspection' },
        ],
      },
    ],
    accessibilityNotes: ['List selection announced to screen readers', 'Detail panel focus trap'],
    tokenGuidance: ['List density: compact for admin workflows'],
  };
}

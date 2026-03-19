import type { ScreenProposal } from '@repo/fluent-designer-contract';

export function buildDashboardProposal(): ScreenProposal {
  return {
    pageType: 'dashboard',
    hierarchy: ['Page Header', 'Filters', 'KPI Row', 'Chart Area', 'Detail Table'],
    sections: [
      {
        id: 'header',
        title: 'Header',
        purpose: 'Primary page orientation and actions',
        components: [
          {
            slot: 'header',
            fluentComponent: 'Title1 + Toolbar + Button',
            rationale: 'Matches enterprise dashboard page shell',
          },
        ],
      },
      {
        id: 'filters',
        title: 'Filter Bar',
        purpose: 'Data scope selection',
        components: [
          {
            slot: 'filters',
            fluentComponent: 'Toolbar + Dropdown + DatePicker',
            rationale: 'Standard filter bar pattern for data views',
          },
        ],
      },
      {
        id: 'kpi-row',
        title: 'KPI Summary',
        purpose: 'At-a-glance metrics',
        components: [
          {
            slot: 'kpi',
            fluentComponent: 'Card + Text + Badge',
            rationale: 'KPI cards with status badges for quick scanning',
          },
        ],
      },
      {
        id: 'charts',
        title: 'Chart Area',
        purpose: 'Visual data representation',
        components: [
          {
            slot: 'charts',
            fluentComponent: 'Card (container) + external chart library',
            rationale: 'Fluent Card as container; chart rendering is domain-specific',
          },
        ],
      },
      {
        id: 'detail-table',
        title: 'Detail Table',
        purpose: 'Tabular drill-down data',
        components: [
          {
            slot: 'table',
            fluentComponent: 'DataGrid + DataGridHeader + DataGridRow',
            rationale: 'Fluent DataGrid for enterprise-grade tabular data',
          },
        ],
      },
    ],
    accessibilityNotes: [
      'Visible focus states on all interactive elements',
      'Semantic headings (h1 for page title, h2 for sections)',
      'Descriptive action labels (not just icons)',
      'Data table must support keyboard navigation',
    ],
    tokenGuidance: [
      'Use standard Fluent spacing tokens (spacingHorizontalM, spacingVerticalL)',
      'Keep contrast and density restrained',
      'Use colorNeutralForeground1 for primary text',
      'Use colorBrandBackground for primary actions',
    ],
  };
}

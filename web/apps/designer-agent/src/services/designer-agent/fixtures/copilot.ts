import type { ScreenProposal } from '@repo/fluent-designer-contract';

export function buildCopilotPanelProposal(): ScreenProposal {
  return {
    pageType: 'copilot-panel',
    hierarchy: ['Panel Header', 'Context Summary', 'Response Area', 'Input Area'],
    sections: [
      {
        id: 'header',
        title: 'Panel Header',
        purpose: 'Copilot identity and close action',
        components: [
          { slot: 'header', fluentComponent: 'DrawerHeader + Title3 + Button (dismiss)', rationale: 'Standard panel header' },
        ],
      },
      {
        id: 'response',
        title: 'Response Area',
        purpose: 'AI response rendering',
        components: [
          { slot: 'response', fluentComponent: 'MessageBar + Card + Text', rationale: 'Structured response with status feedback' },
        ],
      },
      {
        id: 'input',
        title: 'Input Area',
        purpose: 'User prompt entry',
        components: [
          { slot: 'input', fluentComponent: 'Textarea + Button', rationale: 'Prompt input with submit action' },
        ],
      },
    ],
    accessibilityNotes: ['Live region for response updates', 'Focus management on panel open/close'],
    tokenGuidance: ['Panel width: 360-400px', 'Use colorNeutralBackground2 for panel background'],
  };
}

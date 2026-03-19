import type { ScreenProposal } from '@repo/fluent-designer-contract';

export { buildDashboardProposal } from './dashboard';
export { buildSettingsProposal } from './settings';
export { buildCopilotPanelProposal } from './copilot';
export { buildAdminListDetailProposal } from './admin';
export { buildHeroProposal } from './hero';

import { buildDashboardProposal } from './dashboard';
import { buildSettingsProposal } from './settings';
import { buildCopilotPanelProposal } from './copilot';
import { buildAdminListDetailProposal } from './admin';
import { buildHeroProposal } from './hero';

export const proposalsByType: Record<string, () => ScreenProposal> = {
  dashboard: buildDashboardProposal,
  settings: buildSettingsProposal,
  'copilot-panel': buildCopilotPanelProposal,
  'admin-list-detail': buildAdminListDetailProposal,
  'hero-landing': buildHeroProposal,
};

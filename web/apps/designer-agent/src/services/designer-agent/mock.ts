import type {
  DesignBrief,
  DesignerAgentResponse,
  DesignerMode,
  DesignCritique,
  HandoffArtifact,
} from '@repo/fluent-designer-contract';
import { buildCodingAgentPrompt } from '@repo/fluent-designer-prompts';
import { proposalsByType, buildDashboardProposal } from './fixtures';

function inferPageType(brief: DesignBrief): string {
  const text = `${brief.title} ${brief.objective}`.toLowerCase();
  if (text.includes('dashboard') || text.includes('analytics')) return 'dashboard';
  if (text.includes('settings') || text.includes('config')) return 'settings';
  if (text.includes('copilot') || text.includes('panel') || text.includes('side')) return 'copilot-panel';
  if (text.includes('admin') || text.includes('list') || text.includes('detail')) return 'admin-list-detail';
  if (text.includes('hero') || text.includes('landing')) return 'hero-landing';
  return 'dashboard';
}

export async function executeMockDesignerAgent(
  mode: DesignerMode,
  brief: DesignBrief
): Promise<DesignerAgentResponse> {
  const pageType = inferPageType(brief);
  const buildProposal = proposalsByType[pageType] ?? buildDashboardProposal;
  const proposal = buildProposal();

  const critique: DesignCritique = {
    summary: 'Mostly aligned with Fluent-first composition.',
    items: [],
  };

  const handoff: HandoffArtifact = {
    implementationSummary:
      'Build as a Fluent UI React v9 page with a client-side provider boundary.',
    componentMap: proposal.sections.map((s) => ({
      region: s.title,
      component: s.components[0]?.fluentComponent ?? 'Unknown',
      reason: s.components[0]?.rationale ?? '',
    })),
    acceptanceCriteria: [
      'Uses Fluent UI React v9 components',
      'Preserves Microsoft-native hierarchy',
      'Passes schema validation',
      'Meets WCAG 2.1 AA',
    ],
    codingAgentPrompt: buildCodingAgentPrompt(brief, proposal),
  };

  return {
    mode,
    brief,
    proposal: mode !== 'critique' ? proposal : undefined,
    critique: mode === 'critique' ? critique : undefined,
    handoff: mode === 'handoff' ? handoff : undefined,
    rationale: ['Fluent-first composition', 'Enterprise-native restraint', 'Accessibility-first'],
    warnings: [],
  };
}

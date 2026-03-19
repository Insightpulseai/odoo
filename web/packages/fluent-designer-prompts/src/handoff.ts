import type { DesignBrief, ScreenProposal } from '@repo/fluent-designer-contract';

export function buildCodingAgentPrompt(
  brief: DesignBrief,
  proposal: ScreenProposal
): string {
  return [
    `Implement a Fluent UI React v9 screen.`,
    `Title: ${brief.title}`,
    `Objective: ${brief.objective}`,
    `Page type: ${proposal.pageType}`,
    `Hierarchy: ${proposal.hierarchy.join(' > ')}`,
    ``,
    `Sections:`,
    ...proposal.sections.map(
      (s) =>
        `- ${s.title}: ${s.components.map((c) => c.fluentComponent).join(', ')}`
    ),
    ``,
    `Use Fluent UI React v9 components only where practical.`,
    `Preserve Microsoft-native spacing, hierarchy, and accessibility.`,
    `Constraints: ${brief.constraints.join('; ')}`,
  ].join('\n');
}

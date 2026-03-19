import type { ScreenProposal } from '@repo/fluent-designer-contract';

export interface FluentRuleResult {
  ruleId: string;
  principle: 'hierarchy' | 'density' | 'component-fit' | 'a11y' | 'tone';
  severity: 'info' | 'warning' | 'error';
  issue: string;
  recommendation: string;
  autofixHint?: string;
}

export function evaluateProposalAgainstFluentRules(
  proposal: ScreenProposal
): FluentRuleResult[] {
  const issues: FluentRuleResult[] = [];

  if (proposal.hierarchy.length === 0) {
    issues.push({
      ruleId: 'missing-hierarchy',
      principle: 'hierarchy',
      severity: 'error',
      issue: 'Screen proposal has no information hierarchy.',
      recommendation: 'Define clear page-to-section heading order.',
      autofixHint: 'Add hierarchy array with at least [Page Header, Content].',
    });
  }

  if (proposal.sections.length > 8) {
    issues.push({
      ruleId: 'too-many-sections',
      principle: 'density',
      severity: 'warning',
      issue: 'Too many top-level sections may reduce signal-to-noise.',
      recommendation: 'Group related content into fewer primary regions.',
    });
  }

  if (proposal.sections.length === 0) {
    issues.push({
      ruleId: 'no-sections',
      principle: 'hierarchy',
      severity: 'error',
      issue: 'Proposal has no sections defined.',
      recommendation: 'Add at least header, content, and footer sections.',
      autofixHint: 'Generate default sections: header, content, footer.',
    });
  }

  for (const section of proposal.sections) {
    if (section.components.length === 0) {
      issues.push({
        ruleId: `empty-section-${section.id}`,
        principle: 'component-fit',
        severity: 'warning',
        issue: `Section "${section.title}" has no component recommendations.`,
        recommendation: 'Add at least one Fluent component recommendation per section.',
      });
    }
  }

  if (proposal.accessibilityNotes.length === 0) {
    issues.push({
      ruleId: 'missing-a11y-notes',
      principle: 'a11y',
      severity: 'warning',
      issue: 'No accessibility notes provided.',
      recommendation: 'Add focus management, heading semantics, and ARIA guidance.',
      autofixHint: 'Add default a11y notes: focus states, semantic headings, ARIA labels.',
    });
  }

  if (proposal.tokenGuidance.length === 0) {
    issues.push({
      ruleId: 'missing-token-guidance',
      principle: 'tone',
      severity: 'info',
      issue: 'No token guidance provided.',
      recommendation: 'Reference Fluent spacing and color tokens for consistency.',
    });
  }

  return issues;
}

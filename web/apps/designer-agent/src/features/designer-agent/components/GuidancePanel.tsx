'use client';

import * as React from 'react';
import { Text, makeStyles, tokens } from '@fluentui/react-components';
import type { DesignerAgentResponse } from '@repo/fluent-designer-contract';

const useStyles = makeStyles({
  panel: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: tokens.borderRadiusMedium,
    padding: tokens.spacingHorizontalL,
    boxShadow: tokens.shadow2,
  },
});

interface GuidancePanelProps {
  response: DesignerAgentResponse | null;
}

export function GuidancePanel({ response }: GuidancePanelProps) {
  const styles = useStyles();

  return (
    <>
      <div className={styles.panel}>
        <Text weight="semibold" size={400}>
          Fluent Guidance
        </Text>
        <Text size={200}>
          Prefer calm hierarchy, explicit actions, accessible focus, and
          restrained density. Use Fluent tokens for spacing and color.
        </Text>
      </div>
      {response?.proposal && (
        <div className={styles.panel}>
          <Text weight="semibold" size={400}>
            Components
          </Text>
          {response.proposal.sections.map((s) => (
            <div key={s.id}>
              <Text weight="semibold" size={200}>
                {s.title}
              </Text>
              {s.components.map((c, i) => (
                <Text key={i} size={200} block>
                  {c.fluentComponent} — {c.rationale}
                </Text>
              ))}
            </div>
          ))}
        </div>
      )}
      {response?.proposal && (
        <div className={styles.panel}>
          <Text weight="semibold" size={400}>
            Accessibility
          </Text>
          {response.proposal.accessibilityNotes.map((n, i) => (
            <Text key={i} size={200} block>
              • {n}
            </Text>
          ))}
        </div>
      )}
    </>
  );
}

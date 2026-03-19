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
  response: {
    maxHeight: '60vh',
    overflowY: 'auto' as const,
  },
  bottomPane: {
    gridColumn: '1 / -1',
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: tokens.borderRadiusMedium,
    padding: tokens.spacingHorizontalL,
    boxShadow: tokens.shadow2,
    maxHeight: '30vh',
    overflowY: 'auto' as const,
  },
  pre: {
    fontSize: tokens.fontSizeBase200,
    fontFamily: tokens.fontFamilyMonospace,
    whiteSpace: 'pre-wrap' as const,
    wordBreak: 'break-word' as const,
  },
});

interface ResponsePaneProps {
  response: DesignerAgentResponse | null;
}

export function ResponseSummary({ response }: ResponsePaneProps) {
  const styles = useStyles();

  if (!response) return null;

  return (
    <div className={`${styles.panel} ${styles.response}`}>
      <Text weight="semibold" size={400}>
        Response — {response.mode}
      </Text>
      {response.proposal && (
        <>
          <Text size={300}>
            Page: {response.proposal.pageType} | Sections:{' '}
            {response.proposal.sections.length}
          </Text>
          <Text size={300}>
            Hierarchy: {response.proposal.hierarchy.join(' → ')}
          </Text>
        </>
      )}
      {response.rationale.length > 0 && (
        <>
          <Text weight="semibold" size={300}>
            Rationale
          </Text>
          <ul>
            {response.rationale.map((r, i) => (
              <li key={i}>
                <Text size={200}>{r}</Text>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export function ResponseJsonPane({ response }: ResponsePaneProps) {
  const styles = useStyles();

  if (!response) return null;

  return (
    <div className={styles.bottomPane}>
      <Text weight="semibold" size={400}>
        Handoff / JSON
      </Text>
      <pre className={styles.pre}>
        {JSON.stringify(response, null, 2)}
      </pre>
    </div>
  );
}

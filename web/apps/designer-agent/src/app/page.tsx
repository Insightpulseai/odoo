'use client';

import * as React from 'react';
import { makeStyles, tokens } from '@fluentui/react-components';
import type {
  DesignBrief,
  DesignerMode,
  DesignerAgentResponse,
} from '@repo/fluent-designer-contract';
import { executeMockDesignerAgent } from '@/services/designer-agent/mock';
import { ModeTabs } from '@/features/designer-agent/components/ModeTabs';
import { BriefForm } from '@/features/designer-agent/components/BriefForm';
import { ResponseSummary, ResponseJsonPane } from '@/features/designer-agent/components/ResponsePane';
import { GuidancePanel } from '@/features/designer-agent/components/GuidancePanel';

const useStyles = makeStyles({
  page: {
    display: 'grid',
    gridTemplateColumns: '240px 1fr 320px',
    gridTemplateRows: '1fr auto',
    gap: tokens.spacingHorizontalL,
    padding: tokens.spacingHorizontalL,
    minHeight: '100vh',
    backgroundColor: tokens.colorNeutralBackground2,
  },
  rail: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  center: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalL,
  },
});

export default function Page() {
  const styles = useStyles();
  const [mode, setMode] = React.useState<DesignerMode>('generate');
  const [title, setTitle] = React.useState('Campaign Performance Dashboard');
  const [objective, setObjective] = React.useState(
    'Design a Microsoft-style analytics workspace for marketing campaign performance.'
  );
  const [constraints, setConstraints] = React.useState(
    'Use Fluent components. Enterprise tone. High readability. Accessible.'
  );
  const [response, setResponse] = React.useState<DesignerAgentResponse | null>(
    null
  );
  const [loading, setLoading] = React.useState(false);

  async function run() {
    setLoading(true);
    try {
      const brief: DesignBrief = {
        title,
        objective,
        constraints: constraints
          .split('.')
          .map((s) => s.trim())
          .filter(Boolean),
        intent: {
          productType: 'analytics workspace',
          audience: 'enterprise operators',
          platform: 'web',
          tone: 'microsoft-native',
        },
        requiredRegions: ['header', 'filters', 'content', 'insights'],
      };

      const result = await executeMockDesignerAgent(mode, brief);
      setResponse(result);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      {/* Left Rail */}
      <aside className={styles.rail}>
        <ModeTabs mode={mode} onModeChange={setMode} />
      </aside>

      {/* Center Pane */}
      <main className={styles.center}>
        <BriefForm
          mode={mode}
          title={title}
          objective={objective}
          constraints={constraints}
          loading={loading}
          onTitleChange={setTitle}
          onObjectiveChange={setObjective}
          onConstraintsChange={setConstraints}
          onRun={run}
        />
        <ResponseSummary response={response} />
      </main>

      {/* Right Rail */}
      <aside className={styles.rail}>
        <GuidancePanel response={response} />
      </aside>

      {/* Bottom Pane */}
      <ResponseJsonPane response={response} />
    </div>
  );
}

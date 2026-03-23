import type { ReactNode } from 'react';
import {
  makeStyles,
  tokens,
  Text,
  Toolbar,
  ToolbarButton,
} from '@fluentui/react-components';
import {
  TargetArrowRegular,
  ChatRegular,
} from '@fluentui/react-icons';
import { useState } from 'react';
import { CopilotPanel } from '../patterns/CopilotPanel';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: tokens.colorNeutralBackground1,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: `${tokens.spacingVerticalM} ${tokens.spacingHorizontalL}`,
    borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  titleSection: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  content: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden',
  },
  main: {
    flex: 1,
    overflow: 'auto',
    padding: tokens.spacingHorizontalL,
  },
  copilotOpen: {
    flex: '0 0 380px',
  },
});

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const styles = useStyles();
  const [copilotOpen, setCopilotOpen] = useState(false);

  return (
    <div className={styles.root}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <TargetArrowRegular fontSize={24} />
          <Text weight="semibold" size={500}>
            Diva Goals
          </Text>
        </div>
        <Toolbar>
          <ToolbarButton
            icon={<ChatRegular />}
            appearance={copilotOpen ? 'primary' : 'subtle'}
            onClick={() => setCopilotOpen(!copilotOpen)}
          >
            Copilot
          </ToolbarButton>
        </Toolbar>
      </div>
      <div className={styles.content}>
        <div className={styles.main}>{children}</div>
        {copilotOpen && (
          <div className={styles.copilotOpen}>
            <CopilotPanel onClose={() => setCopilotOpen(false)} />
          </div>
        )}
      </div>
    </div>
  );
}

import React from 'react';
import type { ReactNode } from 'react';
import { makeStyles, tokens } from '@fluentui/react-components';

interface PreviewShellProps {
  sidebar?: ReactNode;
  toolbar?: ReactNode;
  preview: ReactNode;
  diagnostics?: ReactNode;
  diagnosticsOpen?: boolean;
  className?: string;
}

const useStyles = makeStyles({
  root: {
    minHeight: '100vh',
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    display: 'grid',
    gridTemplateRows: 'auto 1fr',
  },
  toolbar: {
    gridColumn: '1 / -1',
  },
  sidebar: {
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    overflowY: 'auto',
  },
  main: {
    overflow: 'hidden',
    position: 'relative',
  },
  diagnosticsWrapper: {
    overflow: 'hidden',
    transitionProperty: 'width',
    transitionDuration: tokens.durationNormal,
    transitionTimingFunction: tokens.curveEasyEase,
  },
  diagnosticsInner: {
    width: '320px',
    height: '100%',
  },
});

export function PreviewShell({
  sidebar,
  toolbar,
  preview,
  diagnostics,
  diagnosticsOpen = false,
  className,
}: PreviewShellProps) {
  const styles = useStyles();

  const gridTemplateColumns = sidebar
    ? `auto 1fr ${diagnosticsOpen ? '320px' : '0px'}`
    : `1fr ${diagnosticsOpen ? '320px' : '0px'}`;

  return (
    <div
      className={`${styles.root} ${className ?? ''}`}
      style={{ gridTemplateColumns }}
    >
      {toolbar && (
        <div className={styles.toolbar}>{toolbar}</div>
      )}

      {sidebar && (
        <aside className={styles.sidebar}>{sidebar}</aside>
      )}

      <main className={styles.main}>{preview}</main>

      <div
        className={styles.diagnosticsWrapper}
        style={{ width: diagnosticsOpen ? '320px' : '0px' }}
        aria-hidden={!diagnosticsOpen}
      >
        {diagnostics && (
          <div className={styles.diagnosticsInner}>{diagnostics}</div>
        )}
      </div>
    </div>
  );
}

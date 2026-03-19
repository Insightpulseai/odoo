import React, { useState } from 'react';
import {
  makeStyles,
  tokens,
  Text,
  Button,
  Badge,
  Divider,
  mergeClasses,
} from '@fluentui/react-components';
import {
  ErrorCircleRegular,
  WarningRegular,
  InfoRegular,
  ChevronDownRegular,
  DeleteRegular,
} from '@fluentui/react-icons';
import type { DiagnosticEntry } from './console-bridge';

interface DiagnosticsPanelProps {
  entries: DiagnosticEntry[];
  onClear: () => void;
  className?: string;
}

const useStyles = makeStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: tokens.colorNeutralBackground1,
    borderLeft: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingLeft: tokens.spacingHorizontalM,
    paddingRight: tokens.spacingHorizontalS,
    paddingTop: tokens.spacingVerticalS,
    paddingBottom: tokens.spacingVerticalS,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    flexShrink: 0,
  },
  headerLeft: {
    display: 'flex',
    alignItems: 'center',
    columnGap: tokens.spacingHorizontalS,
  },
  list: {
    flex: 1,
    overflowY: 'auto',
    padding: tokens.spacingHorizontalS,
    display: 'flex',
    flexDirection: 'column',
    rowGap: tokens.spacingVerticalXS,
  },
  empty: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    color: tokens.colorNeutralForeground4,
  },
  row: {
    display: 'flex',
    flexDirection: 'column',
    borderRadius: tokens.borderRadiusMedium,
    padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  rowError: {
    backgroundColor: tokens.colorPaletteRedBackground1,
    borderColor: tokens.colorPaletteRedBorder1,
  },
  rowWarn: {
    backgroundColor: tokens.colorPaletteYellowBackground1,
    borderColor: tokens.colorPaletteYellowBorder1,
  },
  rowInfo: {
    backgroundColor: tokens.colorNeutralBackground2,
  },
  rowTop: {
    display: 'flex',
    alignItems: 'flex-start',
    columnGap: tokens.spacingHorizontalS,
  },
  rowContent: {
    minWidth: 0,
    flex: 1,
  },
  message: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
    lineHeight: tokens.lineHeightBase200,
    wordBreak: 'break-word',
  },
  meta: {
    display: 'flex',
    alignItems: 'center',
    columnGap: tokens.spacingHorizontalS,
    marginTop: tokens.spacingVerticalXXS,
    fontSize: tokens.fontSizeBase100,
    color: tokens.colorNeutralForeground4,
  },
  chevron: {
    cursor: 'pointer',
    flexShrink: 0,
    transition: 'transform 150ms',
  },
  chevronOpen: {
    transform: 'rotate(180deg)',
  },
  stack: {
    marginTop: tokens.spacingVerticalS,
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase100,
    lineHeight: tokens.lineHeightBase200,
    color: tokens.colorNeutralForeground3,
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    backgroundColor: tokens.colorNeutralBackground3,
    borderRadius: tokens.borderRadiusSmall,
    padding: tokens.spacingHorizontalS,
    maxHeight: '192px',
    overflowY: 'auto',
  },
  iconError: { color: tokens.colorPaletteRedForeground1 },
  iconWarn: { color: tokens.colorPaletteYellowForeground1 },
  iconInfo: { color: tokens.colorNeutralForeground3 },
});

function formatRelativeTime(timestamp: number): string {
  const delta = Date.now() - timestamp;
  if (delta < 1000) return 'just now';
  if (delta < 60_000) return `${Math.floor(delta / 1000)}s ago`;
  if (delta < 3_600_000) return `${Math.floor(delta / 60_000)}m ago`;
  return `${Math.floor(delta / 3_600_000)}h ago`;
}

function DiagnosticRow({ entry }: { entry: DiagnosticEntry }) {
  const [expanded, setExpanded] = useState(false);
  const styles = useStyles();

  const severityStyles = {
    error: styles.rowError,
    warn: styles.rowWarn,
    info: styles.rowInfo,
  };

  const severityIcons = {
    error: <ErrorCircleRegular className={styles.iconError} fontSize={16} />,
    warn: <WarningRegular className={styles.iconWarn} fontSize={16} />,
    info: <InfoRegular className={styles.iconInfo} fontSize={16} />,
  };

  return (
    <div className={mergeClasses(styles.row, severityStyles[entry.severity])}>
      <div className={styles.rowTop}>
        {severityIcons[entry.severity]}
        <div className={styles.rowContent}>
          <Text className={styles.message}>{entry.message}</Text>
          <div className={styles.meta}>
            <span>{formatRelativeTime(entry.timestamp)}</span>
            <span>|</span>
            <span>{entry.source}</span>
            {entry.route && (
              <>
                <span>|</span>
                <span>{entry.route}</span>
              </>
            )}
          </div>
        </div>
        {entry.stack && (
          <ChevronDownRegular
            className={mergeClasses(styles.chevron, expanded && styles.chevronOpen)}
            fontSize={16}
            onClick={() => setExpanded((prev) => !prev)}
          />
        )}
      </div>
      {expanded && entry.stack && (
        <pre className={styles.stack}>{entry.stack}</pre>
      )}
    </div>
  );
}

export function DiagnosticsPanel({
  entries,
  onClear,
  className,
}: DiagnosticsPanelProps) {
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  const styles = useStyles();
  const errorCount = entries.filter((e) => e.severity === 'error').length;
  const warnCount = entries.filter((e) => e.severity === 'warn').length;

  return (
    <div
      className={mergeClasses(styles.root, className)}
      role="log"
      aria-label="Diagnostics panel"
    >
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <Text weight="semibold" size={200}>Diagnostics</Text>
          <Text size={100} style={{ color: tokens.colorNeutralForeground4 }}>
            {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
          </Text>
          {errorCount > 0 && (
            <Badge appearance="filled" color="danger" size="small">
              {errorCount} error{errorCount !== 1 ? 's' : ''}
            </Badge>
          )}
          {warnCount > 0 && (
            <Badge appearance="filled" color="warning" size="small">
              {warnCount} warn{warnCount !== 1 ? 's' : ''}
            </Badge>
          )}
        </div>
        <Button
          icon={<DeleteRegular />}
          appearance="subtle"
          size="small"
          onClick={onClear}
          aria-label="Clear diagnostics"
        >
          Clear
        </Button>
      </div>

      <div className={styles.list}>
        {entries.length === 0 ? (
          <div className={styles.empty}>
            <Text size={200}>No diagnostics captured</Text>
          </div>
        ) : (
          entries.map((entry) => (
            <DiagnosticRow key={entry.id} entry={entry} />
          ))
        )}
      </div>
    </div>
  );
}

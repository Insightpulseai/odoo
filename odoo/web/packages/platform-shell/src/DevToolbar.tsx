import React from 'react';
import {
  makeStyles,
  tokens,
  Badge,
  Button,
  Toolbar,
  ToolbarButton,
  Tooltip,
  Text,
  mergeClasses,
} from '@fluentui/react-components';
import {
  PulseRegular,
  DeleteRegular,
  ErrorCircleRegular,
} from '@fluentui/react-icons';

interface DevToolbarProps {
  environment: string;
  diagnosticCount: number;
  onToggleDiagnostics: () => void;
  onClearDiagnostics: () => void;
  buildSha?: string;
  className?: string;
}

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '32px',
    paddingLeft: tokens.spacingHorizontalS,
    paddingRight: tokens.spacingHorizontalS,
    backgroundColor: tokens.colorNeutralBackground1,
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    userSelect: 'none',
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    columnGap: tokens.spacingHorizontalS,
  },
  right: {
    display: 'flex',
    alignItems: 'center',
  },
  sha: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase100,
    color: tokens.colorNeutralForeground4,
  },
});

const ENV_COLORS: Record<string, 'success' | 'warning' | 'danger' | 'informative'> = {
  dev: 'success',
  development: 'success',
  staging: 'warning',
  production: 'danger',
};

export function DevToolbar({
  environment,
  diagnosticCount,
  onToggleDiagnostics,
  onClearDiagnostics,
  buildSha,
  className,
}: DevToolbarProps) {
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  const styles = useStyles();
  const envColor = ENV_COLORS[environment.toLowerCase()] ?? 'informative';
  const truncatedSha = buildSha ? buildSha.slice(0, 7) : undefined;

  return (
    <div
      className={mergeClasses(styles.root, className)}
      role="toolbar"
      aria-label="Developer toolbar"
    >
      <div className={styles.left}>
        <PulseRegular fontSize={14} />
        <Badge appearance="filled" color={envColor} size="small">
          {environment}
        </Badge>
        {truncatedSha && (
          <Tooltip content={buildSha!} relationship="description">
            <Text className={styles.sha}>{truncatedSha}</Text>
          </Tooltip>
        )}
      </div>

      <Toolbar size="small" className={styles.right}>
        <Tooltip content={`${diagnosticCount} diagnostics`} relationship="label">
          <ToolbarButton
            icon={<ErrorCircleRegular />}
            onClick={onToggleDiagnostics}
            aria-label={`Toggle diagnostics panel, ${diagnosticCount} entries`}
          >
            {diagnosticCount > 0 && (
              <Badge appearance="filled" color="danger" size="tiny">
                {diagnosticCount > 99 ? '99+' : diagnosticCount}
              </Badge>
            )}
          </ToolbarButton>
        </Tooltip>
        <Tooltip content="Clear diagnostics" relationship="label">
          <ToolbarButton
            icon={<DeleteRegular />}
            onClick={onClearDiagnostics}
            aria-label="Clear diagnostics"
          />
        </Tooltip>
      </Toolbar>
    </div>
  );
}

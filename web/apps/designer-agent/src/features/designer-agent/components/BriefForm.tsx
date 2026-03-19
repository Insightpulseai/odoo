'use client';

import * as React from 'react';
import {
  Button,
  Field,
  Input,
  Text,
  Textarea,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import type { DesignerMode } from '@repo/fluent-designer-contract';

const useStyles = makeStyles({
  panel: {
    backgroundColor: tokens.colorNeutralBackground1,
    borderRadius: tokens.borderRadiusMedium,
    padding: tokens.spacingHorizontalL,
    boxShadow: tokens.shadow2,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
});

interface BriefFormProps {
  mode: DesignerMode;
  title: string;
  objective: string;
  constraints: string;
  loading: boolean;
  onTitleChange: (value: string) => void;
  onObjectiveChange: (value: string) => void;
  onConstraintsChange: (value: string) => void;
  onRun: () => void;
}

export function BriefForm({
  mode,
  title,
  objective,
  constraints,
  loading,
  onTitleChange,
  onObjectiveChange,
  onConstraintsChange,
  onRun,
}: BriefFormProps) {
  const styles = useStyles();

  return (
    <div className={styles.panel}>
      <div className={styles.form}>
        <Text weight="semibold" size={500}>
          Design Brief
        </Text>
        <Field label="Title">
          <Input value={title} onChange={(_, d) => onTitleChange(d.value)} />
        </Field>
        <Field label="Objective">
          <Input
            value={objective}
            onChange={(_, d) => onObjectiveChange(d.value)}
          />
        </Field>
        <Field label="Constraints (period-separated)">
          <Textarea
            value={constraints}
            onChange={(_, d) => onConstraintsChange(d.value)}
            rows={3}
          />
        </Field>
        <Button appearance="primary" onClick={onRun} disabled={loading}>
          {loading ? 'Running...' : `Run ${mode}`}
        </Button>
      </div>
    </div>
  );
}

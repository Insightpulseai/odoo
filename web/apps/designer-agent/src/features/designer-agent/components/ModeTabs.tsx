'use client';

import * as React from 'react';
import {
  Tab,
  TabList,
  Text,
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
});

interface ModeTabsProps {
  mode: DesignerMode;
  onModeChange: (mode: DesignerMode) => void;
}

export function ModeTabs({ mode, onModeChange }: ModeTabsProps) {
  const styles = useStyles();

  return (
    <div className={styles.panel}>
      <Text weight="semibold" size={400}>
        Modes
      </Text>
      <TabList
        selectedValue={mode}
        onTabSelect={(_, data) => onModeChange(data.value as DesignerMode)}
        vertical
      >
        <Tab value="generate">Generate</Tab>
        <Tab value="critique">Critique</Tab>
        <Tab value="refine">Refine</Tab>
        <Tab value="handoff">Handoff</Tab>
      </TabList>
    </div>
  );
}

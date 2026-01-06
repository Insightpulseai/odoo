"use client";

import * as React from "react";
import {
  FluentProvider,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import { tbwaTheme } from "./theme/tbwaFluentTheme";

const useStyles = makeStyles({
  app: {
    minHeight: "100vh",
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    ...shorthands.padding(0),
    ...shorthands.margin(0),
  },
});

export default function Providers({ children }: { children: React.ReactNode }) {
  const styles = useStyles();

  return (
    <FluentProvider theme={tbwaTheme}>
      <div className={styles.app}>{children}</div>
    </FluentProvider>
  );
}

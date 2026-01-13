"use client";

import * as React from "react";
import {
  FluentProvider,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import { useTheme } from "@/hooks/useTheme";
import { getFluentTheme } from "@/theme/fluentThemes";

const useStyles = makeStyles({
  app: {
    minHeight: "100vh",
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    ...shorthands.padding(0),
    ...shorthands.margin(0),
  },
});

/**
 * Theme Context for accessing theme state in components
 */
interface ThemeContextValue {
  theme: "suqi" | "system" | "tbwa-dark";
  scheme: "light" | "dark";
  setTheme: (theme: "suqi" | "system" | "tbwa-dark") => void;
  setScheme: (scheme: "light" | "dark") => void;
}

export const ThemeContext = React.createContext<ThemeContextValue | null>(null);

export function useThemeContext() {
  const ctx = React.useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useThemeContext must be used within Providers");
  }
  return ctx;
}

/**
 * Root providers component
 * Wraps the app with FluentProvider and theme context
 */
export default function Providers({ children }: { children: React.ReactNode }) {
  const [theme, scheme, setTheme, setScheme] = useTheme();
  const styles = useStyles();

  // Get the appropriate Fluent theme based on current UI theme and scheme
  const fluentTheme = React.useMemo(
    () => getFluentTheme(theme, scheme),
    [theme, scheme]
  );

  // Context value for child components
  const themeContextValue = React.useMemo<ThemeContextValue>(
    () => ({
      theme,
      scheme,
      setTheme,
      setScheme,
    }),
    [theme, scheme, setTheme, setScheme]
  );

  return (
    <ThemeContext.Provider value={themeContextValue}>
      <FluentProvider theme={fluentTheme}>
        <div className={styles.app}>{children}</div>
      </FluentProvider>
    </ThemeContext.Provider>
  );
}

"use client";

import * as React from "react";
import {
  Menu,
  MenuTrigger,
  MenuList,
  MenuItem,
  MenuPopover,
  Button,
  makeStyles,
  tokens,
  Divider,
} from "@fluentui/react-components";
import {
  WeatherSunny24Regular,
  WeatherMoon24Regular,
  ColorBackground24Regular,
} from "@fluentui/react-icons";
import { useThemeContext } from "@/app/providers";

const useStyles = makeStyles({
  menuItem: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalS,
  },
  activeIndicator: {
    width: "8px",
    height: "8px",
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: tokens.colorBrandBackground,
  },
  inactiveIndicator: {
    width: "8px",
    height: "8px",
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: "transparent",
    border: `1px solid ${tokens.colorNeutralStroke1}`,
  },
  schemeSection: {
    paddingTop: tokens.spacingVerticalS,
  },
});

const themeOptions = [
  { id: "suqi", label: "Suqi (Yellow)", icon: "🌻" },
  { id: "system", label: "System (Blue)", icon: "💙" },
  { id: "tbwa-dark", label: "TBWA Dark", icon: "🌙" },
] as const;

export function ThemeSwitcher() {
  const styles = useStyles();
  const { theme, scheme, setTheme, setScheme } = useThemeContext();

  const currentTheme = themeOptions.find((t) => t.id === theme);

  return (
    <Menu>
      <MenuTrigger disableButtonEnhancement>
        <Button
          appearance="subtle"
          icon={<ColorBackground24Regular />}
          aria-label="Theme settings"
        >
          {currentTheme?.icon}
        </Button>
      </MenuTrigger>

      <MenuPopover>
        <MenuList>
          {/* Theme Family Selection */}
          {themeOptions.map((option) => (
            <MenuItem
              key={option.id}
              onClick={() => setTheme(option.id)}
            >
              <span className={styles.menuItem}>
                <span
                  className={
                    theme === option.id
                      ? styles.activeIndicator
                      : styles.inactiveIndicator
                  }
                />
                <span>{option.icon}</span>
                <span>{option.label}</span>
              </span>
            </MenuItem>
          ))}

          <Divider />

          {/* Color Scheme Selection */}
          <MenuItem
            icon={<WeatherSunny24Regular />}
            onClick={() => setScheme("light")}
          >
            <span className={styles.menuItem}>
              <span
                className={
                  scheme === "light"
                    ? styles.activeIndicator
                    : styles.inactiveIndicator
                }
              />
              Light
            </span>
          </MenuItem>

          <MenuItem
            icon={<WeatherMoon24Regular />}
            onClick={() => setScheme("dark")}
          >
            <span className={styles.menuItem}>
              <span
                className={
                  scheme === "dark"
                    ? styles.activeIndicator
                    : styles.inactiveIndicator
                }
              />
              Dark
            </span>
          </MenuItem>
        </MenuList>
      </MenuPopover>
    </Menu>
  );
}

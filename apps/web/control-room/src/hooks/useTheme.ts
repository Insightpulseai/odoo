"use client";

import { useState, useEffect, useCallback } from "react";
import type { UiTheme, Scheme } from "@/theme/fluentThemes";

const STORAGE_KEY = "ipai-ui-theme";
const SCHEME_KEY = "ipai-color-scheme";

/**
 * Theme hook that syncs with:
 * - localStorage persistence
 * - data-theme attribute on <html>
 * - CSS custom properties
 * - Odoo parent frame via postMessage
 */
export function useTheme(): [
  UiTheme,
  Scheme,
  (theme: UiTheme) => void,
  (scheme: Scheme) => void
] {
  const [theme, setThemeState] = useState<UiTheme>("suqi");
  const [scheme, setSchemeState] = useState<Scheme>("light");

  // Initialize from localStorage or system preference
  useEffect(() => {
    const storedTheme = localStorage.getItem(STORAGE_KEY) as UiTheme | null;
    const storedScheme = localStorage.getItem(SCHEME_KEY) as Scheme | null;

    if (storedTheme && ["suqi", "system", "tbwa-dark"].includes(storedTheme)) {
      setThemeState(storedTheme);
    }

    if (storedScheme && ["light", "dark"].includes(storedScheme)) {
      setSchemeState(storedScheme);
    } else if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      setSchemeState("dark");
    }

    // Listen for theme changes from Odoo parent frame
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "IPAI_THEME_CHANGE") {
        const { theme: newTheme, scheme: newScheme } = event.data;
        if (newTheme && ["suqi", "system", "tbwa-dark"].includes(newTheme)) {
          setThemeState(newTheme);
          localStorage.setItem(STORAGE_KEY, newTheme);
        }
        if (newScheme && ["light", "dark"].includes(newScheme)) {
          setSchemeState(newScheme);
          localStorage.setItem(SCHEME_KEY, newScheme);
        }
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  // Apply theme to DOM
  useEffect(() => {
    const root = document.documentElement;

    // Set data attributes
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-scheme", scheme);

    // Apply CSS classes for Tailwind dark mode
    if (scheme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }

    // Notify Odoo parent frame of theme change
    if (window.parent !== window) {
      window.parent.postMessage(
        {
          type: "IPAI_THEME_SYNC",
          theme,
          scheme,
        },
        "*"
      );
    }
  }, [theme, scheme]);

  const setTheme = useCallback((newTheme: UiTheme) => {
    setThemeState(newTheme);
    localStorage.setItem(STORAGE_KEY, newTheme);

    // Auto-set scheme based on theme
    if (newTheme === "tbwa-dark") {
      setSchemeState("dark");
      localStorage.setItem(SCHEME_KEY, "dark");
    }
  }, []);

  const setScheme = useCallback((newScheme: Scheme) => {
    setSchemeState(newScheme);
    localStorage.setItem(SCHEME_KEY, newScheme);
  }, []);

  return [theme, scheme, setTheme, setScheme];
}

/**
 * Hook to get current theme without setters (for read-only components)
 */
export function useCurrentTheme(): { theme: UiTheme; scheme: Scheme } {
  const [theme, scheme] = useTheme();
  return { theme, scheme };
}

/**
 * Odoo Brand Tokens Fetcher & Fluent Theme Mapper
 * ================================================
 *
 * This module fetches brand tokens from the Odoo API and maps them
 * to Fluent UI / App SDK theme format.
 *
 * Usage:
 * ```tsx
 * import { fetchOdooTokens, createFluentTheme } from '@ipai/design-tokens/odooTokens';
 *
 * const tokens = await fetchOdooTokens('https://erp.insightpulseai.net');
 * const theme = createFluentTheme(tokens);
 *
 * <FluentProvider theme={theme}>
 *   <App />
 * </FluentProvider>
 * ```
 */

export interface OdooTokens {
  palette: {
    primary: string;
    primaryHover: string;
    accent: string;
    accentHover: string;
    success: string;
    warning: string;
    danger: string;
    info: string;
  };
  surface: {
    bg: string;
    card: string;
    elevated: string;
    border: string;
  };
  text: {
    primary: string;
    secondary: string;
    onPrimary: string;
    onAccent: string;
  };
  radius: {
    sm: string;
    md: string;
    lg: string;
  };
  shadow: {
    sm: string;
    md: string;
    lg: string;
  };
  typography: {
    fontFamily: string;
  };
  meta: {
    preset: string;
    iconPack: string;
    companyId: number;
    companyName: string;
  };
}

// Default TBWA tokens (fallback if API unavailable)
export const defaultTokens: OdooTokens = {
  palette: {
    primary: "#000000",
    primaryHover: "#1A1A1A",
    accent: "#FBBF24",
    accentHover: "#F59E0B",
    success: "#10B981",
    warning: "#F59E0B",
    danger: "#EF4444",
    info: "#3B82F6",
  },
  surface: {
    bg: "#FFFFFF",
    card: "#F9FAFB",
    elevated: "#FFFFFF",
    border: "#E5E7EB",
  },
  text: {
    primary: "#111827",
    secondary: "#6B7280",
    onPrimary: "#FFFFFF",
    onAccent: "#000000",
  },
  radius: {
    sm: "4px",
    md: "8px",
    lg: "12px",
  },
  shadow: {
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
  },
  typography: {
    fontFamily: '"Segoe UI", system-ui, -apple-system, sans-serif',
  },
  meta: {
    preset: "tbwa",
    iconPack: "fluent",
    companyId: 0,
    companyName: "Default",
  },
};

/**
 * Fetch brand tokens from Odoo API
 */
export async function fetchOdooTokens(
  baseUrl: string,
  companyId?: number
): Promise<OdooTokens> {
  const url = new URL("/ipai/ui/tokens.json", baseUrl);
  if (companyId) {
    url.searchParams.set("company_id", String(companyId));
  }

  try {
    const response = await fetch(url.toString(), {
      headers: {
        Accept: "application/json",
      },
      // Cache for 5 minutes
      next: { revalidate: 300 },
    });

    if (!response.ok) {
      console.warn(
        `[OdooTokens] Failed to fetch tokens: ${response.status}`
      );
      return defaultTokens;
    }

    const tokens = await response.json();
    return tokens as OdooTokens;
  } catch (error) {
    console.warn("[OdooTokens] Error fetching tokens:", error);
    return defaultTokens;
  }
}

/**
 * Create Fluent UI v9 theme from Odoo tokens
 *
 * Maps Odoo brand tokens to Fluent UI theme tokens.
 * Compatible with @fluentui/react-components v9.
 */
export function createFluentTheme(tokens: OdooTokens) {
  return {
    // Brand colors
    colorBrandBackground: tokens.palette.primary,
    colorBrandBackgroundHover: tokens.palette.primaryHover,
    colorBrandBackgroundPressed: tokens.palette.primaryHover,
    colorBrandForeground1: tokens.palette.primary,
    colorBrandForeground2: tokens.palette.primaryHover,

    // Accent / highlight
    colorCompoundBrandBackground: tokens.palette.accent,
    colorCompoundBrandBackgroundHover: tokens.palette.accentHover,
    colorCompoundBrandBackgroundPressed: tokens.palette.accentHover,
    colorCompoundBrandForeground1: tokens.palette.accent,
    colorCompoundBrandForeground1Hover: tokens.palette.accentHover,
    colorCompoundBrandForeground1Pressed: tokens.palette.accentHover,

    // Neutral backgrounds
    colorNeutralBackground1: tokens.surface.bg,
    colorNeutralBackground2: tokens.surface.card,
    colorNeutralBackground3: tokens.surface.elevated,
    colorNeutralBackground4: tokens.surface.border,

    // Neutral foregrounds (text)
    colorNeutralForeground1: tokens.text.primary,
    colorNeutralForeground2: tokens.text.secondary,
    colorNeutralForeground3: tokens.text.secondary,
    colorNeutralForeground4: tokens.text.secondary,

    // Stroke/border
    colorNeutralStroke1: tokens.surface.border,
    colorNeutralStroke2: tokens.surface.border,

    // Status colors
    colorStatusSuccessBackground1: `${tokens.palette.success}15`,
    colorStatusSuccessBackground2: tokens.palette.success,
    colorStatusSuccessForeground1: tokens.palette.success,

    colorStatusWarningBackground1: `${tokens.palette.warning}15`,
    colorStatusWarningBackground2: tokens.palette.warning,
    colorStatusWarningForeground1: tokens.palette.warning,

    colorStatusDangerBackground1: `${tokens.palette.danger}15`,
    colorStatusDangerBackground2: tokens.palette.danger,
    colorStatusDangerForeground1: tokens.palette.danger,

    // Shape
    borderRadiusSmall: tokens.radius.sm,
    borderRadiusMedium: tokens.radius.md,
    borderRadiusLarge: tokens.radius.lg,
    borderRadiusXLarge: tokens.radius.lg,

    // Shadows
    shadow2: tokens.shadow.sm,
    shadow4: tokens.shadow.sm,
    shadow8: tokens.shadow.md,
    shadow16: tokens.shadow.md,
    shadow28: tokens.shadow.lg,
    shadow64: tokens.shadow.lg,

    // Typography
    fontFamilyBase: tokens.typography.fontFamily,
    fontFamilyMonospace: '"JetBrains Mono", "Fira Code", Consolas, monospace',
  };
}

/**
 * Create ChatGPT App SDK theme from Odoo tokens
 *
 * Maps Odoo brand tokens to ChatGPT App SDK theme format.
 * Use with AppSDKProvider or similar.
 */
export function createAppSDKTheme(tokens: OdooTokens) {
  return {
    colors: {
      // Primary colors
      primary: tokens.palette.primary,
      "primary-hover": tokens.palette.primaryHover,

      // Accent colors
      accent: tokens.palette.accent,
      "accent-hover": tokens.palette.accentHover,

      // Background colors
      background: tokens.surface.bg,
      surface: tokens.surface.card,
      "surface-elevated": tokens.surface.elevated,
      border: tokens.surface.border,

      // Text colors
      text: tokens.text.primary,
      "text-muted": tokens.text.secondary,
      "text-on-primary": tokens.text.onPrimary,
      "text-on-accent": tokens.text.onAccent,

      // Status colors
      success: tokens.palette.success,
      warning: tokens.palette.warning,
      danger: tokens.palette.danger,
      info: tokens.palette.info,
    },
    radius: {
      sm: tokens.radius.sm,
      md: tokens.radius.md,
      lg: tokens.radius.lg,
    },
    shadows: {
      sm: tokens.shadow.sm,
      md: tokens.shadow.md,
      lg: tokens.shadow.lg,
    },
    typography: {
      fontFamily: tokens.typography.fontFamily,
    },
  };
}

/**
 * Apply tokens as CSS custom properties to document
 *
 * Useful for non-React contexts or global styling.
 */
export function applyTokensToDocument(tokens: OdooTokens): void {
  const root = document.documentElement;

  // Palette
  root.style.setProperty("--tbwa-primary", tokens.palette.primary);
  root.style.setProperty("--tbwa-primary-hover", tokens.palette.primaryHover);
  root.style.setProperty("--tbwa-accent", tokens.palette.accent);
  root.style.setProperty("--tbwa-accent-hover", tokens.palette.accentHover);
  root.style.setProperty("--tbwa-success", tokens.palette.success);
  root.style.setProperty("--tbwa-warning", tokens.palette.warning);
  root.style.setProperty("--tbwa-danger", tokens.palette.danger);
  root.style.setProperty("--tbwa-info", tokens.palette.info);

  // Surface
  root.style.setProperty("--tbwa-bg", tokens.surface.bg);
  root.style.setProperty("--tbwa-surface", tokens.surface.card);
  root.style.setProperty("--tbwa-surface-elevated", tokens.surface.elevated);
  root.style.setProperty("--tbwa-border", tokens.surface.border);

  // Text
  root.style.setProperty("--tbwa-text-primary", tokens.text.primary);
  root.style.setProperty("--tbwa-text-secondary", tokens.text.secondary);
  root.style.setProperty("--tbwa-text-on-primary", tokens.text.onPrimary);
  root.style.setProperty("--tbwa-text-on-accent", tokens.text.onAccent);

  // Shape
  root.style.setProperty("--tbwa-radius-sm", tokens.radius.sm);
  root.style.setProperty("--tbwa-radius-md", tokens.radius.md);
  root.style.setProperty("--tbwa-radius-lg", tokens.radius.lg);

  // Shadows
  root.style.setProperty("--tbwa-shadow-sm", tokens.shadow.sm);
  root.style.setProperty("--tbwa-shadow-md", tokens.shadow.md);
  root.style.setProperty("--tbwa-shadow-lg", tokens.shadow.lg);

  // Typography
  root.style.setProperty("--tbwa-font-family", tokens.typography.fontFamily);
}

/**
 * React hook for using Odoo tokens
 *
 * ```tsx
 * const { tokens, loading, error } = useOdooTokens('https://erp.insightpulseai.net');
 * ```
 */
export function createUseOdooTokensHook(React: {
  useState: Function;
  useEffect: Function;
}) {
  return function useOdooTokens(baseUrl: string, companyId?: number) {
    const [tokens, setTokens] = React.useState<OdooTokens>(defaultTokens);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState<Error | null>(null);

    React.useEffect(() => {
      let cancelled = false;

      fetchOdooTokens(baseUrl, companyId)
        .then((t) => {
          if (!cancelled) {
            setTokens(t);
            setLoading(false);
          }
        })
        .catch((e) => {
          if (!cancelled) {
            setError(e);
            setLoading(false);
          }
        });

      return () => {
        cancelled = true;
      };
    }, [baseUrl, companyId]);

    return { tokens, loading, error };
  };
}

import type { Config } from "tailwindcss";

import typography from "@tailwindcss/typography";
import radix from "tailwindcss-radix";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    fontFamily: {
      sans: "var(--font-sans)",
      mono: "var(--font-mono)",
    },
    colors: {
      transparent: "transparent",
      white: "#fff",
      black: "#000",
      brand: {
        DEFAULT: "var(--colorBrandBackground)",
        hover: "var(--colorBrandBackgroundHover)",
        pressed: "var(--colorBrandBackgroundPressed)",
        foreground: "var(--colorBrandForeground1)",
        "foreground-2": "var(--colorBrandForeground2)",
        stroke: "var(--colorBrandStroke1)",
        subtle: "var(--colorBrandBackground2)",
      },
      neutral: {
        "bg1": "var(--colorNeutralBackground1)",
        "bg2": "var(--colorNeutralBackground2)",
        "bg3": "var(--colorNeutralBackground3)",
        "bg4": "var(--colorNeutralBackground4)",
        "bg5": "var(--colorNeutralBackground5)",
        "bg-inverted": "var(--colorNeutralBackgroundInverted)",
        "fg1": "var(--colorNeutralForeground1)",
        "fg2": "var(--colorNeutralForeground2)",
        "fg3": "var(--colorNeutralForeground3)",
        "fg4": "var(--colorNeutralForeground4)",
        "fg-on-brand": "var(--colorNeutralForegroundOnBrand)",
        "stroke1": "var(--colorNeutralStroke1)",
        "stroke2": "var(--colorNeutralStroke2)",
        "stroke-accessible": "var(--colorNeutralStrokeAccessible)",
      },
      status: {
        danger: "var(--colorStatusDangerForeground1)",
        "danger-bg": "var(--colorStatusDangerBackground1)",
        success: "var(--colorStatusSuccessForeground1)",
        "success-bg": "var(--colorStatusSuccessBackground1)",
      },
    },
    fontSize: {
      "2xs": ["10px", { lineHeight: "14px", fontWeight: "400" }],
      xs: ["12px", { lineHeight: "16px", fontWeight: "400" }],
      sm: ["14px", { lineHeight: "20px", fontWeight: "400" }],
      base: ["16px", { lineHeight: "22px", fontWeight: "600" }],
      lg: ["20px", { lineHeight: "26px", fontWeight: "600" }],
      xl: ["24px", { lineHeight: "32px", fontWeight: "600" }],
      "2xl": ["28px", { lineHeight: "36px", fontWeight: "600" }],
      "3xl": ["32px", { lineHeight: "40px", fontWeight: "600" }],
      "4xl": ["40px", { lineHeight: "52px", fontWeight: "600" }],
      "5xl": ["68px", { lineHeight: "92px", fontWeight: "600" }],
    },
    extend: {
      maxWidth: {
        prose: "75ch",
      },
      gridTemplateColumns: {
        header: "1fr max-content 1fr",
      },
      boxShadow: {
        neon: "0 0 2px 2px var(--tw-shadow), 0 0 6px 3px var(--tw-ring-offset-shadow), 0 0 8px 4px var(--tw-ring-shadow)",
      },
      zIndex: {
        modal: "9999",
      },
      keyframes: {
        enterFromRight: {
          from: { opacity: "0", transform: "translateX(200px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        enterFromLeft: {
          from: { opacity: "0", transform: "translateX(-200px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        exitToRight: {
          from: { opacity: "1", transform: "translateX(0)" },
          to: { opacity: "0", transform: "translateX(200px)" },
        },
        exitToLeft: {
          from: { opacity: "1", transform: "translateX(0)" },
          to: { opacity: "0", transform: "translateX(-200px)" },
        },
        scaleIn: {
          from: { opacity: "0", transform: "rotateX(-10deg) scale(0.9)" },
          to: { opacity: "1", transform: "rotateX(0deg) scale(1)" },
        },
        scaleOut: {
          from: { opacity: "1", transform: "rotateX(0deg) scale(1)" },
          to: { opacity: "0", transform: "rotateX(-10deg) scale(0.95)" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        fadeOut: {
          from: { opacity: "1" },
          to: { opacity: "0" },
        },
        slideDown: {
          from: { height: "0px" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        slideUp: {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0px" },
        },
        pulse: {
          "50%": {
            opacity: "0.5",
          },
        },
      },
      letterSpacing: {
        tighter: "-0.58px",
        tight: "-0.48px",
      },
      typography: {
        DEFAULT: {
          css: {
            p: {
              letterSpacing: "-0.48px",
            },
            code: {
              letterSpacing: "normal",
            },
          },
        },
      },
    },
    animation: {
      slideDown: "slideDown 300ms cubic-bezier(0.87, 0, 0.13, 1)",
      slideUp: "slideUp 300ms cubic-bezier(0.87, 0, 0.13, 1)",
      scaleIn: "scaleIn 200ms ease",
      scaleOut: "scaleOut 200ms ease",
      fadeIn: "fadeIn 200ms ease",
      fadeOut: "fadeOut 200ms ease",
      enterFromLeft: "enterFromLeft 250ms ease",
      enterFromRight: "enterFromRight 250ms ease",
      exitToLeft: "exitToLeft 250ms ease",
      exitToRight: "exitToRight 250ms ease",
      pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
    },
  },
  plugins: [typography, radix],
};

export default config;

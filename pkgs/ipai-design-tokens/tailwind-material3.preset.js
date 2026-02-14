/**
 * IPAI Design Tokens - Material 3 "Expressive" Tailwind Preset
 *
 * Production-ready Tailwind configuration for the Gemini-style M3 theme.
 * Maps CSS variables to Tailwind utilities for seamless integration.
 *
 * IMPORTANT: For Odoo integration, set prefix: 'tw-' in your tailwind.config.js
 * to avoid Bootstrap collisions.
 *
 * Usage in tailwind.config.js:
 *   import m3Preset from "@ipai/design-tokens/tailwind-material3.preset";
 *   export default {
 *     presets: [m3Preset],
 *     darkMode: 'class',
 *     prefix: 'tw-', // For Odoo safety
 *     ...
 *   }
 */

/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  theme: {
    extend: {
      /* =======================================================================
       * Typography
       * ======================================================================= */
      fontFamily: {
        sans: ['var(--md-sys-typescale-font-family-plain)', 'system-ui', 'sans-serif'],
        brand: ['var(--md-sys-typescale-font-family-brand)', 'system-ui', 'sans-serif'],
        mono: ['var(--md-sys-typescale-font-family-mono)', 'monospace'],
      },

      fontSize: {
        'display-large': ['var(--md-sys-typescale-display-large-size)', { lineHeight: '1.1', letterSpacing: '-0.25px' }],
        'display-medium': ['var(--md-sys-typescale-display-medium-size)', { lineHeight: '1.15', letterSpacing: '0' }],
        'display-small': ['var(--md-sys-typescale-display-small-size)', { lineHeight: '1.2', letterSpacing: '0' }],
        'headline-large': ['var(--md-sys-typescale-headline-large-size)', { lineHeight: '1.25', letterSpacing: '0' }],
        'headline-medium': ['var(--md-sys-typescale-headline-medium-size)', { lineHeight: '1.3', letterSpacing: '0' }],
        'headline-small': ['var(--md-sys-typescale-headline-small-size)', { lineHeight: '1.35', letterSpacing: '0' }],
        'title-large': ['var(--md-sys-typescale-title-large-size)', { lineHeight: '1.4', letterSpacing: '0' }],
        'title-medium': ['var(--md-sys-typescale-title-medium-size)', { lineHeight: '1.5', letterSpacing: '0.15px', fontWeight: '500' }],
        'title-small': ['var(--md-sys-typescale-title-small-size)', { lineHeight: '1.45', letterSpacing: '0.1px', fontWeight: '500' }],
        'body-large': ['var(--md-sys-typescale-body-large-size)', { lineHeight: '1.5', letterSpacing: '0.5px' }],
        'body-medium': ['var(--md-sys-typescale-body-medium-size)', { lineHeight: '1.45', letterSpacing: '0.25px' }],
        'body-small': ['var(--md-sys-typescale-body-small-size)', { lineHeight: '1.35', letterSpacing: '0.4px' }],
        'label-large': ['var(--md-sys-typescale-label-large-size)', { lineHeight: '1.45', letterSpacing: '0.1px', fontWeight: '500' }],
        'label-medium': ['var(--md-sys-typescale-label-medium-size)', { lineHeight: '1.35', letterSpacing: '0.5px', fontWeight: '500' }],
        'label-small': ['var(--md-sys-typescale-label-small-size)', { lineHeight: '1.3', letterSpacing: '0.5px', fontWeight: '500' }],
      },

      /* =======================================================================
       * Colors
       * ======================================================================= */
      colors: {
        // Primary
        primary: {
          DEFAULT: 'rgb(var(--md-sys-color-primary) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-primary) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-primary-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-primary-container) / <alpha-value>)',
        },

        // Secondary
        secondary: {
          DEFAULT: 'rgb(var(--md-sys-color-secondary) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-secondary) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-secondary-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-secondary-container) / <alpha-value>)',
        },

        // Tertiary
        tertiary: {
          DEFAULT: 'rgb(var(--md-sys-color-tertiary) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-tertiary) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-tertiary-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-tertiary-container) / <alpha-value>)',
        },

        // Error
        error: {
          DEFAULT: 'rgb(var(--md-sys-color-error) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-error) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-error-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-error-container) / <alpha-value>)',
        },

        // Surface (The core of Gemini aesthetics)
        surface: {
          DEFAULT: 'rgb(var(--md-sys-color-surface) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-surface) / <alpha-value>)',
          'on-variant': 'rgb(var(--md-sys-color-on-surface-variant) / <alpha-value>)',
          dim: 'rgb(var(--md-sys-color-surface-dim) / <alpha-value>)',
          bright: 'rgb(var(--md-sys-color-surface-bright) / <alpha-value>)',
          'container-lowest': 'rgb(var(--md-sys-color-surface-container-lowest) / <alpha-value>)',
          'container-low': 'rgb(var(--md-sys-color-surface-container-low) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-surface-container) / <alpha-value>)',
          'container-high': 'rgb(var(--md-sys-color-surface-container-high) / <alpha-value>)',
          'container-highest': 'rgb(var(--md-sys-color-surface-container-highest) / <alpha-value>)',
        },

        // Inverse
        inverse: {
          surface: 'rgb(var(--md-sys-color-inverse-surface) / <alpha-value>)',
          'on-surface': 'rgb(var(--md-sys-color-inverse-on-surface) / <alpha-value>)',
          primary: 'rgb(var(--md-sys-color-inverse-primary) / <alpha-value>)',
        },

        // Outline
        outline: {
          DEFAULT: 'rgb(var(--md-sys-color-outline) / <alpha-value>)',
          variant: 'rgb(var(--md-sys-color-outline-variant) / <alpha-value>)',
        },

        // Background (deprecated, use surface)
        background: 'rgb(var(--md-sys-color-background) / <alpha-value>)',
        'on-background': 'rgb(var(--md-sys-color-on-background) / <alpha-value>)',

        // Semantic status colors
        success: {
          DEFAULT: 'rgb(var(--md-sys-color-success) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-success) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-success-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-success-container) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--md-sys-color-warning) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-warning) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-warning-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-warning-container) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--md-sys-color-info) / <alpha-value>)',
          on: 'rgb(var(--md-sys-color-on-info) / <alpha-value>)',
          container: 'rgb(var(--md-sys-color-info-container) / <alpha-value>)',
          'on-container': 'rgb(var(--md-sys-color-on-info-container) / <alpha-value>)',
        },

        // Shadow & Scrim
        shadow: 'rgb(var(--md-sys-color-shadow) / <alpha-value>)',
        scrim: 'rgb(var(--md-sys-color-scrim) / <alpha-value>)',

        // UI Layer Colors (production-ready)
        ui: {
          muted: 'rgb(var(--ui-color-muted) / <alpha-value>)',
          subtle: 'rgb(var(--ui-color-subtle) / <alpha-value>)',
          success: 'rgb(var(--ui-color-success) / <alpha-value>)',
          warning: 'rgb(var(--ui-color-warning) / <alpha-value>)',
          danger: 'rgb(var(--ui-color-danger) / <alpha-value>)',
          info: 'rgb(var(--ui-color-info) / <alpha-value>)',
          scrim: 'rgb(var(--ui-color-scrim) / <alpha-value>)',
        },
      },

      /* =======================================================================
       * Text Colors (convenience aliases)
       * ======================================================================= */
      textColor: {
        'on-surface': 'rgb(var(--md-sys-color-on-surface) / <alpha-value>)',
        'on-surface-variant': 'rgb(var(--md-sys-color-on-surface-variant) / <alpha-value>)',
        'on-primary': 'rgb(var(--md-sys-color-on-primary) / <alpha-value>)',
        'on-primary-container': 'rgb(var(--md-sys-color-on-primary-container) / <alpha-value>)',
        'on-secondary': 'rgb(var(--md-sys-color-on-secondary) / <alpha-value>)',
        'on-secondary-container': 'rgb(var(--md-sys-color-on-secondary-container) / <alpha-value>)',
        'on-tertiary': 'rgb(var(--md-sys-color-on-tertiary) / <alpha-value>)',
        'on-tertiary-container': 'rgb(var(--md-sys-color-on-tertiary-container) / <alpha-value>)',
        'on-error': 'rgb(var(--md-sys-color-on-error) / <alpha-value>)',
        'on-error-container': 'rgb(var(--md-sys-color-on-error-container) / <alpha-value>)',
      },

      /* =======================================================================
       * Border Radius (M3 Shape System)
       * ======================================================================= */
      borderRadius: {
        none: 'var(--md-sys-shape-corner-none)',
        xs: 'var(--md-sys-shape-corner-extra-small)',
        sm: 'var(--md-sys-shape-corner-small)',
        md: 'var(--md-sys-shape-corner-medium)',
        DEFAULT: 'var(--md-sys-shape-corner-medium)',
        lg: 'var(--md-sys-shape-corner-large)',
        xl: 'var(--md-sys-shape-corner-extra-large)',
        '2xl': 'var(--radius-2xl)',
        '3xl': 'var(--radius-xl)',
        '4xl': 'var(--radius-2xl)',
        full: 'var(--md-sys-shape-corner-full)',
      },

      /* =======================================================================
       * Box Shadow (M3 Elevation System)
       * ======================================================================= */
      boxShadow: {
        'elevation-0': 'var(--md-sys-elevation-0)',
        'elevation-1': 'var(--md-sys-elevation-1)',
        'elevation-2': 'var(--md-sys-elevation-2)',
        'elevation-3': 'var(--md-sys-elevation-3)',
        'elevation-4': 'var(--md-sys-elevation-4)',
        'elevation-5': 'var(--md-sys-elevation-5)',
        // Production elevation
        'elev-1': 'var(--elev-1)',
        'elev-2': 'var(--elev-2)',
        'elev-3': 'var(--elev-3)',
        // Semantic aliases
        'sm': 'var(--md-sys-elevation-1)',
        'md': 'var(--md-sys-elevation-2)',
        'lg': 'var(--md-sys-elevation-3)',
        'xl': 'var(--md-sys-elevation-4)',
        '2xl': 'var(--md-sys-elevation-5)',
      },

      /* =======================================================================
       * Background Images (Gemini Gradients)
       * ======================================================================= */
      backgroundImage: {
        'gemini-gradient': 'var(--md-gemini-gradient)',
        'gemini-mesh': 'var(--md-gemini-mesh)',
        'gemini-glow': 'var(--md-gemini-glow)',
      },

      /* =======================================================================
       * Transitions (M3 Motion)
       * ======================================================================= */
      transitionTimingFunction: {
        'standard': 'cubic-bezier(0.2, 0, 0, 1)',
        'standard-decelerate': 'cubic-bezier(0, 0, 0, 1)',
        'standard-accelerate': 'cubic-bezier(0.3, 0, 1, 1)',
        'emphasized': 'cubic-bezier(0.2, 0, 0, 1)',
        'emphasized-decelerate': 'cubic-bezier(0.05, 0.7, 0.1, 1)',
        'emphasized-accelerate': 'cubic-bezier(0.3, 0, 0.8, 0.15)',
      },

      transitionDuration: {
        'short-1': '50ms',
        'short-2': '100ms',
        'short-3': '150ms',
        'short-4': '200ms',
        'medium-1': '250ms',
        'medium-2': '300ms',
        'medium-3': '350ms',
        'medium-4': '400ms',
        'long-1': '450ms',
        'long-2': '500ms',
        'long-3': '550ms',
        'long-4': '600ms',
        'extra-long-1': '700ms',
        'extra-long-2': '800ms',
        'extra-long-3': '900ms',
        'extra-long-4': '1000ms',
      },

      /* =======================================================================
       * Opacity (M3 State Layers)
       * ======================================================================= */
      opacity: {
        'hover': 'var(--md-sys-state-hover-opacity)',
        'focus': 'var(--md-sys-state-focus-opacity)',
        'pressed': 'var(--md-sys-state-pressed-opacity)',
        'dragged': 'var(--md-sys-state-dragged-opacity)',
        '8': '0.08',
        '12': '0.12',
        '16': '0.16',
      },

      /* =======================================================================
       * Z-Index Scale
       * ======================================================================= */
      zIndex: {
        'navigation': '100',
        'modal': '200',
        'popup': '300',
        'notification': '400',
        'tooltip': '500',
      },

      /* =======================================================================
       * Spacing
       * ======================================================================= */
      spacing: {
        '4.5': '1.125rem',  // 18px
        '13': '3.25rem',    // 52px
        '15': '3.75rem',    // 60px
        '18': '4.5rem',     // 72px
        '22': '5.5rem',     // 88px
      },

      /* =======================================================================
       * Keyframes & Animations
       * ======================================================================= */
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
      },

      animation: {
        'fade-in': 'fade-in 200ms var(--md-sys-motion-easing-emphasized-decelerate, ease-out)',
        'fade-out': 'fade-out 150ms var(--md-sys-motion-easing-emphasized-accelerate, ease-in)',
        'slide-up': 'slide-up 300ms var(--md-sys-motion-easing-emphasized-decelerate, ease-out)',
        'slide-down': 'slide-down 300ms var(--md-sys-motion-easing-emphasized-decelerate, ease-out)',
        'scale-in': 'scale-in 200ms var(--md-sys-motion-easing-emphasized-decelerate, ease-out)',
        'spin-slow': 'spin-slow 3s linear infinite',
      },
    },
  },
};

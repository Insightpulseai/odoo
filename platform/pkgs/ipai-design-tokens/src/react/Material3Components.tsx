/**
 * Material 3 "Expressive" React Components
 * =========================================
 *
 * Production-ready React components implementing the M3 Expressive theme.
 * These components are designed for Gemini-style AI chat interfaces.
 *
 * Usage:
 * ```tsx
 * import {
 *   M3PromptInput,
 *   M3ResponseCard,
 *   M3Button,
 *   M3ThemeToggle
 * } from '@ipai/design-tokens/react/Material3Components';
 * ```
 *
 * IMPORTANT: For Odoo integration, wrap your app with:
 * <div id="ipai-ai-root" className="tbwa">...</div>
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  toggleM3Theme,
  initM3Theme,
  onM3ThemeChange,
  type M3ThemeMode,
} from '../material3Theme';

/* =============================================================================
 * M3 Prompt Input (Gemini-style)
 * ============================================================================= */

export interface M3PromptInputProps {
  placeholder?: string;
  onSubmit?: (value: string) => void;
  disabled?: boolean;
  className?: string;
}

export function M3PromptInput({
  placeholder = 'Ask InsightPulse ERP...',
  onSubmit,
  disabled = false,
  className = '',
}: M3PromptInputProps) {
  const [value, setValue] = useState('');

  const handleSubmit = useCallback(() => {
    if (value.trim() && onSubmit) {
      onSubmit(value.trim());
      setValue('');
    }
  }, [value, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className={`tw-w-full tw-max-w-3xl tw-mx-auto tw-p-4 ${className}`}>
      <div
        className={`
          tw-relative tw-rounded-3xl tw-bg-surface-container-low tw-p-4
          tw-border tw-border-transparent tw-shadow-elev-1 tw-transition-ui
          hover:tw-bg-surface-container
          focus-within:tw-bg-surface focus-within:tw-border-outline-variant focus-within:tw-shadow-elev-2
          ${disabled ? 'tw-opacity-60 tw-pointer-events-none' : ''}
        `}
      >
        <textarea
          className="
            tw-w-full tw-bg-transparent tw-text-on-surface
            tw-placeholder-ui-muted tw-resize-none tw-outline-none
            tw-text-lg tw-leading-7
          "
          rows={1}
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
        />

        <div className="tw-flex tw-justify-between tw-items-center tw-mt-3">
          <div className="tw-flex tw-gap-2 tw-text-ui-muted">
            <button
              type="button"
              className="
                tw-p-2 tw-rounded-full tw-transition-ui
                hover:tw-bg-surface-container-high
              "
              aria-label="Add attachment"
            >
              <svg
                className="tw-w-5 tw-h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </button>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!value.trim() || disabled}
            className={`
              tw-p-2 tw-rounded-full tw-transition-ui
              tw-bg-primary tw-text-primary-on
              hover:tw-opacity-90 active:tw-scale-[0.98]
              focus:tw-outline-none focus-visible:tw-ring-2 focus-visible:tw-ring-primary/50
              disabled:tw-opacity-50 disabled:tw-cursor-not-allowed
            `}
            aria-label="Send message"
          >
            <svg
              className="tw-w-5 tw-h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 12h14M12 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

/* =============================================================================
 * M3 Response Card (Bot Response)
 * ============================================================================= */

export interface M3ResponseCardProps {
  children: React.ReactNode;
  title?: string;
  actions?: React.ReactNode;
  showAvatar?: boolean;
  className?: string;
}

export function M3ResponseCard({
  children,
  title,
  actions,
  showAvatar = true,
  className = '',
}: M3ResponseCardProps) {
  return (
    <div className={`tw-flex tw-gap-4 tw-max-w-3xl tw-mx-auto tw-mb-8 ${className}`}>
      {showAvatar && (
        <div
          className="tw-w-8 tw-h-8 tw-rounded-full tw-flex-shrink-0"
          style={{ background: 'var(--md-gemini-gradient)' }}
        />
      )}

      <div className="tw-flex-1 tw-space-y-4">
        {title && (
          <div className="tw-text-on-surface tw-text-base tw-leading-relaxed">
            {title}
          </div>
        )}

        <div
          className="
            tw-bg-surface-container tw-rounded-3xl tw-p-6
            tw-border tw-border-outline-variant/30
          "
        >
          {children}

          {actions && (
            <div className="tw-flex tw-gap-2 tw-mt-6">
              {actions}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* =============================================================================
 * M3 Button Variants
 * ============================================================================= */

export interface M3ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'filled' | 'outlined' | 'text' | 'tonal';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function M3Button({
  variant = 'filled',
  size = 'md',
  children,
  className = '',
  ...props
}: M3ButtonProps) {
  const sizeClasses = {
    sm: 'tw-px-4 tw-py-1.5 tw-text-sm',
    md: 'tw-px-6 tw-py-2.5 tw-text-sm',
    lg: 'tw-px-8 tw-py-3 tw-text-base',
  };

  const variantClasses = {
    filled: `
      tw-bg-primary tw-text-primary-on
      hover:tw-shadow-md active:tw-shadow-sm
    `,
    outlined: `
      tw-bg-transparent tw-text-primary
      tw-border tw-border-outline
      hover:tw-bg-primary/[0.08] active:tw-bg-primary/[0.12]
    `,
    text: `
      tw-bg-transparent tw-text-primary
      hover:tw-bg-primary/[0.08] active:tw-bg-primary/[0.12]
    `,
    tonal: `
      tw-bg-secondary-container tw-text-on-secondary-container
      hover:tw-shadow-sm active:tw-shadow-none
    `,
  };

  return (
    <button
      className={`
        tw-inline-flex tw-items-center tw-justify-center tw-rounded-full
        tw-font-medium tw-transition-ui
        focus:tw-outline-none focus-visible:tw-ring-2 focus-visible:tw-ring-primary/50
        disabled:tw-opacity-50 disabled:tw-cursor-not-allowed
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}

/* =============================================================================
 * M3 Theme Toggle
 * ============================================================================= */

export interface M3ThemeToggleProps {
  className?: string;
}

export function M3ThemeToggle({ className = '' }: M3ThemeToggleProps) {
  const [mode, setMode] = useState<M3ThemeMode>('light');

  useEffect(() => {
    // Initialize theme
    const initialMode = initM3Theme();
    setMode(initialMode);

    // Listen for theme changes
    const unsubscribe = onM3ThemeChange((newMode) => {
      setMode(newMode);
    });

    return unsubscribe;
  }, []);

  const handleToggle = useCallback(() => {
    const newMode = toggleM3Theme();
    setMode(newMode);
  }, []);

  return (
    <button
      type="button"
      onClick={handleToggle}
      className={`
        tw-p-2 tw-rounded-full tw-transition-ui
        tw-bg-surface-container-high tw-text-on-surface-variant
        hover:tw-bg-surface-container-highest
        focus:tw-outline-none focus-visible:tw-ring-2 focus-visible:tw-ring-primary/50
        ${className}
      `}
      aria-label={`Switch to ${mode === 'dark' ? 'light' : 'dark'} mode`}
    >
      {mode === 'dark' ? (
        <svg className="tw-w-5 tw-h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
      ) : (
        <svg className="tw-w-5 tw-h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      )}
    </button>
  );
}

/* =============================================================================
 * M3 Chip
 * ============================================================================= */

export interface M3ChipProps {
  children: React.ReactNode;
  selected?: boolean;
  onClick?: () => void;
  className?: string;
}

export function M3Chip({
  children,
  selected = false,
  onClick,
  className = '',
}: M3ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        tw-inline-flex tw-items-center tw-gap-2 tw-px-4 tw-py-1.5 tw-rounded-lg
        tw-text-sm tw-transition-ui
        ${
          selected
            ? 'tw-bg-secondary-container tw-text-on-secondary-container tw-border-transparent'
            : 'tw-bg-surface-container-high tw-text-on-surface-variant tw-border tw-border-outline-variant/50'
        }
        hover:tw-bg-surface-container-highest
        focus:tw-outline-none focus-visible:tw-ring-2 focus-visible:tw-ring-primary/50
        ${className}
      `}
    >
      {children}
    </button>
  );
}

/* =============================================================================
 * M3 Loading Indicator (Typing Dots)
 * ============================================================================= */

export function M3LoadingDots({ className = '' }: { className?: string }) {
  return (
    <div className={`tw-flex tw-items-center tw-gap-1 ${className}`}>
      <span
        className="tw-w-2 tw-h-2 tw-rounded-full tw-bg-primary"
        style={{ animation: 'typing-dots 1.4s infinite ease-in-out both' }}
      />
      <span
        className="tw-w-2 tw-h-2 tw-rounded-full tw-bg-primary"
        style={{ animation: 'typing-dots 1.4s infinite ease-in-out both', animationDelay: '0.2s' }}
      />
      <span
        className="tw-w-2 tw-h-2 tw-rounded-full tw-bg-primary"
        style={{ animation: 'typing-dots 1.4s infinite ease-in-out both', animationDelay: '0.4s' }}
      />
    </div>
  );
}

/* =============================================================================
 * M3 Data Row (for tables/lists in response cards)
 * ============================================================================= */

export interface M3DataRowProps {
  label: string;
  value: string | React.ReactNode;
  className?: string;
}

export function M3DataRow({ label, value, className = '' }: M3DataRowProps) {
  return (
    <div
      className={`
        tw-flex tw-justify-between tw-items-center tw-py-3
        tw-border-b tw-border-outline-variant/20
        last:tw-border-b-0
        ${className}
      `}
    >
      <span className="tw-text-on-surface/80">{label}</span>
      <span className="tw-font-mono tw-text-on-surface tw-font-semibold">{value}</span>
    </div>
  );
}

/* =============================================================================
 * M3 App Root Wrapper (for Odoo safety)
 * ============================================================================= */

export interface M3AppRootProps {
  children: React.ReactNode;
  useTBWAAccent?: boolean;
  className?: string;
}

export function M3AppRoot({
  children,
  useTBWAAccent = false,
  className = '',
}: M3AppRootProps) {
  useEffect(() => {
    initM3Theme();
  }, []);

  return (
    <div
      id="ipai-ai-root"
      className={`
        tw-bg-surface tw-text-on-surface tw-font-sans tw-antialiased
        tw-min-h-screen
        ${useTBWAAccent ? 'tbwa' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

/* =============================================================================
 * Exports
 * ============================================================================= */

export default {
  M3PromptInput,
  M3ResponseCard,
  M3Button,
  M3ThemeToggle,
  M3Chip,
  M3LoadingDots,
  M3DataRow,
  M3AppRoot,
};

/**
 * Design tokens for Noble Finances accounting services website
 * Extracted from Friendly Accounting Services mockups
 */

export const colors = {
  // Primary palette
  mint: {
    50: '#F0FAF0',
    100: '#E8F5E1',
    200: '#D1EBC3',
    300: '#B9E1A5',
    400: '#A2D787',
    500: '#8BCD69',
    600: '#6FB54B',
    700: '#539D2D',
    800: '#37850F',
    900: '#1B6D00',
  },
  forest: {
    50: '#E8F2ED',
    100: '#D1E5DB',
    200: '#A3CBB7',
    300: '#75B193',
    400: '#47976F',
    500: '#2C6B4F',
    600: '#1B4332',
    700: '#153529',
    800: '#0F2720',
    900: '#091917',
  },
  // Neutrals
  white: '#FFFFFF',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
}

export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    display: ['Cal Sans', 'Inter', 'system-ui', 'sans-serif'],
  },
  fontSize: {
    hero: ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
    h1: ['2.5rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
    h2: ['2rem', { lineHeight: '1.3', letterSpacing: '-0.01em' }],
    h3: ['1.5rem', { lineHeight: '1.4' }],
    h4: ['1.25rem', { lineHeight: '1.5' }],
    body: ['1rem', { lineHeight: '1.6' }],
    small: ['0.875rem', { lineHeight: '1.5' }],
  },
}

export const spacing = {
  section: {
    mobile: '3rem',
    tablet: '4rem',
    desktop: '5rem',
  },
  container: {
    mobile: '1.5rem',
    tablet: '2rem',
    desktop: '4rem',
  },
}

export const breakpoints = {
  mobile: '640px',
  tablet: '768px',
  desktop: '1024px',
  wide: '1280px',
}

export const borderRadius = {
  sm: '0.5rem',
  md: '0.75rem',
  lg: '1rem',
  xl: '1.5rem',
  full: '9999px',
}

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1)',
}

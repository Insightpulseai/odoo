/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [require('@ipai/design-tokens/tailwind.preset').default],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Financial services specific accent colors
        finance: {
          navy: '#0F2A44',
          navyDeep: '#0A1E33',
          teal: '#64B9CA',
          green: '#7BC043',
          amber: '#F6C445',
          slate: '#1E293B',
          gold: '#D4AF37',
          trust: '#0066CC',
        },
      },
      backdropBlur: {
        'glass': '24px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'hero-pattern': "url('/solutions/financial-services/bg/camo-pattern-bg.webp')",
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
  darkMode: 'class',
};

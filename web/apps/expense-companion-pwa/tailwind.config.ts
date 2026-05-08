import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        ember: '#f45d22',
        ink: '#101417',
        sand: '#f5efe6',
        mint: '#b7f3d0',
        slate: '#74818e',
      },
      boxShadow: {
        panel: '0 24px 80px rgba(13, 17, 23, 0.12)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
};

export default config;

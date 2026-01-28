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
        tbwa: {
          black: '#000000',
          yellow: '#FFED00',
          gray: '#f8f9fa',
        },
      },
    },
  },
  plugins: [],
};

export default config;

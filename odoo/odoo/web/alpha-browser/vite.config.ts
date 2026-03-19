import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        'service-worker': resolve(__dirname, 'src/background/service-worker.ts'),
        'content-main': resolve(__dirname, 'src/content/content-main.ts'),
        popup: resolve(__dirname, 'src/popup/popup.html'),
        offscreen: resolve(__dirname, 'src/offscreen/offscreen.html')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          // Service worker and content script in root
          if (chunkInfo.name === 'service-worker' || chunkInfo.name === 'content-main') {
            return '[name].js';
          }
          // Other assets in assets/
          return 'assets/[name]-[hash].js';
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          // CSS in root
          if (assetInfo.name?.endsWith('.css')) {
            return '[name][extname]';
          }
          // HTML files preserve structure
          if (assetInfo.name?.endsWith('.html')) {
            return 'src/[name][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        }
      }
    }
  }
});

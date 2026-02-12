import { defineConfig } from 'tsup';

export default defineConfig({
  entry: [
    'src/index.ts',
    'src/loaders/browser.ts',
    'src/loaders/node.ts',
    'src/loaders/cdn.ts',
    'src/themes/dark.ts',
    'src/themes/shine.ts',
    'src/themes/vintage.ts',
    'src/themes/roma.ts',
    'src/themes/macarons.ts',
    'src/themes/infographic.ts',
  ],
  format: ['cjs', 'esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  treeshake: true,
  minify: false,
});

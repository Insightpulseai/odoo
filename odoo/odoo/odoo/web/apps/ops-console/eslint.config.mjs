import { dirname } from 'path'
import { fileURLToPath } from 'url'
import { FlatCompat } from '@eslint/eslintrc'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname,
})

/** @type {import('eslint').Linter.Config[]} */
const config = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      // Disallow any type in non-legacy code (warn, not error, during migration).
      '@typescript-eslint/no-explicit-any': 'warn',
      // Prefer const assertions for readonly data.
      'prefer-const': 'error',
    },
  },
]

export default config

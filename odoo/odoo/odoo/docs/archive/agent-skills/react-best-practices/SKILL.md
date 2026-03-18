---
name: vercel-react-best-practices
description: Review React code for performance, security, and maintainability. Use when reviewing components, optimizing bundles, or refactoring for React 19.
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Vercel React Best Practices

Review React code for performance, security, and maintainability.

## Rule Categories by Priority

| Priority | Category                  | Impact | Prefix     |
| -------- | ------------------------- | ------ | ---------- |
| 1        | Performance (Waterfall)   | HIGH   | `perf-wf-` |
| 1        | Performance (Bundle)      | HIGH   | `perf-bn-` |
| 2        | Security (Data Leak)      | HIGH   | `sec-dk-`  |
| 3        | Maintainability (Pattern) | MEDIUM | `maint-`   |

## Usage

Check code against the categories above. Focus on eliminating waterfalls and optimizing bundle sizes first.

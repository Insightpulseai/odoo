# Packaging Fix: Renderer Loading Bug

## Problem

Colima Desktop Electron app showed blank white page when launched from packaged DMG.

### Root Cause

TypeScript preserves source directory structure when compiling:
- Source: `src/main/index.ts`
- Compiled: `dist-main/src/main/index.js`

This meant `__dirname` at runtime was `dist-main/src/main`, causing:

```javascript
path.join(__dirname, '../dist-renderer/index.html')
// Resolved to: dist-main/src/dist-renderer/index.html ❌ (wrong path)
// Should be: dist-renderer/index.html ✅ (correct path)
```

### Symptoms

- Blank white page on app launch
- Console error: "Not allowed to load local resource"
- DevTools showing 404 for renderer HTML

## Solution

### 1. Implemented Packaging-Safe Renderer Resolver

Added `getRendererEntry()` function that uses `app.getAppPath()` to get the correct base path:

```typescript
function getRendererEntry(): { kind: 'url' | 'file'; value: string } {
  if (process.env.NODE_ENV === 'development') {
    return { kind: 'url', value: 'http://localhost:5173' };
  }

  const appPath = app.getAppPath();
  const rendererPath = path.join(appPath, 'dist-renderer', 'index.html');
  return { kind: 'file', value: rendererPath };
}
```

### 2. Fixed DevTools Auto-Open

Changed DevTools to only open in development mode:

```typescript
// Open DevTools in development only
if (process.env.NODE_ENV === 'development') {
  mainWindow.webContents.openDevTools();
}
```

## Files Modified

- `src/main/index.ts`: Added renderer resolver, fixed DevTools behavior

## Verification

### Build Verification

```bash
pnpm build  # Compiles TypeScript
pnpm package  # Creates DMG
```

### Package Structure Verification

```bash
# Verify dist structure
npx asar list "dist/mac-arm64/Colima Desktop.app/Contents/Resources/app.asar"
```

Expected structure:
```
/dist-renderer/
  index.html
  assets/
    index-*.js
    index-*.css
/dist-main/
  src/
    main/
      index.js
      ipc-handlers.js
      ...
```

### Runtime Verification

1. Install packaged DMG
2. Launch app
3. Verify UI renders (not blank)
4. Verify DevTools does NOT auto-open
5. Check console for no path errors

## Before/After

### Before

```typescript
// ❌ Broken path resolution
mainWindow.loadFile(path.join(__dirname, '../dist-renderer/index.html'));
// __dirname = dist-main/src/main
// Resolves to: dist-main/src/dist-renderer/index.html
```

### After

```typescript
// ✅ Correct path resolution
const appPath = app.getAppPath();
const rendererPath = path.join(appPath, 'dist-renderer', 'index.html');
mainWindow.loadFile(rendererPath);
// app.getAppPath() = /path/to/app.asar
// Resolves to: /path/to/app.asar/dist-renderer/index.html
```

## Related Issues

- Electron packaging with TypeScript directory structure preservation
- `app.getAppPath()` vs `__dirname` in packaged apps
- Development vs production renderer loading

## Testing Commands

```bash
# Build and package
pnpm build && pnpm package

# Verify asar contents
npx asar list "dist/mac-arm64/Colima Desktop.app/Contents/Resources/app.asar" | grep renderer

# Extract and inspect
npx asar extract "dist/mac-arm64/Colima Desktop.app/Contents/Resources/app.asar" /tmp/app-check
grep -A 10 "getRendererEntry" /tmp/app-check/dist-main/src/main/index.js
```

## Date

2026-02-15

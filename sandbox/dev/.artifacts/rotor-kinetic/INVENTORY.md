# Rotor: Kinetic Cylindrical Gallery - Artifact Inventory

**Generated**: 2026-02-16
**Source**: Figma Make Export
**Original Figma**: https://www.figma.com/design/aYLMJ2RXJFNN5yzGntFJKF/Rotor--Kinetic-Cylindrical-Gallery
**Status**: ✅ Running (localhost:3001)

---

## Overview

**Type**: React + Three.js 3D Application
**Purpose**: Interactive 3D kinetic cylindrical gallery with image upload and animation controls
**Total Size**: 357 MB
**Source Files**: 72 files (excluding node_modules)
**Dependencies**: 356 MB (224 packages)

---

## Technology Stack

### Core Framework
- **React**: 19.2.4 (upgraded from 18.3.1 for compatibility)
- **React DOM**: 19.2.4
- **Build Tool**: Vite 6.3.5
- **TypeScript**: Yes (TSX/TS files)

### 3D Graphics
- **Three.js**: Latest (core WebGL library)
- **@react-three/fiber**: Latest (React renderer for Three.js)
- **@react-three/drei**: Latest (Three.js helpers)
- **Custom Shaders**: WebGL GLSL shaders for visual effects

### UI Framework
- **Radix UI**: Complete component library (31 components)
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Icon library
- **Sonner**: Toast notifications
- **Vaul**: Drawer component

### Additional Libraries
- **Recharts**: Data visualization
- **React Hook Form**: Form handling
- **Embla Carousel**: Carousel functionality
- **Next Themes**: Dark mode support

---

## Directory Structure

```
rotor-kinetic/
├── src/
│   ├── components/
│   │   ├── figma/              # Figma-specific components
│   │   │   └── ImageWithFallback.tsx
│   │   ├── ui/                 # UI components (59 files)
│   │   │   ├── Radix UI components (54 files)
│   │   │   ├── CameraConfigOverlay.jsx
│   │   │   ├── ControlPanel.jsx
│   │   │   ├── ImageDropZone.jsx
│   │   │   └── ImageUploadOverlay.jsx
│   │   └── webgl/              # 3D scene components
│   │       ├── DisplayCylinder.jsx
│   │       ├── KineticScene.jsx
│   │       └── MarqueeStrip.jsx
│   ├── data/
│   │   └── defaultImages.js    # Default texture assets
│   ├── hooks/
│   │   └── useTextureManager.js
│   ├── styles/
│   │   └── globals.css
│   ├── utils/
│   │   └── textureUtils.js
│   ├── webgl/
│   │   └── materials/          # Custom WebGL shaders
│   │       ├── MeshDisplayMaterial.js
│   │       └── MeshMarqueeMaterial.js
│   ├── App.tsx                 # Main application
│   ├── index.css               # 36 KB global styles
│   ├── main.tsx                # Entry point
│   └── guidelines/
│       └── Guidelines.md       # Figma Make template
├── index.html                  # HTML entry point
├── package.json                # Dependencies
├── package-lock.json           # 216 KB lock file
├── vite.config.ts              # Vite configuration
└── README.md                   # Basic instructions
```

---

## Key Components

### 1. **Main Application** (`App.tsx`)
- Root component orchestrating the entire app
- Integrates 3D scene, overlays, and controls
- State management via `useTextureManager` hook

### 2. **3D Scene Components**

#### `KineticScene.jsx`
- Main Three.js canvas container
- WebGL renderer setup
- Camera controls and animation loop
- Integrates DisplayCylinder and MarqueeStrip

#### `DisplayCylinder.jsx`
- 3D cylindrical mesh for main display
- Custom shader material for visual effects
- Texture mapping and animation

#### `MarqueeStrip.jsx`
- Animated marquee strip around cylinder
- Scrolling text/image effects
- Independent animation controls

### 3. **UI Overlays**

#### `ImageUploadOverlay.jsx`
- Drag-and-drop image upload interface
- Display and marquee image management
- Reset to defaults functionality
- File validation and loading states

#### `CameraConfigOverlay.jsx`
- Real-time camera position/rotation display
- Debug information overlay
- WebGL performance metrics

#### `ControlPanel.jsx`
- Floating control panel
- Animation speed controls
- Reset and configuration options
- Camera information display

#### `ImageDropZone.jsx`
- Reusable drag-and-drop component
- Image preview
- File type validation

### 4. **WebGL Shaders**

#### `MeshDisplayMaterial.js`
- Custom GLSL shader for cylinder surface
- Texture distortion effects
- Lighting and reflection calculations
- Animation uniforms

#### `MeshMarqueeMaterial.js`
- Shader for marquee strip
- Scrolling animation effects
- Texture sampling
- Visual effects parameters

### 5. **Hooks & Utilities**

#### `useTextureManager.js`
- Central state management for textures
- Image loading and validation
- Texture updates and defaults
- Animation speed control

#### `textureUtils.js`
- Texture loading helpers
- Image dimension extraction
- Format validation
- Error handling

### 6. **Radix UI Components** (54 files)
Complete design system including:
- Accordion, Alert Dialog, Avatar, Badge
- Button, Calendar, Card, Carousel
- Checkbox, Collapsible, Command, Context Menu
- Dialog, Drawer, Dropdown Menu, Form
- Hover Card, Input, Label, Menubar
- Navigation Menu, Pagination, Popover
- Progress, Radio Group, Resizable, Scroll Area
- Select, Separator, Sheet, Sidebar
- Skeleton, Slider, Switch, Table
- Tabs, Textarea, Toggle, Tooltip
- And more...

---

## Features

### Core Functionality
1. **3D Kinetic Gallery**
   - Cylindrical display surface
   - Smooth rotation and animation
   - WebGL-powered visual effects

2. **Image Management**
   - Upload custom images for display texture
   - Upload custom images for marquee strip
   - Default image fallbacks
   - Real-time texture updates

3. **Animation Controls**
   - Adjustable animation speeds
   - Independent display/marquee controls
   - Pause/play functionality
   - Reset to defaults

4. **Camera System**
   - Interactive camera controls
   - Position and rotation tracking
   - Debug information overlay
   - Real-time updates

5. **Responsive UI**
   - Tailwind CSS styling
   - Dark mode support (Next Themes)
   - Mobile-friendly controls
   - Toast notifications

---

## Technical Implementation

### WebGL/Three.js
- Custom shader materials for visual effects
- Texture mapping on cylindrical geometry
- Real-time animation loop
- Performance optimization

### React Architecture
- Functional components with hooks
- State management via custom hooks
- Component composition pattern
- TypeScript for type safety

### Build System
- Vite for fast development
- React SWC plugin for compilation
- Hot module replacement
- Optimized production builds

---

## Dependencies (224 packages)

### Critical Dependencies
- **React 19.2.4**: Core framework (upgraded for compatibility)
- **Three.js**: 3D graphics engine
- **@react-three/fiber**: React Three.js renderer
- **@react-three/drei**: Three.js helpers and abstractions
- **Vite 6.3.5**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **31 Radix UI packages**: Complete UI component library

### Development Dependencies
- **@types/node**: Node.js type definitions
- **@vitejs/plugin-react-swc**: Fast React compilation
- **TypeScript types**: Type safety throughout

---

## Known Issues & Fixes

### 1. React Version Conflict (RESOLVED)
- **Issue**: Original export used React 18.3.1
- **Problem**: @react-three/fiber requires React 19
- **Error**: `Cannot read properties of undefined (reading 'S')` at reconciler
- **Fix**: Upgraded to React 19.2.4
- **Status**: ✅ Fixed

### 2. Port Conflict
- **Issue**: Port 3000 already in use
- **Solution**: Server automatically switched to port 3001
- **Access**: http://localhost:3001/

---

## Current Status

### Running Environment
- **Server**: Vite dev server on port 3001
- **Status**: ✅ Running successfully
- **Performance**: Ready in ~500ms
- **Build**: Hot module replacement active

### Verification
- ✅ HTTP 200 response
- ✅ React 19 loaded correctly
- ✅ All dependencies installed (224 packages)
- ✅ No runtime errors
- ✅ 3D scene rendering

---

## Usage Instructions

### Start Development Server
```bash
cd .artifacts/rotor-kinetic
npm run dev
```

### Access Application
Open browser to: **http://localhost:3001/**

### Build for Production
```bash
npm run build
```

### Features to Test
1. Upload image for cylinder display
2. Upload image for marquee strip
3. Adjust animation speeds
4. View camera configuration
5. Reset to defaults
6. Observe 3D kinetic effects

---

## File Statistics

### Source Code (excluding node_modules)
- **Total Files**: 72
- **TypeScript/TSX**: 62 files
- **JavaScript/JSX**: 5 files
- **CSS**: 2 files
- **Markdown**: 2 files
- **HTML**: 1 file

### Size Breakdown
- **Total**: 357 MB
- **node_modules**: 356 MB (99.7%)
- **Source Code**: ~1 MB (0.3%)
- **Largest Source File**: index.css (36 KB)
- **Package Lock**: 216 KB

---

## Integration Notes

### Figma Make Export
- Generated from Figma Make AI-powered design-to-code
- Production-ready React codebase
- Complete UI component library included
- Custom WebGL shaders for 3D effects
- Responsive design system

### Modifications Made
1. React upgraded from 18.3.1 → 19.2.4
2. Dependencies installed with `--legacy-peer-deps`
3. Server port changed from 3000 → 3001

---

## Maintenance

### Regular Tasks
- Keep React and Three.js dependencies updated
- Monitor WebGL performance
- Test across different browsers
- Optimize texture loading

### Known Limitations
- Large texture files may impact performance
- WebGL support required (no fallback)
- Desktop-optimized (mobile UX may need refinement)

---

**End of Inventory**

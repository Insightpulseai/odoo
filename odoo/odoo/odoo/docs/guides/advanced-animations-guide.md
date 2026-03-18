# Advanced Animations in Odoo 19: SVG, Lottie, GSAP & Three.js

Complete guide for implementing premium animations, micro-interactions, and 3D graphics in Odoo's OWL framework.

---

## Table of Contents

1. [Overview](#overview)
2. [SVG Illustrations & Micro-interactions](#svg-illustrations--micro-interactions)
3. [Lottie Animations](#lottie-animations)
4. [GSAP (GreenSock) Integration](#gsap-greensock-integration)
5. [Three.js 3D Graphics](#threejs-3d-graphics)
6. [Avatar Motion & Character Animation](#avatar-motion--character-animation)
7. [Creative Content: Logos, Icons, Images](#creative-content-logos-icons-images)
8. [OWL Lifecycle Hooks for Animations](#owl-lifecycle-hooks-for-animations)
9. [Performance Optimization](#performance-optimization)
10. [Complete Examples](#complete-examples)

---

## Overview

Modern web animations enhance UX through:

- **Micro-interactions**: Subtle feedback for user actions
- **SVG illustrations**: Scalable, animatable vector graphics
- **Lottie**: Lightweight JSON-based animations from After Effects
- **GSAP**: Professional-grade animation library
- **Three.js**: WebGL-powered 3D graphics

### Why Animations in Odoo?

- **Premium UX**: Match Enterprise Edition feel
- **User Engagement**: Guide attention, provide feedback
- **Brand Identity**: Unique, memorable interactions
- **Performance**: Modern libraries are GPU-accelerated

---

## SVG Illustrations & Micro-interactions

### 1. SVG Basics in Odoo

**Inline SVG in QWeb Template**:

```xml
<templates xml:space="preserve">
    <t t-name="ipai.AnimatedIcon" owl="1">
        <div class="animated-icon">
            <svg width="100" height="100" viewBox="0 0 100 100">
                <circle class="pulse-circle" cx="50" cy="50" r="40"
                        fill="none" stroke="#714B67" stroke-width="2"/>
                <path class="checkmark" d="M30,50 L45,65 L70,35"
                      fill="none" stroke="#714B67" stroke-width="3"/>
            </svg>
        </div>
    </t>
</templates>
```

**CSS Animations** (`static/src/css/animations.css`):

```css
.pulse-circle {
  animation: pulse 2s ease-in-out infinite;
  transform-origin: center;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
}

.checkmark {
  stroke-dasharray: 100;
  stroke-dashoffset: 100;
  animation: draw 1s ease-out forwards;
}

@keyframes draw {
  to {
    stroke-dashoffset: 0;
  }
}
```

### 2. SVG Micro-interactions

**Button Hover Effect**:

```xml
<t t-name="ipai.AnimatedButton" owl="1">
    <button class="btn-animated" t-on-click="handleClick">
        <svg class="btn-icon" width="24" height="24" viewBox="0 0 24 24">
            <circle class="bg-circle" cx="12" cy="12" r="10"/>
            <path class="arrow" d="M8,12 L16,12 M13,9 L16,12 L13,15"/>
        </svg>
        <span t-esc="props.label"/>
    </button>
</t>
```

```css
.btn-animated:hover .bg-circle {
  transform: scale(1.2);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.btn-animated:hover .arrow {
  transform: translateX(4px);
  transition: transform 0.3s ease;
}
```

### 3. Loading States

**Spinner Component**:

```xml
<t t-name="ipai.LoadingSpinner" owl="1">
    <div class="loading-spinner">
        <svg width="50" height="50" viewBox="0 0 50 50">
            <circle class="spinner-track" cx="25" cy="25" r="20"
                    fill="none" stroke="#e0e0e0" stroke-width="4"/>
            <circle class="spinner-head" cx="25" cy="25" r="20"
                    fill="none" stroke="#714B67" stroke-width="4"
                    stroke-linecap="round"/>
        </svg>
    </div>
</t>
```

```css
.spinner-head {
  stroke-dasharray: 125;
  stroke-dashoffset: 0;
  animation: spin 1.5s ease-in-out infinite;
  transform-origin: center;
}

@keyframes spin {
  0% {
    stroke-dashoffset: 125;
    transform: rotate(0deg);
  }
  50% {
    stroke-dashoffset: 31.25;
    transform: rotate(720deg);
  }
  100% {
    stroke-dashoffset: 125;
    transform: rotate(1080deg);
  }
}
```

---

## Lottie Animations

### 1. Setup Lottie in Odoo

**Install lottie-web**:

```bash
cd addons/ipai_animations
npm install lottie-web
```

**Add to manifest** (`__manifest__.py`):

```python
{
    "name": "IPAI Animations",
    "assets": {
        "web.assets_backend": [
            "ipai_animations/static/lib/lottie-web/lottie.min.js",
            "ipai_animations/static/src/js/lottie_component.js",
            "ipai_animations/static/src/xml/lottie_component.xml",
        ],
    },
}
```

### 2. Lottie OWL Component

**Component JS** (`static/src/js/lottie_component.js`):

```javascript
/** @odoo-module **/
import { Component, useRef, onMounted, onWillUnmount } from "@odoo/owl";

export class LottieAnimation extends Component {
  static template = "ipai.LottieAnimation";
  static props = {
    animationData: Object,
    loop: { type: Boolean, optional: true },
    autoplay: { type: Boolean, optional: true },
    speed: { type: Number, optional: true },
  };

  setup() {
    this.containerRef = useRef("lottie-container");
    this.animation = null;

    onMounted(() => {
      this.animation = lottie.loadAnimation({
        container: this.containerRef.el,
        renderer: "svg",
        loop: this.props.loop ?? true,
        autoplay: this.props.autoplay ?? true,
        animationData: this.props.animationData,
      });

      if (this.props.speed) {
        this.animation.setSpeed(this.props.speed);
      }
    });

    onWillUnmount(() => {
      if (this.animation) {
        this.animation.destroy();
      }
    });
  }

  play() {
    this.animation?.play();
  }

  pause() {
    this.animation?.pause();
  }

  stop() {
    this.animation?.stop();
  }
}
```

**Component Template** (`static/src/xml/lottie_component.xml`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="ipai.LottieAnimation" owl="1">
        <div class="lottie-animation" t-ref="lottie-container"/>
    </t>
</templates>
```

### 3. Using Lottie Animations

**Success Animation**:

```javascript
import { LottieAnimation } from "./lottie_component";
import successAnimation from "../animations/success.json";

export class SuccessMessage extends Component {
  static template = "ipai.SuccessMessage";
  static components = { LottieAnimation };

  get animationData() {
    return successAnimation;
  }
}
```

```xml
<t t-name="ipai.SuccessMessage" owl="1">
    <div class="success-message">
        <LottieAnimation
            animationData="animationData"
            loop="false"
            autoplay="true"/>
        <p>Operation completed successfully!</p>
    </div>
</t>
```

---

## GSAP (GreenSock) Integration

### 1. Setup GSAP

**Add GSAP via CDN** (in `web.layout` or asset bundle):

```xml
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
```

**Or install via npm**:

```bash
npm install gsap
```

### 2. GSAP in OWL Components

**Animated Card Component**:

```javascript
/** @odoo-module **/
import { Component, useRef, onMounted } from "@odoo/owl";
import { gsap } from "gsap";

export class AnimatedCard extends Component {
  static template = "ipai.AnimatedCard";

  setup() {
    this.cardRef = useRef("card");

    onMounted(() => {
      // Entrance animation
      gsap.from(this.cardRef.el, {
        y: 50,
        opacity: 0,
        duration: 0.6,
        ease: "power3.out",
      });
    });
  }

  handleHover(isEntering) {
    gsap.to(this.cardRef.el, {
      scale: isEntering ? 1.05 : 1,
      boxShadow: isEntering
        ? "0 10px 30px rgba(0,0,0,0.2)"
        : "0 2px 10px rgba(0,0,0,0.1)",
      duration: 0.3,
      ease: "power2.out",
    });
  }
}
```

```xml
<t t-name="ipai.AnimatedCard" owl="1">
    <div class="animated-card"
         t-ref="card"
         t-on-mouseenter="() => this.handleHover(true)"
         t-on-mouseleave="() => this.handleHover(false)">
        <t t-slot="default"/>
    </div>
</t>
```

### 3. Scroll-Triggered Animations

```javascript
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);

export class ScrollReveal extends Component {
  setup() {
    this.elementsRef = useRef("reveal-elements");

    onMounted(() => {
      const elements = this.elementsRef.el.querySelectorAll(".reveal-item");

      elements.forEach((el, index) => {
        gsap.from(el, {
          scrollTrigger: {
            trigger: el,
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
          y: 100,
          opacity: 0,
          duration: 0.8,
          delay: index * 0.1,
          ease: "power3.out",
        });
      });
    });
  }
}
```

### 4. Timeline Animations

**Complex Sequence**:

```javascript
onMounted(() => {
  const tl = gsap.timeline();

  tl.from(".header", { y: -100, opacity: 0, duration: 0.5 })
    .from(".content", { x: -50, opacity: 0, duration: 0.5 }, "-=0.2")
    .from(".sidebar", { x: 50, opacity: 0, duration: 0.5 }, "-=0.3")
    .from(".footer", { y: 100, opacity: 0, duration: 0.5 }, "-=0.2");
});
```

---

## Three.js 3D Graphics

### 1. Setup Three.js

**Install Three.js**:

```bash
npm install three
```

**Add to manifest**:

```python
{
    "assets": {
        "web.assets_backend": [
            "ipai_animations/static/lib/three/three.min.js",
            "ipai_animations/static/src/js/three_component.js",
        ],
    },
}
```

### 2. Three.js OWL Component

**3D Scene Component**:

```javascript
/** @odoo-module **/
import { Component, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import * as THREE from "three";

export class ThreeScene extends Component {
  static template = "ipai.ThreeScene";

  setup() {
    this.containerRef = useRef("three-container");
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.animationId = null;

    onMounted(() => {
      this.initScene();
      this.animate();
    });

    onWillUnmount(() => {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
      }
      if (this.renderer) {
        this.renderer.dispose();
      }
    });
  }

  initScene() {
    const container = this.containerRef.el;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf0f0f0);

    // Camera
    this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    this.camera.position.z = 5;

    // Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(width, height);
    container.appendChild(this.renderer.domElement);

    // Add objects
    this.addCube();
    this.addLights();
  }

  addCube() {
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const material = new THREE.MeshPhongMaterial({
      color: 0x714b67,
      shininess: 100,
    });
    this.cube = new THREE.Mesh(geometry, material);
    this.scene.add(this.cube);
  }

  addLights() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    this.scene.add(directionalLight);
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());

    // Rotate cube
    this.cube.rotation.x += 0.01;
    this.cube.rotation.y += 0.01;

    this.renderer.render(this.scene, this.camera);
  }
}
```

```xml
<t t-name="ipai.ThreeScene" owl="1">
    <div class="three-scene" t-ref="three-container"
         style="width: 100%; height: 400px;"/>
</t>
```

### 3. 3D Product Viewer

**Interactive Product Model**:

```javascript
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

export class ProductViewer extends Component {
  setup() {
    // ... scene setup

    onMounted(() => {
      this.initScene();
      this.loadModel();
      this.addControls();
    });
  }

  loadModel() {
    const loader = new GLTFLoader();
    loader.load("/path/to/product.gltf", (gltf) => {
      this.scene.add(gltf.scene);
    });
  }

  addControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
  }
}
```

---

## Avatar Motion & Character Animation

### 1. SVG Avatar with Expressions

**Animated Avatar Component**:

```xml
<t t-name="ipai.AnimatedAvatar" owl="1">
    <svg class="avatar" width="100" height="100" viewBox="0 0 100 100">
        <!-- Head -->
        <circle cx="50" cy="50" r="40" fill="#FFC857"/>

        <!-- Eyes -->
        <g class="eyes" t-att-class="state.expression">
            <ellipse cx="35" cy="45" rx="5" ry="8" fill="#000"/>
            <ellipse cx="65" cy="45" rx="5" ry="8" fill="#000"/>
        </g>

        <!-- Mouth -->
        <path class="mouth" t-att-class="state.expression"
              d="M 30,60 Q 50,70 70,60"
              fill="none" stroke="#000" stroke-width="2"/>
    </svg>
</t>
```

```javascript
export class AnimatedAvatar extends Component {
  setup() {
    this.state = useState({
      expression: "happy", // happy, sad, surprised, neutral
    });
  }

  setExpression(expression) {
    this.state.expression = expression;
  }
}
```

```css
.eyes.happy ellipse {
  transform: scaleY(1);
}
.eyes.sad ellipse {
  transform: scaleY(0.6);
}
.eyes.surprised ellipse {
  transform: scaleY(1.5);
}

.mouth.happy {
  d: path("M 30,60 Q 50,70 70,60");
}
.mouth.sad {
  d: path("M 30,70 Q 50,60 70,70");
}
.mouth.surprised {
  d: path("M 40,65 L 60,65");
}
```

### 2. Character Walk Cycle

**Sprite Sheet Animation**:

```javascript
export class WalkingCharacter extends Component {
  setup() {
    this.frameIndex = 0;
    this.totalFrames = 8;

    onMounted(() => {
      this.startWalking();
    });
  }

  startWalking() {
    setInterval(() => {
      this.frameIndex = (this.frameIndex + 1) % this.totalFrames;
      const offset = this.frameIndex * -100; // Frame width
      this.containerRef.el.style.backgroundPosition = `${offset}px 0`;
    }, 100);
  }
}
```

---

## Creative Content: Logos, Icons, Images

### 1. Dynamic Logo Generation

**Animated Logo Component**:

```xml
<t t-name="ipai.AnimatedLogo" owl="1">
    <svg class="logo" width="200" height="60" viewBox="0 0 200 60">
        <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#714B67"/>
                <stop offset="100%" style="stop-color:#FFC857"/>
            </linearGradient>
        </defs>

        <!-- Company name with animated letters -->
        <text class="logo-text" x="10" y="40"
              fill="url(#logoGradient)"
              font-size="36" font-weight="bold">
            <tspan class="letter" t-foreach="letters" t-as="letter" t-key="letter_index">
                <t t-esc="letter"/>
            </tspan>
        </text>
    </svg>
</t>
```

```css
.logo-text .letter {
  animation: letterPop 0.5s ease-out;
  animation-fill-mode: backwards;
}

.logo-text .letter:nth-child(1) {
  animation-delay: 0.1s;
}
.logo-text .letter:nth-child(2) {
  animation-delay: 0.2s;
}
.logo-text .letter:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes letterPop {
  0% {
    transform: translateY(20px);
    opacity: 0;
  }
  50% {
    transform: translateY(-5px);
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### 2. Icon System with Animations

**Icon Component**:

```javascript
export class AnimatedIcon extends Component {
  static template = "ipai.AnimatedIcon";
  static props = {
    name: String,
    size: { type: Number, optional: true },
    color: { type: String, optional: true },
    animate: { type: Boolean, optional: true },
  };

  get iconPath() {
    const icons = {
      check: "M5,12 L10,17 L20,7",
      close: "M6,6 L18,18 M18,6 L6,18",
      menu: "M4,8 L20,8 M4,16 L20,16",
      arrow: "M5,12 L19,12 M15,8 L19,12 L15,16",
    };
    return icons[this.props.name] || "";
  }
}
```

```xml
<t t-name="ipai.AnimatedIcon" owl="1">
    <svg t-att-width="props.size or 24"
         t-att-height="props.size or 24"
         viewBox="0 0 24 24"
         t-att-class="props.animate ? 'icon-animated' : ''">
        <path t-att-d="iconPath"
              fill="none"
              t-att-stroke="props.color or 'currentColor'"
              stroke-width="2"
              stroke-linecap="round"/>
    </svg>
</t>
```

### 3. Image Placeholders with Loading Animation

**Skeleton Loader**:

```xml
<t t-name="ipai.ImagePlaceholder" owl="1">
    <div class="image-placeholder">
        <svg width="100%" height="100%" viewBox="0 0 400 300">
            <rect class="skeleton-bg" width="400" height="300" fill="#e0e0e0"/>
            <rect class="skeleton-shine" width="400" height="300" fill="url(#shine)"/>

            <defs>
                <linearGradient id="shine">
                    <stop offset="0%" stop-color="#e0e0e0" stop-opacity="0"/>
                    <stop offset="50%" stop-color="#f5f5f5" stop-opacity="1"/>
                    <stop offset="100%" stop-color="#e0e0e0" stop-opacity="0"/>
                    <animateTransform
                        attributeName="gradientTransform"
                        type="translate"
                        from="-400 0"
                        to="400 0"
                        dur="1.5s"
                        repeatCount="indefinite"/>
                </linearGradient>
            </defs>
        </svg>
    </div>
</t>
```

---

## OWL Lifecycle Hooks for Animations

### Key Lifecycle Hooks

| Hook              | When                   | Use For                                  |
| ----------------- | ---------------------- | ---------------------------------------- |
| `setup()`         | Component construction | Initialize state, register hooks         |
| `onWillStart()`   | Before first render    | Load animation data, fetch assets        |
| `onMounted()`     | After DOM attachment   | **Start animations**, init libraries     |
| `onWillPatch()`   | Before DOM update      | Save animation state                     |
| `onPatched()`     | After DOM update       | Restart/update animations                |
| `onWillUnmount()` | Before removal         | **Cleanup animations**, remove listeners |

### Animation Lifecycle Pattern

```javascript
export class AnimatedComponent extends Component {
  setup() {
    this.elementRef = useRef("animated-element");
    this.animation = null;

    // Load animation data
    onWillStart(async () => {
      this.animationData = await this.loadAnimationData();
    });

    // Initialize animation after mount
    onMounted(() => {
      this.animation = gsap.from(this.elementRef.el, {
        opacity: 0,
        y: 50,
        duration: 0.6,
      });
    });

    // Update animation on state change
    onPatched(() => {
      if (this.animation) {
        this.animation.restart();
      }
    });

    // Cleanup
    onWillUnmount(() => {
      if (this.animation) {
        this.animation.kill();
      }
    });
  }
}
```

---

## Performance Optimization

### 1. SVG Optimization

**Best Practices**:

- Use SVGO to minify SVGs
- Remove unnecessary groups and attributes
- Use `viewBox` instead of fixed dimensions
- Optimize path data with precision limits

**SVGO Configuration**:

```json
{
  "plugins": [
    "removeDoctype",
    "removeXMLProcInst",
    "removeComments",
    "removeMetadata",
    "removeEditorsNSData",
    "cleanupAttrs",
    "mergeStyles",
    "inlineStyles",
    "minifyStyles",
    "cleanupIds",
    "removeUselessDefs",
    "cleanupNumericValues",
    "convertColors",
    "removeUnknownsAndDefaults",
    "removeNonInheritableGroupAttrs",
    "removeUselessStrokeAndFill",
    "removeViewBox",
    "cleanupEnableBackground",
    "removeHiddenElems",
    "removeEmptyText",
    "convertShapeToPath",
    "moveElemsAttrsToGroup",
    "moveGroupAttrsToElems",
    "collapseGroups",
    "convertPathData",
    "convertTransform",
    "removeEmptyAttrs",
    "removeEmptyContainers",
    "mergePaths",
    "removeUnusedNS",
    "sortAttrs",
    "removeTitle",
    "removeDesc"
  ]
}
```

### 2. Animation Performance

**Use Transform Properties**:

```css
/* ✅ GPU-accelerated */
transform: translateX(100px);
transform: scale(1.2);
transform: rotate(45deg);

/* ❌ Triggers layout */
left: 100px;
width: 200px;
```

**Will-Change Hint**:

```css
.animated-element {
  will-change: transform, opacity;
}

/* Remove after animation */
.animated-element.animation-complete {
  will-change: auto;
}
```

**Reduce Paint Area**:

```css
.container {
  contain: layout style paint;
}
```

### 3. Lazy Loading Animations

```javascript
export class LazyAnimation extends Component {
  setup() {
    this.isVisible = false;

    onMounted(() => {
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !this.isVisible) {
          this.isVisible = true;
          this.startAnimation();
          observer.disconnect();
        }
      });

      observer.observe(this.elementRef.el);
    });
  }
}
```

### 4. Debounce Scroll Animations

```javascript
import { debounce } from "@web/core/utils/timing";

setup() {
    this.handleScroll = debounce(() => {
        this.updateScrollAnimations();
    }, 100);

    onMounted(() => {
        window.addEventListener('scroll', this.handleScroll);
    });

    onWillUnmount(() => {
        window.removeEventListener('scroll', this.handleScroll);
    });
}
```

---

## Complete Examples

### Example 1: Animated Dashboard Widget

**Component**:

```javascript
/** @odoo-module **/
import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { gsap } from "gsap";

export class DashboardWidget extends Component {
  static template = "ipai.DashboardWidget";
  static props = {
    title: String,
    value: Number,
    icon: String,
    trend: { type: String, optional: true },
  };

  setup() {
    this.cardRef = useRef("card");
    this.valueRef = useRef("value");
    this.state = useState({
      displayValue: 0,
    });

    onMounted(() => {
      // Card entrance
      gsap.from(this.cardRef.el, {
        scale: 0.8,
        opacity: 0,
        duration: 0.5,
        ease: "back.out(1.7)",
      });

      // Counter animation
      gsap.to(this.state, {
        displayValue: this.props.value,
        duration: 1.5,
        ease: "power2.out",
        snap: { displayValue: 1 },
      });
    });
  }
}
```

**Template**:

```xml
<t t-name="ipai.DashboardWidget" owl="1">
    <div class="dashboard-widget" t-ref="card">
        <div class="widget-icon">
            <svg width="48" height="48">
                <use t-att-href="'#icon-' + props.icon"/>
            </svg>
        </div>
        <div class="widget-content">
            <h3 class="widget-title" t-esc="props.title"/>
            <div class="widget-value" t-ref="value">
                <span class="value-number" t-esc="Math.round(state.displayValue)"/>
                <span t-if="props.trend"
                      t-att-class="'trend trend-' + props.trend">
                    <t t-if="props.trend === 'up'">↑</t>
                    <t t-elif="props.trend === 'down'">↓</t>
                </span>
            </div>
        </div>
    </div>
</t>
```

### Example 2: Interactive Product Card

**Component with Lottie + GSAP**:

```javascript
import { LottieAnimation } from "./lottie_component";

export class ProductCard extends Component {
  static template = "ipai.ProductCard";
  static components = { LottieAnimation };
  static props = {
    product: Object,
  };

  setup() {
    this.cardRef = useRef("card");
    this.imageRef = useRef("image");
    this.state = useState({
      isHovered: false,
      showSuccess: false,
    });
  }

  handleMouseEnter() {
    this.state.isHovered = true;

    gsap.to(this.imageRef.el, {
      scale: 1.1,
      duration: 0.4,
      ease: "power2.out",
    });
  }

  handleMouseLeave() {
    this.state.isHovered = false;

    gsap.to(this.imageRef.el, {
      scale: 1,
      duration: 0.4,
      ease: "power2.out",
    });
  }

  async addToCart() {
    this.state.showSuccess = true;

    // Show success animation
    await new Promise((resolve) => setTimeout(resolve, 2000));
    this.state.showSuccess = false;
  }
}
```

**Template**:

```xml
<t t-name="ipai.ProductCard" owl="1">
    <div class="product-card"
         t-ref="card"
         t-on-mouseenter="handleMouseEnter"
         t-on-mouseleave="handleMouseLeave">

        <div class="product-image-container">
            <img t-ref="image"
                 t-att-src="props.product.image"
                 t-att-alt="props.product.name"/>

            <t t-if="state.showSuccess">
                <div class="success-overlay">
                    <LottieAnimation
                        animationData="successAnimationData"
                        loop="false"/>
                </div>
            </t>
        </div>

        <div class="product-info">
            <h3 t-esc="props.product.name"/>
            <p class="price" t-esc="props.product.price"/>
            <button class="btn-add-cart" t-on-click="addToCart">
                Add to Cart
            </button>
        </div>
    </div>
</t>
```

### Example 3: 3D Warehouse Visualization

**Three.js Warehouse Component**:

```javascript
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

export class WarehouseViewer extends Component {
  static template = "ipai.WarehouseViewer";

  setup() {
    this.containerRef = useRef("warehouse-container");

    onMounted(() => {
      this.initScene();
      this.loadWarehouseLayout();
      this.animate();
    });
  }

  loadWarehouseLayout() {
    // Create warehouse shelves
    const shelfGeometry = new THREE.BoxGeometry(2, 4, 0.5);
    const shelfMaterial = new THREE.MeshPhongMaterial({ color: 0x8b4513 });

    for (let i = 0; i < 10; i++) {
      const shelf = new THREE.Mesh(shelfGeometry, shelfMaterial);
      shelf.position.set(i * 3 - 15, 2, 0);
      this.scene.add(shelf);

      // Add stock indicators
      this.addStockIndicator(shelf, i);
    }
  }

  addStockIndicator(shelf, index) {
    const stockLevel = Math.random(); // 0-1
    const color =
      stockLevel > 0.7 ? 0x00ff00 : stockLevel > 0.3 ? 0xffff00 : 0xff0000;

    const indicator = new THREE.Mesh(
      new THREE.SphereGeometry(0.3),
      new THREE.MeshBasicMaterial({ color }),
    );
    indicator.position.copy(shelf.position);
    indicator.position.y += 2.5;
    this.scene.add(indicator);
  }
}
```

---

## Resources & Tools

### Animation Libraries

- **GSAP**: https://greensock.com/gsap/
- **Lottie**: https://airbnb.io/lottie/
- **Three.js**: https://threejs.org/
- **Anime.js**: https://animejs.com/

### Design Tools

- **After Effects**: Create Lottie animations
- **Figma**: Design SVG illustrations
- **Blender**: Create 3D models for Three.js
- **SVGOMG**: Optimize SVG files

### Odoo Resources

- **OWL Documentation**: https://github.com/odoo/owl
- **Odoo 19 Frontend Guide**: https://www.odoo.com/documentation/19.0/developer/reference/frontend.html

---

## Best Practices Summary

1. **Always cleanup animations** in `onWillUnmount()`
2. **Use GPU-accelerated properties** (transform, opacity)
3. **Optimize SVGs** before adding to project
4. **Lazy load animations** outside viewport
5. **Test performance** on low-end devices
6. **Keep animations subtle** (200-400ms for micro-interactions)
7. **Provide reduced motion** option for accessibility
8. **Use semantic HTML** with ARIA labels
9. **Cache animation data** to avoid re-parsing
10. **Monitor bundle size** when adding libraries

---

## Accessibility Considerations

**Respect `prefers-reduced-motion`**:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**JavaScript Detection**:

```javascript
const prefersReducedMotion = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

if (!prefersReducedMotion) {
  this.startAnimations();
}
```

---

This guide provides a complete foundation for implementing premium animations in Odoo 19. Start with simple SVG micro-interactions, then progressively enhance with Lottie, GSAP, and Three.js as needed.

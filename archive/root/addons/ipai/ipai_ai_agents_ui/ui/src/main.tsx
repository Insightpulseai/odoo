/**
 * IPAI AI Agents UI - Main Entry Point
 *
 * This file is the entry point for the React + Fluent UI bundle.
 * It exports a mount function that is called by the Odoo client action wrapper.
 */

import React from "react";
import { createRoot, Root } from "react-dom/client";
import { App } from "./app/App";

/**
 * Options passed from Odoo client action wrapper
 */
export interface MountOptions {
  rpcRouteBootstrap: string;
  rpcRouteAsk: string;
  rpcRouteFeedback: string;
}

let activeRoot: Root | null = null;

/**
 * Mount the React application into the specified container element.
 *
 * @param el - The container element to mount into
 * @param options - Configuration options from Odoo
 * @returns Unmount function
 */
function mount(el: HTMLElement, options: MountOptions): () => void {
  // Cleanup previous mount if exists
  if (activeRoot) {
    try {
      activeRoot.unmount();
    } catch (e) {
      console.warn("IPAI AI: Error unmounting previous root:", e);
    }
  }

  // Create new React root and render
  const root = createRoot(el);
  activeRoot = root;

  root.render(
    <React.StrictMode>
      <App options={options} />
    </React.StrictMode>
  );

  // Return unmount function
  return () => {
    if (activeRoot === root) {
      root.unmount();
      activeRoot = null;
    }
  };
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    IPAI_AI_UI: {
      mount: (el: HTMLElement, options: MountOptions) => () => void;
    };
  }
}

// Expose mount function globally for Odoo wrapper
window.IPAI_AI_UI = { mount };

export { mount };

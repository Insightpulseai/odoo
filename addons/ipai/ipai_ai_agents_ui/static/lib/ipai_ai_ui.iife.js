/**
 * IPAI AI Agents UI - React + Fluent UI Bundle (Placeholder)
 *
 * This is a placeholder file. The actual bundle should be built by running:
 *
 *   cd addons/ipai/ipai_ai_agents_ui/ui
 *   npm install
 *   npm run build
 *
 * The build process will generate the actual IIFE bundle and copy it here.
 */

(function() {
  'use strict';

  window.IPAI_AI_UI = {
    mount: function(el, options) {
      el.innerHTML = [
        '<div style="padding: 40px; text-align: center; font-family: system-ui, sans-serif;">',
        '  <h2 style="color: #0078d4;">IPAI AI Agents UI</h2>',
        '  <p style="color: #666;">React bundle not yet built.</p>',
        '  <p style="color: #999; font-size: 14px;">',
        '    Run <code>npm run build</code> in <code>addons/ipai/ipai_ai_agents_ui/ui/</code>',
        '  </p>',
        '</div>'
      ].join('\n');

      return function unmount() {
        el.innerHTML = '';
      };
    }
  };
})();

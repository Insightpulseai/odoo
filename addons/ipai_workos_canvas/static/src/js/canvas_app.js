/** @odoo-module **/

/**
 * Minimal OWL mount placeholder for Canvas.
 * v1 goal: prove assets load + mount point exists.
 * Canvas pan/zoom and node interactions come in next phase.
 */
import { registry } from "@web/core/registry";

function mountCanvasPlaceholder() {
    const roots = document.querySelectorAll(".ipai-workos-canvas-root");
    for (const el of roots) {
        // Skip if already mounted
        if (el.dataset.ipaiMounted) continue;
        el.dataset.ipaiMounted = "1";

        // Clear placeholder and inject canvas UI
        el.innerHTML = `
            <div class="ipai-canvas-container" style="
                width: 100%;
                height: 100%;
                min-height: 500px;
                position: relative;
                overflow: hidden;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 8px;
            ">
                <div class="ipai-canvas-toolbar" style="
                    position: absolute;
                    top: 16px;
                    left: 16px;
                    display: flex;
                    gap: 8px;
                    z-index: 10;
                ">
                    <button class="btn btn-sm btn-light" title="Pan">
                        <i class="fa fa-hand-paper-o"></i>
                    </button>
                    <button class="btn btn-sm btn-light" title="Select">
                        <i class="fa fa-mouse-pointer"></i>
                    </button>
                    <button class="btn btn-sm btn-light" title="Add Text">
                        <i class="fa fa-font"></i>
                    </button>
                    <button class="btn btn-sm btn-light" title="Add Shape">
                        <i class="fa fa-square-o"></i>
                    </button>
                </div>

                <div class="ipai-canvas-viewport" style="
                    position: absolute;
                    inset: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <div class="text-center text-muted">
                        <i class="fa fa-object-group fa-4x mb-3"></i>
                        <h4>WorkOS Canvas</h4>
                        <p>OWL component mounted successfully</p>
                        <p class="small">Next: pan/zoom + node placement</p>
                    </div>
                </div>

                <div class="ipai-canvas-zoom" style="
                    position: absolute;
                    bottom: 16px;
                    right: 16px;
                    display: flex;
                    gap: 4px;
                    z-index: 10;
                ">
                    <button class="btn btn-sm btn-light" title="Zoom Out">
                        <i class="fa fa-minus"></i>
                    </button>
                    <span class="btn btn-sm btn-light disabled">100%</span>
                    <button class="btn btn-sm btn-light" title="Zoom In">
                        <i class="fa fa-plus"></i>
                    </button>
                </div>
            </div>
        `;
    }
}

// Register as a service for auto-start
registry.category("services").add("ipai_workos_canvas_boot", {
    start() {
        // Initial mount
        mountCanvasPlaceholder();

        // Re-mount on SPA navigations (DOM mutations)
        const observer = new MutationObserver(() => {
            mountCanvasPlaceholder();
        });
        observer.observe(document.body, { childList: true, subtree: true });

        return {};
    },
});

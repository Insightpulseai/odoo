/** @odoo-module **/
/**
 * TBWA UI Animations
 * ===================
 * JavaScript enhancements for Framer-like micro-interactions.
 * These are optional progressive enhancements that add polish to the UI.
 */

import { registry } from "@web/core/registry";

/**
 * Intersection Observer for scroll-triggered animations
 * Elements with [data-tbwa-animate] will animate when they enter the viewport
 */
class TBWAAnimationObserver {
    constructor() {
        this.observer = null;
        this.init();
    }

    init() {
        // Check if IntersectionObserver is supported
        if (!('IntersectionObserver' in window)) {
            return;
        }

        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersection(entries),
            {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            }
        );

        // Observe dynamically added elements
        this.observeMutations();
    }

    handleIntersection(entries) {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const animationType = el.dataset.tbwaAnimate || 'fade-in-up';
                el.classList.add(`tbwa-animate-${animationType}`);
                this.observer.unobserve(el);
            }
        });
    }

    observeMutations() {
        const mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        this.observeElement(node);
                    }
                });
            });
        });

        mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    observeElement(el) {
        if (el.dataset && el.dataset.tbwaAnimate) {
            this.observer.observe(el);
        }
        // Also check children
        el.querySelectorAll && el.querySelectorAll('[data-tbwa-animate]').forEach((child) => {
            this.observer.observe(child);
        });
    }
}

/**
 * Button ripple effect (Material Design inspired)
 */
class TBWAButtonRipple {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.btn');
            if (button) {
                this.createRipple(button, e);
            }
        });
    }

    createRipple(button, event) {
        // Check if ripples are enabled
        if (button.classList.contains('no-ripple')) return;

        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: tbwa-ripple 0.6s ease-out;
            pointer-events: none;
        `;

        // Ensure button has relative positioning
        const originalPosition = button.style.position;
        button.style.position = 'relative';
        button.style.overflow = 'hidden';

        button.appendChild(ripple);

        // Cleanup
        setTimeout(() => {
            ripple.remove();
            if (!originalPosition) {
                button.style.position = '';
            }
        }, 600);
    }
}

/**
 * Smooth scroll enhancement
 */
class TBWASmoothScroll {
    constructor() {
        this.init();
    }

    init() {
        // Add smooth scrolling to internal links
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (link) {
                const targetId = link.getAttribute('href').slice(1);
                const target = document.getElementById(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    }
}

/**
 * Focus trap for modals (accessibility)
 */
class TBWAFocusTrap {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    this.trapFocus(modal, e);
                }
            }
        });
    }

    trapFocus(modal, event) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey && document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
        } else if (!event.shiftKey && document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
        }
    }
}

/**
 * Initialize all TBWA UI enhancements
 */
function initTBWAUI() {
    // Add ripple keyframe animation dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes tbwa-ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Initialize modules
    new TBWAAnimationObserver();
    new TBWAButtonRipple();
    new TBWASmoothScroll();
    new TBWAFocusTrap();

    console.log('[TBWA Theme] UI animations initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTBWAUI);
} else {
    initTBWAUI();
}

// Export for potential OWL component integration
export { TBWAAnimationObserver, TBWAButtonRipple, TBWASmoothScroll, TBWAFocusTrap };

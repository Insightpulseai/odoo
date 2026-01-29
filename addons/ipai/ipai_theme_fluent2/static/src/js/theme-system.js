/** @odoo-module **/
/**
 * InsightPulse AI Theme System Manager for Odoo
 * 5 Aesthetic Systems × 2 Color Modes = 10 Themes
 */

import { registry } from "@web/core/registry";

const AESTHETICS = ['default', 'dull', 'claude', 'chatgpt', 'gemini'];
const COLOR_MODES = ['light', 'dark'];

class ThemeSystemManager {
    constructor() {
        this.aesthetic = this.getStoredAesthetic();
        this.colorMode = this.getStoredColorMode();
        this.init();
    }

    init() {
        // Apply theme on page load
        this.applyTheme();

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('ipai-color-mode')) {
                    this.colorMode = e.matches ? 'dark' : 'light';
                    this.applyTheme();
                }
            });
        }

        // Add theme switcher to navbar
        this.addThemeSwitcher();
    }

    getStoredAesthetic() {
        const stored = localStorage.getItem('ipai-aesthetic');
        return AESTHETICS.includes(stored) ? stored : 'default';
    }

    getStoredColorMode() {
        const stored = localStorage.getItem('ipai-color-mode');
        if (stored && COLOR_MODES.includes(stored)) {
            return stored;
        }

        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        return 'light';
    }

    setTheme(aesthetic, colorMode) {
        if (!AESTHETICS.includes(aesthetic) || !COLOR_MODES.includes(colorMode)) {
            console.error('Invalid theme values:', aesthetic, colorMode);
            return;
        }

        this.aesthetic = aesthetic;
        this.colorMode = colorMode;

        localStorage.setItem('ipai-aesthetic', aesthetic);
        localStorage.setItem('ipai-color-mode', colorMode);

        this.applyTheme();
    }

    applyTheme() {
        const html = document.documentElement;
        html.setAttribute('data-aesthetic', this.aesthetic);
        html.setAttribute('data-color-mode', this.colorMode);

        // Dispatch custom event for other modules
        const event = new CustomEvent('ipai-theme-changed', {
            detail: {
                aesthetic: this.aesthetic,
                colorMode: this.colorMode,
                themeMode: `${this.aesthetic}-${this.colorMode}`
            }
        });
        document.dispatchEvent(event);
    }

    toggleColorMode() {
        this.colorMode = this.colorMode === 'light' ? 'dark' : 'light';
        localStorage.setItem('ipai-color-mode', this.colorMode);
        this.applyTheme();
    }

    addThemeSwitcher() {
        // Wait for navbar to be available
        const checkNavbar = setInterval(() => {
            const navbar = document.querySelector('.o_main_navbar .o_menu_systray');
            if (navbar) {
                clearInterval(checkNavbar);
                this.createThemeSwitcher(navbar);
            }
        }, 500);

        // Stop checking after 10 seconds
        setTimeout(() => clearInterval(checkNavbar), 10000);
    }

    createThemeSwitcher(navbar) {
        const aestheticOptions = [
            { value: 'default', label: 'Default', emoji: '🎨' },
            { value: 'dull', label: 'Dull', emoji: '🌫️' },
            { value: 'claude', label: 'Claude', emoji: '📜' },
            { value: 'chatgpt', label: 'ChatGPT', emoji: '💬' },
            { value: 'gemini', label: 'Gemini', emoji: '✨' },
        ];

        // Create container
        const container = document.createElement('div');
        container.className = 'o_theme_switcher';
        container.style.cssText = 'display: flex; align-items: center; gap: 8px; padding: 0 16px;';

        // Aesthetic selector
        const aestheticSelect = document.createElement('select');
        aestheticSelect.className = 'form-select form-select-sm';
        aestheticSelect.style.cssText = 'width: 140px; font-size: 13px;';
        aestheticSelect.title = 'Choose aesthetic system';

        aestheticOptions.forEach(opt => {
            const option = document.createElement('option');
            option.value = opt.value;
            option.textContent = `${opt.emoji} ${opt.label}`;
            if (opt.value === this.aesthetic) {
                option.selected = true;
            }
            aestheticSelect.appendChild(option);
        });

        aestheticSelect.addEventListener('change', (e) => {
            this.setTheme(e.target.value, this.colorMode);
        });

        // Color mode toggle button
        const modeButton = document.createElement('button');
        modeButton.className = 'btn btn-sm btn-secondary';
        modeButton.style.cssText = 'display: flex; align-items: center; gap: 4px; font-size: 13px;';
        modeButton.title = `Switch to ${this.colorMode === 'light' ? 'dark' : 'light'} mode`;

        const updateModeButton = () => {
            const icon = this.colorMode === 'light' ? '🌙' : '☀️';
            const text = this.colorMode.charAt(0).toUpperCase() + this.colorMode.slice(1);
            modeButton.innerHTML = `${icon} <span>${text}</span>`;
            modeButton.title = `Switch to ${this.colorMode === 'light' ? 'dark' : 'light'} mode`;
        };

        updateModeButton();

        modeButton.addEventListener('click', () => {
            this.toggleColorMode();
            updateModeButton();
        });

        // Add to container
        container.appendChild(aestheticSelect);
        container.appendChild(modeButton);

        // Insert into navbar (before other systray items)
        if (navbar.firstChild) {
            navbar.insertBefore(container, navbar.firstChild);
        } else {
            navbar.appendChild(container);
        }
    }

    // Public API
    getCurrentTheme() {
        return {
            aesthetic: this.aesthetic,
            colorMode: this.colorMode,
            themeMode: `${this.aesthetic}-${this.colorMode}`
        };
    }

    getAvailableAesthetics() {
        return AESTHETICS;
    }

    getAvailableColorModes() {
        return COLOR_MODES;
    }
}

// Initialize theme system when Odoo loads
registry.category("services").add("ipai_theme_system", {
    dependencies: [],
    start() {
        const themeManager = new ThemeSystemManager();

        // Expose globally for console access
        window.IpaiThemeSystem = themeManager;

        return {
            setTheme: themeManager.setTheme.bind(themeManager),
            toggleColorMode: themeManager.toggleColorMode.bind(themeManager),
            getCurrentTheme: themeManager.getCurrentTheme.bind(themeManager),
            getAvailableAesthetics: themeManager.getAvailableAesthetics.bind(themeManager),
            getAvailableColorModes: themeManager.getAvailableColorModes.bind(themeManager),
        };
    },
});

// Also initialize on DOMContentLoaded as fallback
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.IpaiThemeSystem) {
            window.IpaiThemeSystem = new ThemeSystemManager();
        }
    });
} else {
    if (!window.IpaiThemeSystem) {
        window.IpaiThemeSystem = new ThemeSystemManager();
    }
}

export default ThemeSystemManager;

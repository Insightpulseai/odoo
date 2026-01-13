/**
 * Fluent 2 Theme Manager for Odoo 18 CE
 *
 * Handles dark/light mode switching with system preference detection
 * and localStorage persistence.
 *
 * Usage:
 *   ThemeManager.initTheme();       // Initialize on page load
 *   ThemeManager.toggleTheme();     // Toggle between light/dark
 *   ThemeManager.applyTheme('dark'); // Set specific theme
 */
(function () {
    'use strict';

    const THEME_KEY = 'ipai_fluent_theme';
    const DARK_CLASS = 'dark';

    /**
     * Get the user's system color scheme preference
     * @returns {'light' | 'dark'}
     */
    function getSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    /**
     * Get the saved theme from localStorage or fall back to system preference
     * @returns {'light' | 'dark'}
     */
    function getSavedTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved === 'dark' || saved === 'light') {
            return saved;
        }
        return getSystemPreference();
    }

    /**
     * Apply a theme to the document
     * @param {'light' | 'dark'} theme
     */
    function applyTheme(theme) {
        const html = document.documentElement;
        const body = document.body;
        const webClient = document.querySelector('.o_web_client');

        if (theme === 'dark') {
            html.classList.add(DARK_CLASS);
            html.setAttribute('data-theme', 'dark');
            if (body) body.classList.add(DARK_CLASS);
            if (webClient) webClient.classList.add(DARK_CLASS);
        } else {
            html.classList.remove(DARK_CLASS);
            html.setAttribute('data-theme', 'light');
            if (body) body.classList.remove(DARK_CLASS);
            if (webClient) webClient.classList.remove(DARK_CLASS);
        }

        localStorage.setItem(THEME_KEY, theme);

        // Dispatch custom event for other components to react
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
    }

    /**
     * Toggle between light and dark themes
     * @returns {'light' | 'dark'} The new theme
     */
    function toggleTheme() {
        const current = getSavedTheme();
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
        return next;
    }

    /**
     * Initialize theme on page load
     */
    function initTheme() {
        const theme = getSavedTheme();
        applyTheme(theme);

        // Listen for system preference changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', function (e) {
                // Only auto-switch if user hasn't set a preference
                if (!localStorage.getItem(THEME_KEY)) {
                    applyTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
    }

    /**
     * Get the current theme
     * @returns {'light' | 'dark'}
     */
    function getCurrentTheme() {
        return getSavedTheme();
    }

    /**
     * Clear saved theme preference and use system preference
     */
    function clearPreference() {
        localStorage.removeItem(THEME_KEY);
        applyTheme(getSystemPreference());
    }

    // Export the ThemeManager
    window.IpaiThemeManager = {
        initTheme,
        applyTheme,
        toggleTheme,
        getCurrentTheme,
        clearPreference,
        getSystemPreference
    };

    // Also export as ThemeManager for backwards compatibility
    window.ThemeManager = window.IpaiThemeManager;

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        // DOM already loaded
        initTheme();
    }
})();

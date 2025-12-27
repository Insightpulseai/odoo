/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * IPAI Custom Home Page Component
 * Renders an app grid similar to Odoo's default home page but with custom styling
 *
 * Includes defensive checks for service availability to prevent
 * "Cannot read properties of undefined" errors.
 */
export class IpaiHomePage extends Component {
    static template = "ipai_default_home.HomePage";
    static props = {};

    setup() {
        // Safely inject services with fallback checks
        try {
            this.action = useService("action");
        } catch (e) {
            console.warn("[IpaiHomePage] Action service not available:", e);
            this.action = null;
        }

        try {
            this.menuService = useService("menu");
        } catch (e) {
            console.warn("[IpaiHomePage] Menu service not available:", e);
            this.menuService = null;
        }

        this.state = useState({
            apps: [],
            favorites: [],
            filteredApps: [],
            searchQuery: "",
            isLoading: true,
            showSearch: false,
            contextMenu: null,
            error: null,
        });

        onWillStart(async () => {
            await this.loadApps();
        });

        onMounted(() => {
            this.setupKeyboardShortcuts();
        });
    }

    /**
     * Wait for menu service to be ready
     */
    async waitForMenuService(maxRetries = 5, delay = 500) {
        for (let i = 0; i < maxRetries; i++) {
            if (this.menuService && typeof this.menuService.getApps === "function") {
                return true;
            }
            await new Promise(resolve => setTimeout(resolve, delay));
        }
        return false;
    }

    async loadApps() {
        try {
            // Wait for menu service if not immediately available
            if (!this.menuService) {
                const ready = await this.waitForMenuService();
                if (!ready) {
                    console.error("[IpaiHomePage] Menu service not available after retries");
                    this.state.error = "Unable to load app menu. Please refresh the page.";
                    this.state.isLoading = false;
                    return;
                }
            }

            // Get menus from menu service (official Odoo way)
            const menus = this.menuService.getApps();

            if (!menus || !Array.isArray(menus)) {
                console.warn("[IpaiHomePage] No menus returned from menu service");
                this.state.apps = [];
                this.state.filteredApps = [];
                this.state.isLoading = false;
                return;
            }

            this.state.apps = menus.map((menu, index) => {
                const appId = menu.xmlid || String(menu.id);
                return {
                    id: appId,
                    name: menu.name,
                    actionId: menu.actionID,
                    menuId: menu.id,
                    // Priority: webIconData (base64) > webIcon > module icon.svg > fallback
                    icon: menu.webIconData || menu.webIcon || this.getFallbackIcon(appId),
                    color: this.getAppColor(appId),
                    unread: 0,
                    sequence: index,
                };
            });

            this.state.filteredApps = [...this.state.apps];
            this.state.isLoading = false;
            this.state.error = null;
        } catch (error) {
            console.error("[IpaiHomePage] Failed to load apps:", error);
            this.state.error = `Error loading apps: ${error.message}`;
            this.state.isLoading = false;
        }
    }

    /**
     * Get app color based on xmlid - using official Odoo brand colors
     * Reference: https://github.com/odoo/odoo/tree/18.0/addons/*/static/description/icon.svg
     */
    getAppColor(appId) {
        const colorMap = {
            // Official Odoo App Colors (from SVG analysis)
            'mail.menu_root_discuss': '#F86126',      // Orange (Discuss)
            'project.menu_main_pm': '#9B59B6',        // Purple (Project)
            'account.menu_finance': '#2EBCFA',        // Cyan (Invoicing)
            'hr.menu_hr_root': '#985184',             // Purple (Employees)
            'hr_expense.menu_hr_expense_root': '#2EBCFA', // Cyan (Expenses)
            'sale.sale_menu_root': '#985184',         // Purple (Sales)
            'purchase.menu_purchase_root': '#714B67', // Odoo Purple (Purchase)
            'stock.menu_stock_root': '#3498DB',       // Blue (Inventory)
            'crm.crm_menu_root': '#985184',           // Purple (CRM)
            'website.menu_website_configuration': '#E91E63', // Pink (Website)
            'spreadsheet_dashboard.menu_dashboard': '#985184', // Purple (Dashboards)
            'base_setup.menu_configuration': '#FBB945', // Yellow (Settings)
            'base.menu_management': '#1AD3BB',        // Teal (Apps)
            'contacts.menu_contacts': '#1AD3BB',      // Teal (Contacts)
            'calendar.mail_menu_calendar': '#F86126', // Orange (Calendar)
            'mrp.menu_mrp_root': '#088BF5',           // Blue (Manufacturing)
            'point_of_sale.menu_point_root': '#03AF89', // Green (POS)
            'fleet.menu_fleet_root': '#FBB945',       // Yellow (Fleet)
            'lunch.menu_lunch': '#FC868B',            // Pink (Lunch)
            'survey.menu_surveys': '#144496',         // Navy (Survey)
            'event.menu_event': '#F9464C',            // Red (Events)
            'helpdesk.menu_helpdesk_root': '#1AD3BB', // Teal (Helpdesk)
            'maintenance.menu_m_main': '#FBB945',     // Yellow (Maintenance)
            'hr_recruitment.menu_hr_recruitment_root': '#985184', // Purple (Recruitment)
        };
        return colorMap[appId] || '#714B67';
    }

    /**
     * Get fallback icon path based on app xmlid
     */
    getFallbackIcon(appId) {
        // Extract module name from xmlid (e.g., 'mail.menu_root_discuss' -> 'mail')
        const moduleName = appId ? appId.split('.')[0] : null;

        // Map common modules to their icon paths
        const iconPaths = {
            'mail': '/mail/static/description/icon.svg',
            'account': '/account/static/description/icon.svg',
            'hr': '/hr/static/description/icon.svg',
            'hr_expense': '/hr_expense/static/description/icon.svg',
            'sale': '/sale/static/description/icon.svg',
            'purchase': '/purchase/static/description/icon.svg',
            'stock': '/stock/static/description/icon.svg',
            'crm': '/crm/static/description/icon.svg',
            'project': '/project/static/description/icon.svg',
            'website': '/website/static/description/icon.svg',
            'spreadsheet_dashboard': '/spreadsheet_dashboard/static/description/icon.svg',
            'base_setup': '/base_setup/static/description/icon.svg',
            'calendar': '/calendar/static/description/icon.svg',
            'contacts': '/contacts/static/description/icon.svg',
            'mrp': '/mrp/static/description/icon.svg',
            'point_of_sale': '/point_of_sale/static/description/icon.svg',
        };

        return iconPaths[moduleName] || '/base/static/description/icon.svg';
    }

    onAppClick(app) {
        if (app.actionId) {
            this.action.doAction(app.actionId);
        } else if (app.menuId) {
            this.menuService.selectMenu(app.menuId);
        }
    }

    onAppContextMenu(event, app) {
        event.preventDefault();
        this.state.contextMenu = {
            x: event.clientX,
            y: event.clientY,
            app: app,
        };

        // Close on click outside
        const closeHandler = () => {
            this.state.contextMenu = null;
            document.removeEventListener('click', closeHandler);
        };
        setTimeout(() => {
            document.addEventListener('click', closeHandler);
        }, 0);
    }

    onContextMenuOpen(app) {
        this.onAppClick(app);
        this.state.contextMenu = null;
    }

    onContextMenuNewWindow(app) {
        if (app.actionId) {
            window.open(`/web#action=${app.actionId}`, '_blank');
        }
        this.state.contextMenu = null;
    }

    onContextMenuFavorite(app) {
        // Toggle favorite in local state (simplified - no backend call)
        if (this.state.favorites.includes(app.id)) {
            this.state.favorites = this.state.favorites.filter(id => id !== app.id);
        } else {
            this.state.favorites = [...this.state.favorites, app.id];
        }
        this.state.contextMenu = null;
    }

    toggleSearch() {
        this.state.showSearch = !this.state.showSearch;
        if (this.state.showSearch) {
            setTimeout(() => {
                const input = document.querySelector('.ipai-search-input');
                if (input) input.focus();
            }, 100);
        } else {
            this.state.searchQuery = "";
            this.state.filteredApps = [...this.state.apps];
        }
    }

    onSearchInput(event) {
        const query = event.target.value.toLowerCase();
        this.state.searchQuery = query;

        if (!query) {
            this.state.filteredApps = [...this.state.apps];
        } else {
            this.state.filteredApps = this.state.apps.filter(app =>
                app.name.toLowerCase().includes(query)
            );
        }
    }

    onSearchResultClick(app) {
        this.onAppClick(app);
        this.toggleSearch();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.toggleSearch();
            }
            // Escape to close search
            if (e.key === 'Escape' && this.state.showSearch) {
                this.toggleSearch();
            }
        });
    }

    isFavorite(app) {
        return this.state.favorites.includes(app.id);
    }
}

// Register as a client action
registry.category("actions").add("ipai_home_page", {
    Component: IpaiHomePage,
});

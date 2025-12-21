/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("omc_finance_ppm_tour", {
    url: "/web",
    sequence: 10,
    steps: () => [
        {
            trigger: 'a[data-menu-xmlid="project.menu_main_pm"]',
            content: "Let's explore the Finance PPM features. Click on the Project menu.",
            position: "bottom",
        },
        {
            trigger: 'a[data-menu-xmlid="omc_finance_ppm.menu_omc_clarity_dashboard"]',
            content: "Open the Clarity PPM Dashboard to view phase progress and to-do completion.",
            position: "bottom",
        },
        {
            trigger: '.btn-primary:contains("Refresh Data")',
            content: "Click here to refresh the dashboard data at any time.",
            position: "left",
        },
        {
            trigger: '#echarts_main',
            content: "This ECharts visualization shows Phase progress with total to-dos, completed to-dos, and completion percentage.",
            position: "top",
        },
        {
            trigger: 'a[data-menu-xmlid="project.menu_projects"]',
            content: "Navigate to Projects to see the Month-End Closing & Tax Filing project.",
            position: "bottom",
        },
        {
            trigger: '.o_kanban_record:contains("Month-End Closing")',
            content: "Click on the Month-End Closing project to view phases and tasks.",
            position: "right",
        },
        {
            trigger: 'button.o_kanban_button_new',
            content: "You can create new tasks here. Each task can have multiple to-do items.",
            position: "bottom",
        },
        {
            trigger: '.o_kanban_record:first',
            content: "Click on any task to open its detail form.",
            position: "right",
        },
        {
            trigger: 'a[name="clarity_todos"]',
            content: "Switch to the 'To-Do Items (Clarity)' tab to manage granular checklist items.",
            position: "bottom",
        },
        {
            trigger: '.o_field_x2many_list_row_add a',
            content: "Add to-do items here. Each item can be assigned to a user and marked as done.",
            position: "top",
        },
        {
            trigger: 'button:contains("Complete All To-Dos")',
            content: "Use this button to mark all to-dos for this task as complete at once.",
            position: "left",
        },
        {
            trigger: 'field[name="x_is_phase"]',
            content: "Toggle this field to mark a task as a Phase (used for dashboard grouping).",
            position: "right",
        },
        {
            trigger: 'a[data-menu-xmlid="project.menu_project_config"]',
            content: "Congratulations! You've completed the Finance PPM tour. Explore configuration options here.",
            position: "bottom",
        },
    ],
});

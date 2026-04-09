# -*- coding: utf-8 -*-

import odoo.tests


def unit_test_error_checker(message):
    return '[HOOT]' not in message


@odoo.tests.tagged('post_install', '-at_install')
class TestCopilotJS(odoo.tests.HttpCase):
    """Run HOOT JS tests for ipai_odoo_copilot via Chrome headless."""

    @odoo.tests.no_retry
    def test_copilot_systray_js(self):
        self.browser_js(
            '/web/tests?headless&loglevel=2&preset=desktop'
            '&timeout=30000&filter=CopilotSystrayButton',
            "",
            "",
            login='admin',
            timeout=120,
            success_signal="[HOOT] Test suite succeeded",
            error_checker=unit_test_error_checker,
        )

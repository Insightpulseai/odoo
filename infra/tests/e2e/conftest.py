"""
Playwright E2E Test Configuration

Shared fixtures and utilities for Odoo 19 E2E testing.

Reference: docs/integrations/ODOO_AI_TESTING_AUTOMATION.md
"""

import pytest
import os
from playwright.sync_api import sync_playwright, Browser, Page, expect
from typing import Generator


# Test configuration from environment
ODOO_BASE_URL = os.getenv('ODOO_BASE_URL', 'https://erp.insightpulseai.com')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'admin')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'admin')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
SLOW_MO = int(os.getenv('SLOW_MO', '0'))
SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
TRACE_ON_FAILURE = os.getenv('TRACE_ON_FAILURE', 'true').lower() == 'true'


@pytest.fixture(scope='session')
def browser() -> Generator[Browser, None, None]:
    """
    Shared browser instance for the test session.

    Yields:
        Browser: Playwright browser instance
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )
        yield browser
        browser.close()


@pytest.fixture(scope='function')
def page(browser: Browser) -> Generator[Page, None, None]:
    """
    New browser page for each test.

    Args:
        browser: Shared browser instance

    Yields:
        Page: Playwright page instance
    """
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='en-US',
        timezone_id='Asia/Manila',
        record_video_dir='test-results/videos' if TRACE_ON_FAILURE else None,
    )

    # Start tracing for debugging
    if TRACE_ON_FAILURE:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()

    yield page

    # Capture screenshot on failure
    if SCREENSHOT_ON_FAILURE:
        try:
            page.screenshot(path='test-results/screenshots/failure.png')
        except Exception:
            pass

    # Stop tracing and save if test failed
    if TRACE_ON_FAILURE:
        try:
            context.tracing.stop(path='test-results/traces/trace.zip')
        except Exception:
            pass

    context.close()


@pytest.fixture(scope='function')
def authenticated_page(page: Page) -> Page:
    """
    Authenticated Odoo session.

    Args:
        page: Playwright page instance

    Returns:
        Page: Authenticated page instance
    """
    # Navigate to login page
    page.goto(f'{ODOO_BASE_URL}/web/login')

    # Fill login form
    page.fill('input[name="login"]', ODOO_USERNAME)
    page.fill('input[name="password"]', ODOO_PASSWORD)

    # Click login button
    page.click('button[type="submit"]')

    # Wait for dashboard to load
    page.wait_for_url(f'{ODOO_BASE_URL}/web', timeout=15000)

    # Verify successful login
    expect(page).to_have_url(f'{ODOO_BASE_URL}/web')

    return page


@pytest.fixture(scope='function')
def odoo_api_context(page: Page):
    """
    Odoo API context for making JSON-RPC calls.

    Args:
        page: Playwright page instance

    Returns:
        dict: API context with session info
    """
    # Login first
    page.goto(f'{ODOO_BASE_URL}/web/login')
    page.fill('input[name="login"]', ODOO_USERNAME)
    page.fill('input[name="password"]', ODOO_PASSWORD)
    page.click('button[type="submit"]')
    page.wait_for_url(f'{ODOO_BASE_URL}/web', timeout=15000)

    # Extract session info from cookies
    cookies = page.context.cookies()
    session_id = None
    for cookie in cookies:
        if cookie['name'] == 'session_id':
            session_id = cookie['value']
            break

    return {
        'base_url': ODOO_BASE_URL,
        'session_id': session_id,
        'cookies': cookies
    }


# Helper functions

def wait_for_odoo_ready(page: Page, timeout: int = 30000) -> None:
    """
    Wait for Odoo web client to be fully loaded.

    Args:
        page: Playwright page instance
        timeout: Maximum wait time in milliseconds
    """
    page.wait_for_selector('.o_web_client', timeout=timeout)
    page.wait_for_load_state('networkidle', timeout=timeout)


def navigate_to_module(page: Page, menu_name: str) -> None:
    """
    Navigate to an Odoo module via menu.

    Args:
        page: Playwright page instance
        menu_name: Name of the menu item to click
    """
    page.click(f'text={menu_name}')
    wait_for_odoo_ready(page)


def create_record(page: Page, form_data: dict) -> None:
    """
    Create a new record in Odoo.

    Args:
        page: Playwright page instance
        form_data: Dictionary of field names and values
    """
    # Click Create button
    page.click('button:has-text("Create")')

    # Fill form fields
    for field_name, value in form_data.items():
        selector = f'input[name="{field_name}"], textarea[name="{field_name}"]'
        page.fill(selector, str(value))

    # Save record
    page.click('button:has-text("Save")')

    # Wait for save to complete
    page.wait_for_selector('.o_notification_title:has-text("Success")', timeout=5000)


def search_record(page: Page, search_term: str) -> None:
    """
    Search for records in Odoo list view.

    Args:
        page: Playwright page instance
        search_term: Search query
    """
    page.fill('.o_searchview_input input', search_term)
    page.press('.o_searchview_input input', 'Enter')
    wait_for_odoo_ready(page)


def verify_notification(page: Page, message_text: str, notification_type: str = 'Success') -> None:
    """
    Verify an Odoo notification appears.

    Args:
        page: Playwright page instance
        message_text: Expected message text
        notification_type: Type of notification (Success, Warning, Error)
    """
    selector = f'.o_notification_title:has-text("{notification_type}")'
    expect(page.locator(selector)).to_be_visible()

    if message_text:
        message_selector = f'.o_notification_content:has-text("{message_text}")'
        expect(page.locator(message_selector)).to_be_visible()


# Pytest configuration

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "smoke: marks tests as smoke tests")


def pytest_collection_modifyitems(config, items):
    """Auto-mark E2E tests."""
    for item in items:
        if 'e2e' in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

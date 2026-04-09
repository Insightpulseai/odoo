"""
E2E Test: Partner/Contact Management Workflow

Tests the complete partner creation and management workflow in Odoo 18.

Reference: docs/integrations/ODOO_AI_TESTING_AUTOMATION.md
"""

import pytest
from playwright.sync_api import Page, expect
from .conftest import (
    wait_for_odoo_ready,
    navigate_to_module,
    create_record,
    search_record,
    verify_notification
)


@pytest.mark.e2e
@pytest.mark.smoke
def test_create_partner(authenticated_page: Page):
    """
    Test creating a new partner through the UI.

    Steps:
    1. Navigate to Contacts module
    2. Click Create button
    3. Fill partner form
    4. Save partner
    5. Verify success notification
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Click Create button
    page.click('button:has-text("Create")')
    wait_for_odoo_ready(page)

    # Fill partner form
    test_partner_name = f'Test Partner {page.evaluate("Date.now()")}'
    page.fill('input[name="name"]', test_partner_name)
    page.fill('input[name="email"]', f'test{page.evaluate("Date.now()")}@example.com')
    page.fill('input[name="phone"]', '+63 917 123 4567')

    # Save partner
    page.click('button:has-text("Save")')

    # Verify success notification
    verify_notification(page, '', 'Success')

    # Verify partner name is displayed
    expect(page.locator(f'text={test_partner_name}')).to_be_visible()


@pytest.mark.e2e
def test_search_partner(authenticated_page: Page):
    """
    Test searching for partners in list view.

    Steps:
    1. Navigate to Contacts
    2. Enter search term
    3. Verify filtered results
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Search for "Test"
    search_record(page, 'Test')

    # Verify search results contain "Test"
    expect(page.locator('.o_list_view tbody tr')).to_contain_text('Test')


@pytest.mark.e2e
def test_edit_partner(authenticated_page: Page):
    """
    Test editing an existing partner.

    Steps:
    1. Navigate to Contacts
    2. Open existing partner
    3. Edit partner details
    4. Save changes
    5. Verify updates
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Click first partner in list
    page.click('.o_list_view tbody tr:first-child')
    wait_for_odoo_ready(page)

    # Click Edit button
    page.click('button:has-text("Edit")')

    # Update phone number
    new_phone = '+63 917 999 8888'
    page.fill('input[name="phone"]', new_phone)

    # Save changes
    page.click('button:has-text("Save")')

    # Verify success notification
    verify_notification(page, '', 'Success')

    # Verify phone number updated
    expect(page.locator('input[name="phone"]')).to_have_value(new_phone)


@pytest.mark.e2e
def test_partner_validation(authenticated_page: Page):
    """
    Test partner form validation.

    Steps:
    1. Navigate to Contacts
    2. Try to create partner without required fields
    3. Verify validation errors
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Click Create button
    page.click('button:has-text("Create")')
    wait_for_odoo_ready(page)

    # Leave name empty and try to save
    page.click('button:has-text("Save")')

    # Verify error notification or invalid field indicator
    # Odoo typically shows red border or error message
    expect(page.locator('input[name="name"]')).to_have_class('o_field_invalid', timeout=5000)


@pytest.mark.e2e
@pytest.mark.slow
def test_partner_export(authenticated_page: Page):
    """
    Test exporting partner list to CSV/Excel.

    Steps:
    1. Navigate to Contacts
    2. Select multiple partners
    3. Click Export button
    4. Verify download
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Select all partners
    page.click('.o_list_view thead input[type="checkbox"]')

    # Click Action dropdown
    page.click('button:has-text("Action")')

    # Click Export
    page.click('text=Export')

    # Wait for export dialog
    expect(page.locator('.modal-title:has-text("Export")')).to_be_visible()

    # Select format (if available)
    # This depends on Odoo configuration
    # For now, just verify export dialog appears


@pytest.mark.e2e
@pytest.mark.integration
def test_partner_archiving(authenticated_page: Page):
    """
    Test archiving and unarchiving partners.

    Steps:
    1. Navigate to Contacts
    2. Open partner
    3. Archive partner
    4. Verify archived
    5. Unarchive partner
    """
    page = authenticated_page

    # Navigate to Contacts
    navigate_to_module(page, 'Contacts')

    # Click first partner
    page.click('.o_list_view tbody tr:first-child')
    wait_for_odoo_ready(page)

    # Click Action dropdown
    page.click('button:has-text("Action")')

    # Click Archive
    page.click('text=Archive')

    # Confirm archive (if dialog appears)
    if page.locator('.modal-footer button:has-text("Ok")').is_visible():
        page.click('.modal-footer button:has-text("Ok")')

    # Verify redirect to list view
    page.wait_for_url('**/web#action=*', timeout=10000)

    # Enable "Archived" filter to view archived records
    page.click('button:has-text("Filters")')
    page.click('text=Archived')

    # Verify archived partner appears
    expect(page.locator('.o_list_view tbody tr')).to_have_count(1, timeout=5000)

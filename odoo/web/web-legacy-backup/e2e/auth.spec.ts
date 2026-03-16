import { test, expect } from '@playwright/test';

test.describe('OTP Authentication Flow', () => {
  test('should display sign in button when not authenticated', async ({ page }) => {
    await page.goto('/');

    // Verify Sign In button is visible
    const signInButton = page.getByRole('button', { name: 'Sign In' });
    await expect(signInButton).toBeVisible();
  });

  test('should open OTP modal when sign in is clicked', async ({ page }) => {
    await page.goto('/');

    // Click Sign In button
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Verify modal is visible with email step
    await expect(page.getByText('Sign In')).toBeVisible();
    await expect(page.getByPlaceholder('your@email.com')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send OTP Code' })).toBeVisible();
  });

  test('should validate email input before enabling submit', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Submit button should be disabled without email
    const submitButton = page.getByRole('button', { name: 'Send OTP Code' });
    await expect(submitButton).toBeDisabled();

    // Enter email
    await page.getByPlaceholder('your@email.com').fill('test@example.com');

    // Submit button should now be enabled
    await expect(submitButton).toBeEnabled();
  });

  test('should progress to OTP verification step after email submission', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Fill email and submit
    await page.getByPlaceholder('your@email.com').fill('test@example.com');

    // Mock the OTP request to succeed
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Verify OTP verification step
    await expect(page.getByText('Verify Code')).toBeVisible();
    await expect(page.getByText(/Enter the 6-digit code sent to/)).toBeVisible();
    await expect(page.getByPlaceholder('000000')).toBeVisible();
  });

  test('should validate OTP input (6 digits only)', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Progress to OTP step
    await page.getByPlaceholder('your@email.com').fill('test@example.com');
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });
    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Verify button should be disabled initially
    const verifyButton = page.getByRole('button', { name: /Verify & Sign In/ });
    await expect(verifyButton).toBeDisabled();

    // Fill partial OTP (should still be disabled)
    await page.getByPlaceholder('000000').fill('12345');
    await expect(verifyButton).toBeDisabled();

    // Fill complete OTP (should be enabled)
    await page.getByPlaceholder('000000').fill('123456');
    await expect(verifyButton).toBeEnabled();
  });

  test('should allow going back to email step', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Progress to OTP step
    await page.getByPlaceholder('your@email.com').fill('test@example.com');
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });
    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Click back button
    await page.getByRole('button', { name: /Back to email/ }).click();

    // Verify back on email step
    await expect(page.getByPlaceholder('your@email.com')).toBeVisible();
    await expect(page.getByPlaceholder('your@email.com')).toHaveValue('test@example.com');
  });

  test('should close modal and reload on successful verification', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Progress to OTP step
    await page.getByPlaceholder('your@email.com').fill('test@example.com');
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });
    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Fill OTP
    await page.getByPlaceholder('000000').fill('123456');

    // Mock successful verification
    await page.route('/api/auth/otp-verify', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    });

    // Track page reload
    const [response] = await Promise.all([
      page.waitForNavigation(),
      page.getByRole('button', { name: /Verify & Sign In/ }).click(),
    ]);

    // Verify page reloaded
    expect(response?.url()).toBe('http://localhost:3000/');
  });

  test('should display error message on failed OTP request', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Mock failed OTP request
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Invalid email address' }),
      });
    });

    await page.getByPlaceholderText('your@email.com').fill('invalid@example.com');
    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Verify error message is displayed
    await expect(page.getByText('Invalid email address')).toBeVisible();
  });

  test('should display error message on failed OTP verification', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Sign In' }).click();

    // Progress to OTP step
    await page.getByPlaceholder('your@email.com').fill('test@example.com');
    await page.route('/api/auth/otp-request', async (route) => {
      await route.fulfill({ status: 200, body: JSON.stringify({ success: true }) });
    });
    await page.getByRole('button', { name: 'Send OTP Code' }).click();

    // Mock failed verification
    await page.route('/api/auth/otp-verify', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Invalid OTP code' }),
      });
    });

    await page.getByPlaceholderText('000000').fill('000000');
    await page.getByRole('button', { name: /Verify & Sign In/ }).click();

    // Verify error message is displayed
    await expect(page.getByText('Invalid OTP code')).toBeVisible();
  });
});

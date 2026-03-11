import { test, expect } from '@playwright/test'

test.describe('Dashboard Visual Regression', () => {
  test('should match baseline screenshot - shine theme', async ({ page }) => {
    await page.goto('/dashboard')

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')

    // Wait a bit for any animations
    await page.waitForTimeout(500)

    await expect(page).toHaveScreenshot('dashboard-shine.png', {
      fullPage: true,
      animations: 'disabled',
    })
  })

  test('should match baseline screenshot - dark theme', async ({ page }) => {
    await page.goto('/dashboard')

    await page.locator('select').first().selectOption('dark')

    // Wait for chart re-render and theme to apply
    await page.waitForTimeout(500)
    await page.waitForLoadState('networkidle')

    await expect(page).toHaveScreenshot('dashboard-dark.png', {
      fullPage: true,
      animations: 'disabled',
    })
  })

  test('should match theme selector component', async ({ page }) => {
    await page.goto('/dashboard')

    const selector = page.locator('select').first()
    await expect(selector).toHaveScreenshot('theme-selector.png')
  })
})

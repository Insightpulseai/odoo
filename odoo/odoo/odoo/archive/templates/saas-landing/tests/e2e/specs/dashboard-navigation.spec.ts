import { test, expect } from '@playwright/test'

test.describe('Dashboard Navigation', () => {
  test('should navigate between tabs', async ({ page }) => {
    await page.goto('/dashboard')

    // Default tab
    await expect(page.locator('[role="tabpanel"]')).toContainText('Recent Commits')

    // Click Deployment Logs tab
    await page.click('button:has-text("Deployment Logs")')
    await expect(page.locator('[role="tabpanel"]')).toContainText('Real-time logs')

    // Click Monitoring tab
    await page.click('button:has-text("Monitoring")')
    await expect(page.locator('[role="tabpanel"]')).toContainText('Performance Monitoring')

    // Click Web Shell tab
    await page.click('button:has-text("Web Shell")')
    await expect(page.locator('[role="tabpanel"]')).toContainText('Direct terminal access')
  })

  test('should switch between environments', async ({ page }) => {
    await page.goto('/dashboard')

    // Default: production
    await expect(page.locator('h1')).toContainText('Production Environment')

    // Click staging
    await page.click('button:has-text("Staging")')
    await expect(page.locator('h1')).toContainText('Staging Environment')

    // Click development
    await page.click('button:has-text("Development")')
    await expect(page.locator('h1')).toContainText('Development Environment')
  })

  test('should display deployment status and recent builds', async ({ page }) => {
    await page.goto('/dashboard')

    // Verify sidebar cards
    await expect(page.locator('text=ENVIRONMENTS')).toBeVisible()
    await expect(page.locator('text=RECENT BUILDS')).toBeVisible()

    // Verify build statuses
    const builds = page.locator('text=/Success|Failed/')
    await expect(builds.first()).toBeVisible()
  })

  test('should have Deploy Now button', async ({ page }) => {
    await page.goto('/dashboard')

    const deployButton = page.locator('button:has-text("Deploy Now")')
    await expect(deployButton).toBeVisible()

    // Click deploy
    await deployButton.click()

    // Verify deploying state
    await expect(page.locator('button:has-text("Deploying...")')).toBeVisible()
  })
})

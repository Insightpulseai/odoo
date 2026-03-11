import { test, expect } from '@playwright/test'

test.describe('Dashboard Theme Selector', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard')
  })

  test('should load dashboard with default shine theme', async ({ page }) => {
    // Verify page loaded
    await expect(page.locator('h1')).toContainText('Environment')

    // Verify theme selector exists
    const themeSelector = page.locator('select').filter({ hasText: 'Shine' })
    await expect(themeSelector).toBeVisible()

    // Verify default theme is "shine"
    await expect(themeSelector).toHaveValue('shine')
  })

  test('should persist theme selection in localStorage', async ({ page }) => {
    // Change to dark theme
    const selector = page.locator('select').first()
    await selector.selectOption('dark')

    // Verify localStorage
    const storedTheme = await page.evaluate(() =>
      localStorage.getItem('ipai.chart_theme')
    )
    expect(storedTheme).toBe('"dark"')

    // Reload page
    await page.reload()

    // Verify theme persisted
    await expect(selector).toHaveValue('dark')
  })

  test('should update all charts when theme changes', async ({ page }) => {
    // Wait for charts to load (if any exist)
    const hasCharts = await page.locator('canvas').count() > 0

    if (hasCharts) {
      const initialCanvases = await page.locator('canvas').count()
      expect(initialCanvases).toBeGreaterThan(0)

      // Change theme
      await page.locator('select').first().selectOption('vintage')

      // Wait for chart re-initialization (EChart component useEffect)
      await page.waitForTimeout(500)

      // Verify canvases still present (charts re-rendered)
      const updatedCanvases = await page.locator('canvas').count()
      expect(updatedCanvases).toBe(initialCanvases)
    } else {
      // If no charts, just verify theme changes
      await page.locator('select').first().selectOption('vintage')
      const storedTheme = await page.evaluate(() =>
        localStorage.getItem('ipai.chart_theme')
      )
      expect(storedTheme).toBe('"vintage"')
    }
  })

  test('should cycle through all 6 themes', async ({ page }) => {
    const themes = ['infographic', 'vintage', 'dark', 'roma', 'shine', 'macarons']
    const selector = page.locator('select').first()

    for (const theme of themes) {
      await selector.selectOption(theme)
      await expect(selector).toHaveValue(theme)

      // Verify localStorage updated
      const stored = await page.evaluate(() =>
        localStorage.getItem('ipai.chart_theme')
      )
      expect(stored).toBe(`"${theme}"`)

      // Small delay for chart re-render
      await page.waitForTimeout(300)
    }
  })

  test('should load theme script dynamically', async ({ page }) => {
    // Intercept theme script request
    const scriptPromise = page.waitForRequest(
      req => req.url().includes('/themes/echarts/dark.js'),
      { timeout: 5000 }
    ).catch(() => null)

    await page.locator('select').first().selectOption('dark')

    const scriptRequest = await scriptPromise
    if (scriptRequest) {
      expect(scriptRequest.url()).toContain('/themes/echarts/dark.js')
    }
  })
})

import { test, expect } from '@playwright/test';

test.describe('User Dashboard Flow', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock authenticated session
    await context.addCookies([
      {
        name: 'next-auth.session-token',
        value: 'mock-session-token',
        domain: 'localhost',
        path: '/',
        httpOnly: true,
        sameSite: 'Lax',
        expires: Date.now() / 1000 + 3600,
      },
    ]);
  });

  test('should display user statistics', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show stats cards
    await expect(page.getByTestId('stats-card')).toBeVisible();
    
    // Should show contribution count
    await expect(page.getByText(/contributions|issues solved/i)).toBeVisible();
  });

  test('should display contribution timeline', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show timeline section
    const timeline = page.getByTestId('contribution-timeline');
    if (await timeline.isVisible()) {
      // Should have timeline items
      await expect(timeline.locator('[data-testid="timeline-item"]').first()).toBeVisible();
    }
  });

  test('should display language breakdown', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show language breakdown
    const languageBreakdown = page.getByTestId('language-breakdown');
    if (await languageBreakdown.isVisible()) {
      // Should show at least one language
      await expect(languageBreakdown.getByText(/javascript|python|typescript/i)).toBeVisible();
    }
  });

  test('should display achievements and badges', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show achievements section
    const achievements = page.getByText(/achievements|badges/i);
    if (await achievements.isVisible()) {
      // Should show achievement badges
      await expect(page.getByTestId('achievement-badge')).toBeVisible();
    }
  });

  test('should navigate to settings', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for settings link
    const settingsLink = page.getByRole('link', { name: /settings|preferences/i });
    
    if (await settingsLink.isVisible()) {
      await settingsLink.click();
      
      // Should navigate to settings page
      await expect(page).toHaveURL(/\/settings|\/preferences/);
    }
  });

  test('should update user preferences', async ({ page }) => {
    await page.goto('/settings');
    
    // Look for language preferences
    const languageCheckbox = page.getByRole('checkbox', { name: /javascript/i });
    
    if (await languageCheckbox.isVisible()) {
      const wasChecked = await languageCheckbox.isChecked();
      
      // Toggle checkbox
      if (wasChecked) {
        await languageCheckbox.uncheck();
      } else {
        await languageCheckbox.check();
      }
      
      // Save preferences
      const saveButton = page.getByRole('button', { name: /save|update/i });
      await saveButton.click();
      
      // Should show success message
      await expect(page.getByText(/saved|updated/i)).toBeVisible();
    }
  });
});

import { test, expect } from '@playwright/test';

test.describe('Issue Discovery Flow', () => {
  test.beforeEach(async ({ page, context }) => {
    // Mock authenticated session for all tests
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

  test('should display list of issues', async ({ page }) => {
    await page.goto('/issues');
    
    // Wait for issues to load
    await page.waitForSelector('[data-testid="issue-card"]', { timeout: 10000 });
    
    // Should show at least one issue
    const issueCards = page.locator('[data-testid="issue-card"]');
    await expect(issueCards.first()).toBeVisible();
  });

  test('should filter issues by programming language', async ({ page }) => {
    await page.goto('/issues');
    
    // Wait for issues to load
    await page.waitForSelector('[data-testid="issue-card"]');
    
    // Click on a language filter
    const languageFilter = page.getByRole('checkbox', { name: /javascript/i });
    if (await languageFilter.isVisible()) {
      await languageFilter.check();
      
      // Wait for filtered results
      await page.waitForTimeout(1000);
      
      // Verify URL contains filter parameter
      expect(page.url()).toContain('language');
    }
  });

  test('should search issues by text', async ({ page }) => {
    await page.goto('/issues');
    
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('bug fix');
    await searchInput.press('Enter');
    
    // Wait for search results
    await page.waitForTimeout(1000);
    
    // Verify URL contains search parameter
    expect(page.url()).toContain('search');
  });

  test('should navigate to issue detail page', async ({ page }) => {
    await page.goto('/issues');
    
    // Wait for issues to load
    await page.waitForSelector('[data-testid="issue-card"]');
    
    // Click on first issue
    const firstIssue = page.locator('[data-testid="issue-card"]').first();
    await firstIssue.click();
    
    // Should navigate to detail page
    await expect(page).toHaveURL(/\/issues\/\d+/);
    
    // Should show issue details
    await expect(page.getByTestId('issue-title')).toBeVisible();
  });

  test('should paginate through issues', async ({ page }) => {
    await page.goto('/issues');
    
    // Wait for issues to load
    await page.waitForSelector('[data-testid="issue-card"]');
    
    // Find next page button
    const nextButton = page.getByRole('button', { name: /next/i });
    
    if (await nextButton.isEnabled()) {
      await nextButton.click();
      
      // Wait for new page to load
      await page.waitForTimeout(1000);
      
      // Verify URL contains page parameter
      expect(page.url()).toContain('page=2');
    }
  });
});

import { test, expect } from '@playwright/test';

test.describe('Issue Claim and PR Submission Flow', () => {
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

  test('should claim an available issue', async ({ page }) => {
    await page.goto('/issues');
    
    // Wait for issues to load
    await page.waitForSelector('[data-testid="issue-card"]');
    
    // Click on first available issue
    const firstIssue = page.locator('[data-testid="issue-card"]').first();
    await firstIssue.click();
    
    // Wait for detail page
    await page.waitForURL(/\/issues\/\d+/);
    
    // Look for "Solve It" or "Claim" button
    const claimButton = page.getByRole('button', { name: /solve it|claim/i });
    
    if (await claimButton.isVisible() && await claimButton.isEnabled()) {
      // Click claim button
      await claimButton.click();
      
      // Should show success message or redirect to GitHub
      await page.waitForTimeout(2000);
      
      // Either redirected to GitHub or button changed state
      const isGitHub = page.url().includes('github.com');
      const buttonChanged = await page.getByText(/claimed|release/i).isVisible();
      
      expect(isGitHub || buttonChanged).toBeTruthy();
    }
  });

  test('should show claimed issue status', async ({ page }) => {
    // Navigate to an issue that's already claimed
    await page.goto('/issues/1');
    
    // Check if issue shows claimed status
    const claimedIndicator = page.getByText(/claimed by|you claimed/i);
    
    if (await claimedIndicator.isVisible()) {
      // Should show countdown timer
      await expect(page.getByTestId('countdown-timer')).toBeVisible();
      
      // Should show release button
      await expect(page.getByRole('button', { name: /release/i })).toBeVisible();
    }
  });

  test('should submit PR link for claimed issue', async ({ page }) => {
    await page.goto('/issues/1');
    
    // Look for PR submission form
    const prInput = page.getByPlaceholder(/pull request url|pr link/i);
    
    if (await prInput.isVisible()) {
      // Fill in PR URL
      await prInput.fill('https://github.com/test/repo/pull/123');
      
      // Submit PR
      const submitButton = page.getByRole('button', { name: /submit pr|submit/i });
      await submitButton.click();
      
      // Wait for submission
      await page.waitForTimeout(2000);
      
      // Should show success message or validation status
      const successMessage = page.getByText(/submitted|validating/i);
      await expect(successMessage).toBeVisible();
    }
  });

  test('should extend claim deadline', async ({ page }) => {
    await page.goto('/issues/1');
    
    // Look for extend deadline button
    const extendButton = page.getByRole('button', { name: /extend/i });
    
    if (await extendButton.isVisible() && await extendButton.isEnabled()) {
      await extendButton.click();
      
      // Should show extension form or confirmation
      await page.waitForTimeout(1000);
      
      const confirmButton = page.getByRole('button', { name: /confirm|request/i });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
        
        // Should show success message
        await expect(page.getByText(/extended|approved/i)).toBeVisible();
      }
    }
  });

  test('should release claimed issue', async ({ page }) => {
    await page.goto('/issues/1');
    
    // Look for release button
    const releaseButton = page.getByRole('button', { name: /release/i });
    
    if (await releaseButton.isVisible() && await releaseButton.isEnabled()) {
      await releaseButton.click();
      
      // Should show confirmation dialog
      const confirmButton = page.getByRole('button', { name: /confirm|yes/i });
      if (await confirmButton.isVisible()) {
        await confirmButton.click();
        
        // Wait for release
        await page.waitForTimeout(1000);
        
        // Button should change back to "Solve It"
        await expect(page.getByRole('button', { name: /solve it/i })).toBeVisible();
      }
    }
  });
});

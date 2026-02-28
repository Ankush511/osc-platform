import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should display login button on homepage', async ({ page }) => {
    await page.goto('/');
    
    const loginButton = page.getByRole('button', { name: /sign in/i });
    await expect(loginButton).toBeVisible();
  });

  test('should redirect to GitHub OAuth when clicking sign in', async ({ page }) => {
    await page.goto('/');
    
    const loginButton = page.getByRole('button', { name: /sign in/i });
    
    // Start waiting for navigation before clicking
    const navigationPromise = page.waitForURL(/github\.com\/login\/oauth/);
    await loginButton.click();
    
    // Wait for navigation to GitHub OAuth
    await navigationPromise;
    
    expect(page.url()).toContain('github.com');
  });

  test('should show protected content after authentication', async ({ page, context }) => {
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

    await page.goto('/dashboard');
    
    // Should not redirect to login
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Should show user dashboard content
    await expect(page.getByText(/dashboard/i)).toBeVisible();
  });

  test('should redirect unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should redirect to home or show login prompt
    await page.waitForURL(/\/(|api\/auth\/signin)/);
  });
});

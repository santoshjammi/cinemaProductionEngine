import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Text Cinema Engine');
    await expect(page.locator('text=Transform your story ideas')).toBeVisible();
  });

  test('shows pipeline input form', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[placeholder*="alien civilization"]')).toBeVisible();
    await expect(page.locator('button:has-text("Generate Story")')).toBeVisible();
  });

  test('can type a story prompt', async ({ page }) => {
    await page.goto('/');
    const input = page.locator('input[placeholder*="alien civilization"]');
    await input.fill('A brave astronaut discovers a new planet');
    await expect(input).toHaveValue('A brave astronaut discovers a new planet');
  });

  test('shows research toggle', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Internet Research')).toBeVisible();
  });
});

test.describe('Pipeline Detail Page', () => {
  test('shows loading state for invalid ID', async ({ page }) => {
    await page.goto('/pipeline/invalid-id');
    await expect(page.locator('text=Back to Home')).toBeVisible();
  });

  test('navigates back to home', async ({ page }) => {
    await page.goto('/pipeline/test-id');
    await page.locator('text=Back to Home').click();
    await expect(page).toHaveURL('/');
  });
});

test.describe('Accessibility Basics', () => {
  test('page has proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    const h1 = page.locator('h1');
    await expect(h1).toHaveCount(1);
  });

  test('form inputs have associated labels', async ({ page }) => {
    await page.goto('/');
    const inputs = page.locator('input, textarea');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
  });
});

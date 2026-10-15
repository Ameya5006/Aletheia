import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const samples = JSON.parse(
  readFileSync(resolve(import.meta.dirname, '../tests/real-api-responses.json'), 'utf8'),
) as Record<string, unknown>;
const axeSource = readFileSync(
  resolve(import.meta.dirname, '../node_modules/axe-core/axe.min.js'),
  'utf8',
);
test.beforeEach(async ({ page }) => {
  await page.route('**/api/v1/**', async (route) => {
    const path = new URL(route.request().url()).pathname.replace('/api/v1', '');
    await route.fulfill({
      status: path === '/health/ready' ? 503 : path in samples ? 200 : 404,
      contentType: 'application/json',
      body: JSON.stringify(
        samples[path] ?? {
          schema_version: 'application-v1',
          request_id: '00000000-0000-4000-8000-000000000001',
          error: { code: 'not_found', message: 'not found' },
        },
      ),
    });
  });
});
for (const width of [375, 768, 1440]) {
  test(`responsive evidence and accessibility at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    for (const path of [
      '/',
      '/demo',
      '/evidence/local',
      '/evidence/global',
      '/evidence/stability',
      '/evidence/subgroups',
      '/evidence/feasibility',
      '/review',
      '/audit-history',
      '/model-card',
      '/sign-in',
    ]) {
      await page.goto(path);
      await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
      await expect(page.getByRole('status')).toHaveCount(0);
      const layout = await page.evaluate(() => ({
        width: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        outside: Array.from(
          document.querySelectorAll(
            'main a, main button, main input, main select, main summary, main code',
          ),
        )
          .filter((element) => {
            const rect = element.getBoundingClientRect();
            return (
              rect.width > 0 &&
              rect.height > 0 &&
              !element.closest('.table-scroll') &&
              (rect.left < 0 || rect.right > window.innerWidth + 1)
            );
          })
          .map((element) => ({ tag: element.tagName, text: element.textContent?.slice(0, 80) })),
      }));
      expect(
        layout.scrollWidth,
        `${path} at ${width}px: ${JSON.stringify(layout)}`,
      ).toBeLessThanOrEqual(width);
      expect(layout.outside, `${path} controls and identifiers at ${width}px`).toEqual([]);
      if (path === '/model-card') {
        for (const region of await page.getByRole('region', { name: 'Model card table' }).all()) {
          await region.focus();
          await expect(region).toBeFocused();
        }
        await page.screenshot({ path: `test-results/model-card-${width}.png`, fullPage: true });
      }
      await page.locator('details').evaluateAll((items) =>
        items.forEach((item) => {
          (item as HTMLDetailsElement).open = true;
        }),
      );
      await expect(page.locator('body')).not.toContainText(
        /synthetic|demonstration|dismissed_demo|\bdemo\b/i,
      );
      await page.addScriptTag({ content: axeSource });
      const violations = await page.evaluate(async () => {
        const runner = (
          window as unknown as {
            axe: {
              run: (
                options: unknown,
              ) => Promise<{ violations: { id: string; impact: string; nodes: unknown[] }[] }>;
            };
          }
        ).axe;
        return (
          await runner.run({
            runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] },
          })
        ).violations;
      });
      expect(violations, `${path} at ${width}px`).toEqual([]);
    }
    await page.goto('/');
    await expect(page.getByText(/No analysis is selected/)).toBeVisible();
    await expect(page.getByText('12.78', { exact: false })).toHaveCount(0);
    if (width < 768) {
      await page.getByRole('button', { name: 'Open navigation' }).click();
      await expect(page.locator('#mobile-menu')).toBeVisible();
      await page.locator('#mobile-menu').getByRole('link', { name: 'New Analysis' }).focus();
      await page.keyboard.press('Escape');
      await expect(page.getByRole('button', { name: 'Open navigation' })).toBeFocused();
      await page.getByRole('button', { name: 'Open navigation' }).click();
      await page.locator('#mobile-menu').getByRole('link', { name: 'New Analysis' }).click();
    } else {
      await page.getByRole('button', { name: 'Collapse sidebar' }).click();
      await expect(
        page.locator('.sidebar').getByRole('link', { name: 'New Analysis' }),
      ).toBeVisible();
      await page.locator('.sidebar').getByRole('link', { name: 'New Analysis' }).click();
    }
    await expect(page.getByRole('main')).toBeFocused();
    await page.screenshot({ path: `test-results/case-${width}.png`, fullPage: true });
  });
}
test('dark appearance, reduced motion, skip navigation and failure state', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark', reducedMotion: 'reduce' });
  await page.goto('/evidence/local');
  await expect(page.getByRole('table')).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Skip to content' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('main')).toBeFocused();
  expect(
    await page
      .locator('button')
      .first()
      .evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe('0s');
  await page.addScriptTag({ content: axeSource });
  expect(
    await page.evaluate(async () =>
      (window as unknown as { axe: { run: () => Promise<{ violations: unknown[] }> } }).axe
        .run()
        .then((r) => r.violations),
    ),
  ).toEqual([]);
  await page.route('**/api/v1/explanations/local/**', (route) => route.abort());
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('No substitute results');
  await expect(page.getByRole('table')).toHaveCount(0);
  await page.screenshot({ path: 'test-results/dark-unavailable.png', fullPage: true });
});

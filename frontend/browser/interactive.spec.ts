// Real API and database: no route interception or API response mocks.
import { test, expect } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

test('manual case, save, reopen, changed rerun, reset and accessible states', async ({ page }) => {
  const token = readFileSync(process.env.ALETHEIA_BROWSER_TOKEN_FILE!, 'utf8').trim();
  const axe = readFileSync(
    resolve(import.meta.dirname, '../node_modules/axe-core/axe.min.js'),
    'utf8',
  );
  const checks: { state: string; width: number; violations: number }[] = [];
  async function accessible(state: string) {
    for (const width of [375, 768, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.evaluate(axe);
      const violations = await page.evaluate(
        async () =>
          (
            await (
              window as unknown as {
                axe: { run: (config: unknown) => Promise<{ violations: unknown[] }> };
              }
            ).axe.run({
              runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] },
            })
          ).violations,
      );
      expect(violations, `${state} ${width}`).toEqual([]);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true,
      );
      checks.push({ state, width, violations: violations.length });
    }
  }
  await page.goto('/local-session');
  await page.getByLabel('Provisioned access token').fill(token);
  const connected = page.waitForResponse((response) => response.url().endsWith('/api/v1/session'));
  await page.getByRole('button', { name: 'Connect local identity', exact: true }).click();
  expect((await connected).status()).toBe(200);
  await expect(page.getByLabel('Admission type')).toBeVisible();
  expect(await page.getByLabel('Admission type').inputValue()).toBe('');
  await page.getByRole('link', { name: 'Overview', exact: true }).click();
  await expect(page.getByText(/No analysis is selected/)).toBeVisible();
  await expect(page.getByText('12.78', { exact: false })).toHaveCount(0);
  await accessible('overview-empty');
  await page.getByRole('link', { name: 'New Analysis', exact: true }).first().click();
  await accessible('empty-input');
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  await expect(page.getByRole('alert')).toHaveText('Check the highlighted fields.');
  await accessible('validation-error');
  for (const [label, value] of Object.entries({
    'Admission type': '2',
    'Admission source': '7',
    'Maximum glucose result': 'Norm',
    'A1C result': '>7',
    'Diabetes medication prescribed': 'Yes',
  }))
    await page.getByLabel(label, { exact: true }).selectOption(value);
  for (const [label, value] of Object.entries({
    'Time in hospital': '5',
    'Laboratory procedures': '45',
    Procedures: '2',
    'Distinct medications': '15',
    'Outpatient visits in the preceding year': '1',
    'Emergency visits in the preceding year': '1',
    'Inpatient visits in the preceding year': '2',
    Diagnoses: '6',
  }))
    await page.getByLabel(label, { exact: true }).fill(value);
  const prediction = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const predictionResponse = await prediction;
  expect(predictionResponse.status(), await predictionResponse.text()).toBe(201);
  const created = await predictionResponse.json();
  const original = created.data;
  expect(original.inputs.number_inpatient).toBe('2');
  expect(original.inputs.time_in_hospital).toBe('5');
  expect(original.probability).toBeGreaterThanOrEqual(0);
  expect(original.probability).toBeLessThanOrEqual(1);
  await expect(page.getByText(original.prediction_id, { exact: true })).toBeVisible();
  await expect(page.getByText(original.event_id, { exact: true })).toBeVisible();
  await accessible('result');
  await page.getByRole('button', { name: 'Save Analysis', exact: true }).click();
  await expect(page.getByText('Saved', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Analysis History', exact: true }).click();
  await expect(
    page.getByRole('link', { name: 'Open analysis ' + original.prediction_id }),
  ).toBeVisible();
  await accessible('history');
  await page.getByRole('link', { name: 'Open analysis ' + original.prediction_id }).click();
  await expect(page.getByText(original.prediction_id, { exact: true })).toBeVisible();
  await accessible('reopened-record');
  await page.getByRole('button', { name: 'Load inputs into New Analysis' }).click();
  await expect(page.getByLabel('Inpatient visits in the preceding year')).toHaveValue('2');
  await page.getByLabel('Inpatient visits in the preceding year').fill('4');
  const rerunResponse = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const rerun = (await (await rerunResponse).json()).data;
  expect(rerun.prediction_id).not.toBe(original.prediction_id);
  expect(rerun.event_id).not.toBe(original.event_id);
  const reopened = (
    await (
      await page.request.get('/api/v1/analyses/' + original.prediction_id, {
        headers: { Authorization: 'Bearer ' + token },
      })
    ).json()
  ).data;
  for (const key of ['inputs', 'probability', 'explanation', 'stability', 'event_id', 'created_at'])
    expect(reopened[key]).toEqual(original[key]);
  await page.getByRole('button', { name: 'Reset Form', exact: true }).click();
  await expect(page.getByLabel('Time in hospital')).toHaveValue('');
  await expect(page.getByRole('heading', { name: 'Prediction Result' })).toHaveCount(0);
  await page.getByRole('link', { name: 'Analysis History', exact: true }).click();
  await expect(
    page.getByRole('link', { name: 'Open analysis ' + original.prediction_id }),
  ).toBeVisible();
  for (const path of [
    '/',
    '/evidence/local',
    '/evidence/global',
    '/evidence/stability',
    '/evidence/subgroups',
    '/evidence/feasibility',
    '/model-card',
    '/review',
    '/audit-history',
  ]) {
    await page.evaluate((target) => {
      history.pushState({}, '', target);
      dispatchEvent(new PopStateEvent('popstate'));
    }, path);
    await expect(page.getByRole('heading', { level: 1 }).first()).toBeVisible();
    await expect(page.getByRole('status')).toHaveCount(0);
    await page.locator('details').evaluateAll((items) =>
      items.forEach((item) => {
        (item as HTMLDetailsElement).open = true;
      }),
    );
    await expect(page.locator('body')).not.toContainText(
      /synthetic|demonstration|dismissed_demo|\bdemo\b/i,
    );
  }
  await page.keyboard.press('Tab');
  writeFileSync(
    process.env.ALETHEIA_BROWSER_EVIDENCE ||
      resolve(import.meta.dirname, '../../artifacts/interactive-verification/browser.json'),
    JSON.stringify(
      {
        checks,
        original_prediction_id: original.prediction_id,
        rerun_prediction_id: rerun.prediction_id,
        immutable_original: true,
        reset_preserved_history: true,
      },
      null,
      2,
    ),
  );
});

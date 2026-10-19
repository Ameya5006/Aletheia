import { test, expect } from '@playwright/test';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

test('Azure provisioned case workflow stays persistent and resettable', async ({ page }) => {
  const token = readFileSync(process.env.ALETHEIA_BROWSER_TOKEN_FILE!, 'utf8').trim();
  await page.goto('/local-session');
  await page.getByLabel('Provisioned access token').fill(token);
  const connected = page.waitForResponse((r) => r.url().includes('/api/v1/analyses?limit=1'));
  await page.getByRole('button', { name: 'Connect provisioned identity' }).click();
  expect((await connected).status()).toBe(200);
  await expect(page.getByLabel('Admission type')).toBeVisible();
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
  const createdResponse = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const created = await createdResponse;
  expect(created.status()).toBe(201);
  const original = (await created.json()).data;
  expect(original.probability).toBeGreaterThanOrEqual(0);
  expect(original.probability).toBeLessThanOrEqual(1);
  await page.getByRole('button', { name: 'Save Analysis' }).click();
  await expect(page.getByText('Saved', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Analysis History', exact: true }).click();
  await page.getByRole('link', { name: 'Open analysis ' + original.prediction_id }).click();
  await expect(page.getByText(original.prediction_id, { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Load inputs into New Analysis' }).click();
  await page.getByLabel('Inpatient visits in the preceding year').fill('4');
  const rerunResponse = page.waitForResponse(
    (r) => r.url().endsWith('/api/v1/analyses') && r.request().method() === 'POST',
  );
  await page.getByRole('button', { name: 'Run Analysis', exact: true }).click();
  const rerun = (await (await rerunResponse).json()).data;
  expect(rerun.prediction_id).not.toBe(original.prediction_id);
  const reopened = await page.request.get('/api/v1/analyses/' + original.prediction_id, {
    headers: { Authorization: 'Bearer ' + token },
  });
  expect(reopened.status()).toBe(200);
  expect((await reopened.json()).data.probability).toBe(original.probability);
  await page.getByRole('button', { name: 'Reset Form' }).click();
  await expect(page.getByLabel('Time in hospital')).toHaveValue('');
  await expect(page.getByRole('heading', { name: 'Prediction Result' })).toHaveCount(0);
  writeFileSync(
    resolve(import.meta.dirname, '../../artifacts/azure-preflight/cloud-browser.json'),
    JSON.stringify(
      {
        original_prediction_id: original.prediction_id,
        rerun_prediction_id: rerun.prediction_id,
        probability: original.probability,
        saved: true,
        reopened: true,
        original_immutable: true,
        reset: true,
      },
      null,
      2,
    ),
  );
});

// Identity and private API fixtures are confined to the browser HTTP boundary.
// This exercises the real PKCE callback/session/UI without a live organization.
import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import {
  publicResponses,
  envelope,
  prediction,
  review,
  event,
  predictionId,
  eventId,
} from '../tests/fixtures';

const axeSource = readFileSync(
  resolve(import.meta.dirname, '../node_modules/axe-core/axe.min.js'),
  'utf8',
);
for (const width of [375, 768, 1440]) {
  test(`authenticated controls and responsive routes at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    const authority = 'https://identity.example.test';
    const now = Math.floor(Date.now() / 1000);
    const jwt = (claims: unknown) =>
      `${Buffer.from(JSON.stringify({ alg: 'RS256' })).toString('base64url')}.${Buffer.from(JSON.stringify(claims)).toString('base64url')}.test-signature`;
    const accessToken = jwt({ roles: ['engineer', 'reviewer', 'administrator'] });
    let nonce: string | null = null;
    await page.route(authority + '/**', async (route) => {
      const url = new URL(route.request().url());
      if (url.pathname === '/.well-known/openid-configuration') {
        await route.fulfill({
          json: {
            issuer: authority,
            authorization_endpoint: authority + '/authorize',
            token_endpoint: authority + '/token',
            userinfo_endpoint: authority + '/userinfo',
            jwks_uri: authority + '/jwks',
          },
        });
      } else if (url.pathname === '/authorize') {
        expect(url.searchParams.get('code_challenge_method')).toBe('S256');
        expect(url.searchParams.get('code_challenge')).toBeTruthy();
        nonce = url.searchParams.get('nonce');
        const callback = new URL(url.searchParams.get('redirect_uri')!);
        callback.searchParams.set('code', 'test-code');
        callback.searchParams.set('state', url.searchParams.get('state')!);
        await route.fulfill({ status: 302, headers: { Location: callback.toString() } });
      } else if (url.pathname === '/token') {
        expect(new URLSearchParams(route.request().postData()!).get('code_verifier')).toBeTruthy();
        await route.fulfill({
          json: {
            access_token: accessToken,
            token_type: 'Bearer',
            expires_in: 600,
            scope: 'openid profile',
            id_token: jwt({
              iss: authority,
              sub: 'browser-test',
              aud: 'browser-test',
              iat: now,
              exp: now + 600,
              ...(nonce ? { nonce } : {}),
            }),
          },
        });
      } else if (url.pathname === '/userinfo') {
        await route.fulfill({ json: { sub: 'browser-test' } });
      } else {
        await route.fulfill({ status: 404, json: {} });
      }
    });
    let reviewSaved = false;
    const model = structuredClone(publicResponses['/models/current']) as {
      data: { approval_status: string; serving_available: boolean };
    };
    model.data.approval_status = 'approved';
    model.data.serving_available = true;
    const version = {
      id: eventId,
      registry_name: 'browser-test-model',
      version: '1',
      run_id: 'browser-test-run',
      model_sha256: 'a'.repeat(64),
      package_sha256: 'b'.repeat(64),
      release_sha256: 'c'.repeat(64),
      config_sha256: 'd'.repeat(64),
      selection_sha256: 'e'.repeat(64),
      split_sha256: 'f'.repeat(64),
      protocol_sha256: 'a'.repeat(64),
      results_sha256: 'b'.repeat(64),
      signature_version: 'synthetic-v1',
      runtime: { python: '3.12.10' },
      created_at: prediction.created_at,
      release_events: [
        {
          id: eventId,
          action: 'activated',
          audit_event_id: eventId,
          created_at: prediction.created_at,
        },
      ],
    };
    await page.route('**/api/v1/**', async (route) => {
      const path = new URL(route.request().url()).pathname.replace('/api/v1', '');
      const privatePath =
        path.startsWith('/predictions') ||
        path.startsWith('/audit-events') ||
        path.startsWith('/admin/');
      if (privatePath)
        expect(route.request().headers().authorization).toBe('Bearer ' + accessToken);
      let body: unknown = publicResponses[path];
      let status = 200;
      if (path === '/models/current') body = model;
      if (path === '/health/ready')
        body = { schema_version: 'application-v1', request_id: eventId, data: { status: 'ready' } };
      if (path === '/predictions' || path === `/predictions/${predictionId}`) {
        body = envelope(prediction, 'synthetic_inference');
        if (route.request().method() === 'POST') status = 201;
      }
      if (path === `/predictions/${predictionId}/reviews`) {
        if (route.request().method() === 'POST') {
          reviewSaved = true;
          status = 201;
          body = envelope(review, 'synthetic_inference');
        } else
          body = envelope(
            { items: reviewSaved ? [review] : [], next_cursor: null },
            'synthetic_inference',
          );
      }
      if (path === '/audit-events') body = envelope({ items: [event], next_cursor: null });
      if (path === `/audit-events/${eventId}`) body = envelope(event);
      if (path === '/admin/model-versions')
        body = envelope({ items: [version], next_cursor: null });
      if (path === '/admin/model-versions/1') body = envelope(version);
      await route.fulfill({ status: body ? status : 404, json: body ?? {} });
    });
    await page.goto('/sign-in');
    await page.getByRole('button', { name: /Continue with organization/ }).click();
    await expect(page).toHaveURL('http://127.0.0.1:4173/');
    if (width < 768) {
      await page.getByRole('button', { name: 'Open navigation' }).click();
      await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible();
    } else await expect(page.getByText('Organization session')).toBeVisible();
    for (const path of [
      `/predictions/${predictionId}`,
      `/predictions/${predictionId}/review`,
      '/audit-history',
      `/audit-history/${eventId}`,
      '/admin/models',
      '/admin/models/1',
    ]) {
      // Client navigation preserves the deliberately in-memory session.
      await page.evaluate((target) => {
        history.pushState({}, '', target);
        dispatchEvent(new PopStateEvent('popstate'));
      }, path);
      await expect(page.getByRole('heading', { level: 1 }).first()).toHaveText(
        path.startsWith('/admin/')
          ? 'Release evidence'
          : path.startsWith('/audit-history')
            ? 'Audit Trail'
            : path.endsWith('/review')
              ? 'Review'
              : 'Case Analysis',
      );
      await expect(page.getByRole('status')).toHaveCount(0);
      const clipped = await page.evaluate(() =>
        Array.from(
          document.querySelectorAll('main button, main input, main select, main a, main summary'),
        )
          .filter((e) => {
            const r = e.getBoundingClientRect();
            return (
              r.width > 0 &&
              r.height > 0 &&
              !e.closest('.table-scroll') &&
              (r.left < 0 || r.right > innerWidth + 1)
            );
          })
          .map((e) => e.textContent),
      );
      expect(clipped, path).toEqual([]);
      expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(
        width,
      );
      await page.locator('details').evaluateAll((items) =>
        items.forEach((item) => {
          (item as HTMLDetailsElement).open = true;
        }),
      );
      await expect(page.locator('body')).not.toContainText(
        /synthetic|demonstration|dismissed_demo|\bdemo\b/i,
      );
      await page.addScriptTag({ content: axeSource });
      const violations = await page.evaluate(async () =>
        (
          window as unknown as {
            axe: { run: (options: unknown) => Promise<{ violations: unknown[] }> };
          }
        ).axe
          .run({ runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] } })
          .then((r) => r.violations),
      );
      expect(violations, path).toEqual([]);
      if (path.endsWith('/review')) {
        for (const checkbox of await page.getByRole('checkbox').all()) await checkbox.check();
        await page.getByLabel('Required coded reason').selectOption('evidence_reviewed');
        await page.getByRole('button', { name: 'Submit coded review' }).click();
        await expect(
          page.getByRole('status').filter({ hasText: 'Review persisted' }),
        ).toBeVisible();
        await page.screenshot({ path: `test-results/review-${width}.png`, fullPage: true });
      }
    }
  });
}

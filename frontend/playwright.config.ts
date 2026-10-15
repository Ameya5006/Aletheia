import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './browser',
  testIgnore: process.env.ALETHEIA_BROWSER_TOKEN_FILE ? [] : ['**/interactive.spec.ts'],
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 150000,
  reporter: 'list',
  use: {
    baseURL: process.env.ALETHEIA_BROWSER_BASE_URL || 'http://127.0.0.1:4173',
    channel: 'msedge',
    headless: true,
    trace: process.env.ALETHEIA_BROWSER_BASE_URL ? 'off' : 'retain-on-failure',
  },
  webServer: process.env.ALETHEIA_BROWSER_BASE_URL
    ? undefined
    : {
        command: 'npm run dev -- --port 4173 --strictPort',
        env: {
          VITE_LOCAL_IDENTITY: 'true',
          VITE_OIDC_AUTHORITY: 'https://identity.example.test',
          VITE_OIDC_CLIENT_ID: 'browser-test',
        },
        url: 'http://127.0.0.1:4173',
        reuseExistingServer: false,
        timeout: 30000,
      },
});

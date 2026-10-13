import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './browser',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 150000,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:4173',
    channel: 'msedge',
    headless: true,
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev -- --port 4173 --strictPort',
    env: {
      VITE_OIDC_AUTHORITY: 'https://identity.example.test',
      VITE_OIDC_CLIENT_ID: 'browser-test',
    },
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: false,
    timeout: 30000,
  },
});

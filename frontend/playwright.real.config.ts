import { defineConfig, devices } from '@playwright/test';

/**
 * Real-backend E2E config — the opposite of the mock suite.
 *
 * These specs (tests/e2e/real/*.real.spec.ts) drive the actual FastAPI
 * backend with NO browser-layer API mocking, so they exercise real auth,
 * real persistence, and the real certificate pipeline. They import the raw
 * `@playwright/test` `test` (not tests/e2e/setup/fixtures.ts) so the api-mock
 * is never installed.
 *
 * Requires both servers already running (this config never spawns them):
 *   - Frontend at E2E_BASE_URL (default http://localhost:3000)
 *   - Backend  at NUXT_PUBLIC_API_BASE_URL (default http://localhost:8020)
 *     with an admin seeded as admin@valuadis.com / password123.
 *
 * Run: npx playwright test --config=playwright.real.config.ts
 */
const baseURL = process.env.E2E_BASE_URL || 'http://localhost:3000';

export default defineConfig({
  testDir: './tests/e2e/real',
  testMatch: '**/*.real.spec.ts',
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'real-chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});

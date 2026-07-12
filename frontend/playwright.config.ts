import { defineConfig, devices } from '@playwright/test';

const e2ePort = process.env.E2E_FRONTEND_PORT || '3020';
const e2eBaseURL = process.env.E2E_BASE_URL || `http://127.0.0.1:${e2ePort}`;
const apiBaseURL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8020';
const skipWebServer =
  process.env.PW_SKIP_WEBSERVER === '1' ||
  process.env.E2E_SKIP_WEBSERVER === '1';
const browserChannel = process.env.PW_BROWSER_CHANNEL || undefined;
const browserUse = browserChannel ? { channel: browserChannel } : {};

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  use: {
    baseURL: e2eBaseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'setup',
      testMatch: '**/setup/auth.setup.ts',
      use: { ...devices['Desktop Chrome'], ...browserUse },
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], ...browserUse },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'], ...browserUse },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
      dependencies: ['setup'],
    },
  ],

  webServer: skipWebServer
    ? undefined
    : {
        command: `cd app && NUXT_PUBLIC_API_BASE_URL=${apiBaseURL} npm run dev -- --host 127.0.0.1 --port ${e2ePort}`,
        url: e2eBaseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 240000,
        stdout: 'pipe',
        stderr: 'pipe',
      },
});

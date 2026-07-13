import { test, expect } from '@playwright/test';

// Health endpoints are a real backend contract (they cannot be intercepted via
// page.route, which only affects page navigation, not page.request). Point them
// at the API origin rather than the frontend baseURL.
const API_BASE = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8020';

test.describe('Operational readiness QA', () => {
  test('health endpoints return deterministic contracts', async ({ page }) => {
    const health = await page.request.get(`${API_BASE}/api/v1/health/full`);
    expect(health.ok()).toBeTruthy();
    const fullBody = await health.json();
    expect(fullBody.service).toBe('valuadis-api');
    expect(['healthy', 'unhealthy']).toContain(fullBody.status);
    expect(fullBody.checks).toHaveProperty('database.status');
    expect(fullBody.checks).toHaveProperty('redis.status');

    const ready = await page.request.get(`${API_BASE}/api/v1/health/ready`);
    expect(ready.ok()).toBeTruthy();
    const readyBody = await ready.json();
    expect(readyBody.service).toBe('valuadis-api');
    expect(['ready', 'not ready']).toContain(readyBody.status);
    expect(readyBody).toHaveProperty('checks');

    const live = await page.request.get(`${API_BASE}/api/v1/health/live`);
    expect(live.ok()).toBeTruthy();
    expect(await live.json()).toEqual({
      status: 'alive',
      service: 'valuadis-api',
    });
  });
});

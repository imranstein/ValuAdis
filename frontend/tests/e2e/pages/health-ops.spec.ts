import { test, expect } from '@playwright/test';

test.describe('Operational readiness QA', () => {
  test('health endpoints return deterministic contracts', async ({ page }) => {
    const health = await page.request.get('/api/v1/health/full');
    expect(health.ok()).toBeTruthy();
    const fullBody = await health.json();
    expect(fullBody.service).toBe('valuadis-api');
    expect(['healthy', 'unhealthy']).toContain(fullBody.status);
    expect(fullBody.checks).toHaveProperty('database.status');
    expect(fullBody.checks).toHaveProperty('redis.status');

    const ready = await page.request.get('/api/v1/health/ready');
    expect(ready.ok()).toBeTruthy();
    const readyBody = await ready.json();
    expect(readyBody.service).toBe('valuadis-api');
    expect(['ready', 'not ready']).toContain(readyBody.status);
    expect(readyBody).toHaveProperty('checks');

    const live = await page.request.get('/api/v1/health/live');
    expect(live.ok()).toBeTruthy();
    expect(await live.json()).toEqual({
      status: 'alive',
      service: 'valuadis-api',
    });
  });
});

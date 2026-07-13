import { test, expect } from '../setup/fixtures';

/**
 * The rebranded Users surface is a read-only access registry backed by the users
 * API. These tests verify registry rendering, search, role/status filtering,
 * metric cards, and the Ethiopian format validators the registry relies on.
 * (Create/edit/deactivate are no longer in-app UI, so those flows are covered by
 * backend tests, not here.)
 */
test.describe('Users registry', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test.beforeEach(async ({ usersPage }) => {
    await usersPage.goto();
    await usersPage.waitForUsersToLoad();
  });

  test('should render backend user records', async ({ usersPage }) => {
    await expect(usersPage.userRows.first()).toBeVisible();
    expect(await usersPage.getUserCount()).toBeGreaterThan(0);
  });

  test('should display access metric cards', async ({ usersPage }) => {
    await expect(usersPage.metricCards.filter({ hasText: 'Total users' })).toBeVisible();
  });

  test('should search users by email', async ({ usersPage }) => {
    await usersPage.searchUser('selam.bekele@valuadis.com');
    await expect(usersPage.userRows).toHaveCount(1);
    await expect(usersPage.userRows.first()).toContainText('selam.bekele@valuadis.com');
  });

  test('should search users by name', async ({ usersPage }) => {
    await usersPage.searchUser('Dawit');
    await expect(usersPage.userRows).toHaveCount(1);
    await expect(usersPage.userRows.first()).toContainText('Dawit Tesfaye');
  });

  test('should handle no search results', async ({ usersPage }) => {
    await usersPage.searchUser('nonexistent.user@valuadis.com');
    await expect(usersPage.userRows).toHaveCount(0);
  });

  test('should filter users by status', async ({ usersPage }) => {
    await usersPage.filterByStatus('inactive');
    await expect(usersPage.userRows).toHaveCount(1);
    await expect(usersPage.userRows.first()).toContainText('Dawit Tesfaye');
    await expect(usersPage.userRows.first()).toContainText('Inactive');
  });

  test('should filter users by role', async ({ usersPage }) => {
    await usersPage.filterByRole('Valuer');
    await expect(usersPage.userRows.first()).toContainText('Valuer');
  });

  test('should reset the search filter', async ({ usersPage }) => {
    await usersPage.searchUser('Dawit');
    await expect(usersPage.userRows).toHaveCount(1);
    await usersPage.searchInput.fill('');
    await expect(usersPage.userRows.first()).toBeVisible();
    expect(await usersPage.getUserCount()).toBeGreaterThan(1);
  });

  test('should display Ethiopian valuer license information', async ({ usersPage }) => {
    await usersPage.searchUser('Selam');
    await expect(usersPage.userRows.first()).toContainText('EV-3344-5566');
  });

  test.describe('Ethiopian format validation', () => {
    test('should accept valid Ethiopian phone numbers', async ({ usersPage }) => {
      for (const phone of ['+251911234567', '0911234567', '+251922345678', '0922345678']) {
        expect(await usersPage.validateEthiopianPhone(phone)).toBe(true);
      }
    });

    test('should reject invalid Ethiopian phone numbers', async ({ usersPage }) => {
      for (const phone of ['+251811234567', '0811234567', '+25191234567', '09123456789', '123456789']) {
        expect(await usersPage.validateEthiopianPhone(phone)).toBe(false);
      }
    });

    test('should accept valid valuer license numbers', async ({ usersPage }) => {
      for (const license of ['EV-1234-5678', 'EV-9876-5432', 'EV-1111-2222']) {
        expect(await usersPage.validateLicenseNumber(license)).toBe(true);
      }
    });

    test('should reject invalid valuer license numbers', async ({ usersPage }) => {
      for (const license of ['EV-123-456', 'EV-12345-67890', 'EV12345678', 'EV-ABCD-EFGH']) {
        expect(await usersPage.validateLicenseNumber(license)).toBe(false);
      }
    });
  });
});

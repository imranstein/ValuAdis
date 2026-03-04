import { test as base } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { PropertiesPage } from '../page-objects/PropertiesPage';
import { ValuationsPage } from '../page-objects/ValuationsPage';
import { SettingsPage } from '../page-objects/SettingsPage';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  propertiesPage: PropertiesPage;
  valuationsPage: ValuationsPage;
  settingsPage: SettingsPage;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
  propertiesPage: async ({ page }, use) => {
    await use(new PropertiesPage(page));
  },
  valuationsPage: async ({ page }, use) => {
    await use(new ValuationsPage(page));
  },
  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
});

export { expect } from '@playwright/test';

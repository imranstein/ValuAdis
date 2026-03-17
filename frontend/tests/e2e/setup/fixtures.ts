import { test as base } from '@playwright/test';
import { LoginPage } from '../page-objects/LoginPage';
import { DashboardPage } from '../page-objects/DashboardPage';
import { PropertiesPage } from '../page-objects/PropertiesPage';
import { ValuationsPage } from '../page-objects/ValuationsPage';
import { SettingsPage } from '../page-objects/SettingsPage';
import { UsersPage } from '../page-objects/UsersPage';
import { ScrapersPage } from '../page-objects/ScrapersPage';
import { VehiclesPage } from '../page-objects/VehiclesPage';
import { AnalyticsPage } from '../page-objects/AnalyticsPage';
import { AuditPage } from '../page-objects/AuditPage';

type MyFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  propertiesPage: PropertiesPage;
  valuationsPage: ValuationsPage;
  settingsPage: SettingsPage;
  usersPage: UsersPage;
  scraperPage: ScrapersPage;
  vehiclesPage: VehiclesPage;
  analyticsPage: AnalyticsPage;
  auditPage: AuditPage;
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
  usersPage: async ({ page }, use) => {
    await use(new UsersPage(page));
  },
  scraperPage: async ({ page }, use) => {
    await use(new ScrapersPage(page));
  },
  vehiclesPage: async ({ page }, use) => {
    await use(new VehiclesPage(page));
  },
  analyticsPage: async ({ page }, use) => {
    await use(new AnalyticsPage(page));
  },
  auditPage: async ({ page }, use) => {
    await use(new AuditPage(page));
  },
});

export { expect } from '@playwright/test';

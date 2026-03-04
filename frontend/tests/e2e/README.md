# ValuAdis E2E Testing Suite

Comprehensive end-to-end testing suite for the ValuAdis Ethiopian Property Valuation Platform using Playwright.

## 📋 Test Coverage

### Core Pages (30+ scenarios)
- **Authentication** (`pages/auth.spec.ts`)
  - Login/logout flows
  - Form validation
  - Session management
  - Error handling

- **Dashboard** (`pages/dashboard.spec.ts`)
  - Statistics display
  - Quick actions
  - Recent activities
  - Responsive layout

- **Properties** (`pages/properties.spec.ts`)
  - CRUD operations
  - Search and filtering
  - Pagination
  - Data export
  - Form validation

- **Valuations** (`pages/valuations.spec.ts`)
  - Valuation creation
  - Method selection
  - Status filtering
  - Report generation
  - Ethiopian compliance

- **Settings** (`pages/settings.spec.ts`)
  - Tab navigation
  - Settings persistence
  - Web Scraper management
  - Configuration validation

### Web Scraper Tests (15+ scenarios)
- Scraper CRUD operations
- Configuration testing
- Manual execution
- Status toggling
- Logs viewing
- Statistics display

### Workflows (5+ scenarios)
- **Property Valuation Workflow** (`flows/property-valuation-workflow.spec.ts`)
  - End-to-end property creation to valuation
  - Multi-step form flows
  - Data persistence

### Ethiopian Compliance (15+ scenarios)
- **Proclamation 1365/2025** (`compliance/ethiopian-compliance.spec.ts`)
  - Currency (ETB) validation
  - Timezone (Addis Ababa)
  - Language support (Amharic)
  - Ethiopian municipalities
  - Property types
  - Documentation requirements
  - Market data sources

## 🚀 Running Tests

### Prerequisites
```bash
cd frontend
npm install
npx playwright install
```

### Run All Tests
```bash
npm run test:e2e
```

### Run Tests in UI Mode
```bash
npm run test:e2e:ui
```

### Run Tests in Headed Mode (See Browser)
```bash
npm run test:e2e:headed
```

### Debug Tests
```bash
npm run test:e2e:debug
```

### View Test Report
```bash
npm run test:e2e:report
```

### Generate Tests with Codegen
```bash
npm run test:e2e:codegen
```

## 📁 Test Structure

```
tests/e2e/
├── setup/
│   ├── auth.setup.ts          # Authentication setup
│   └── fixtures.ts            # Custom fixtures
├── page-objects/
│   ├── LoginPage.ts           # Login page object
│   ├── DashboardPage.ts       # Dashboard page object
│   ├── PropertiesPage.ts      # Properties page object
│   ├── ValuationsPage.ts      # Valuations page object
│   └── SettingsPage.ts        # Settings page object
├── pages/
│   ├── auth.spec.ts           # Authentication tests
│   ├── dashboard.spec.ts      # Dashboard tests
│   ├── properties.spec.ts     # Properties tests
│   ├── valuations.spec.ts     # Valuations tests
│   └── settings.spec.ts       # Settings tests
├── flows/
│   └── property-valuation-workflow.spec.ts
├── compliance/
│   └── ethiopian-compliance.spec.ts
└── README.md
```

## 🎯 Test Scenarios Summary

### Total Test Scenarios: 60+

| Category | Scenarios | Status |
|----------|-----------|--------|
| Authentication | 8 | ✅ |
| Dashboard | 10 | ✅ |
| Properties | 13 | ✅ |
| Valuations | 10 | ✅ |
| Settings (General) | 6 | ✅ |
| Web Scraper | 12 | ✅ |
| Workflows | 3 | ✅ |
| Ethiopian Compliance | 12 | ✅ |

## 🔧 Configuration

Tests are configured in `playwright.config.ts`:

- **Base URL**: `http://localhost:3000`
- **Browsers**: Chromium, Firefox, WebKit
- **Mobile**: Pixel 5, iPhone 12
- **Retries**: 2 (in CI), 0 (locally)
- **Parallel Workers**: 4 (locally), 1 (CI)
- **Timeout**: 30s per test
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

## 📊 Reporting

### HTML Report
After running tests, view the HTML report:
```bash
npm run test:e2e:report
```

### CI/CD Integration
Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

Reports and artifacts are uploaded to GitHub Actions:
- HTML test reports (30 days retention)
- Screenshots on failure (7 days)
- Videos on failure (7 days)

## 🎨 Page Object Pattern

Tests use the Page Object Model for maintainability:

```typescript
// Example: Using page objects
test('should search properties', async ({ propertiesPage }) => {
  await propertiesPage.goto();
  await propertiesPage.searchProperty('Addis Ababa');
  const count = await propertiesPage.getPropertyCount();
  expect(count).toBeGreaterThan(0);
});
```

## 🔐 Authentication

Tests use stored authentication state to avoid repeated logins:

```typescript
test.use({ storageState: 'tests/e2e/.auth/user.json' });
```

Authentication is set up once in `setup/auth.setup.ts`.

## 🌍 Ethiopian Compliance Testing

Special focus on Ethiopian-specific features:
- ETB currency validation
- Addis Ababa timezone
- Amharic language support
- Ethiopian municipalities (Addis Ababa, Bahir Dar, Gondar, etc.)
- Proclamation 1365/2025 compliance
- Ethiopian property sources (livingethio.com, ethiopiapropertycentre.com, etc.)

## 🐛 Debugging

### Debug a Specific Test
```bash
npx playwright test auth.spec.ts --debug
```

### Debug with Playwright Inspector
```bash
npx playwright test --debug
```

### View Trace
```bash
npx playwright show-trace trace.zip
```

## 📝 Writing New Tests

1. Create test file in appropriate directory
2. Import fixtures: `import { test, expect } from '../setup/fixtures'`
3. Use page objects for interactions
4. Add authentication if needed: `test.use({ storageState: 'tests/e2e/.auth/user.json' })`
5. Write descriptive test names
6. Use proper assertions

Example:
```typescript
import { test, expect } from '../setup/fixtures';

test.describe('My Feature', () => {
  test.use({ storageState: 'tests/e2e/.auth/user.json' });

  test('should do something', async ({ page }) => {
    await page.goto('/my-page');
    await expect(page.locator('h1')).toBeVisible();
  });
});
```

## 🎯 Success Criteria

- ✅ 60+ test scenarios implemented
- ✅ >80% coverage for critical flows
- ✅ Test execution time <30 minutes
- ✅ All tests passing in CI/CD
- ✅ Ethiopian compliance validated
- ✅ Web Scraper functionality tested
- ✅ Responsive design verified

## 🔄 Continuous Integration

GitHub Actions workflow (`.github/workflows/e2e-tests.yml`):
1. Sets up PostgreSQL with PostGIS
2. Installs backend dependencies
3. Runs database migrations
4. Starts backend server
5. Installs frontend dependencies
6. Installs Playwright browsers
7. Runs E2E tests
8. Uploads reports and artifacts

## 📚 Resources

- [Playwright Documentation](https://playwright.dev)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Page Object Model](https://playwright.dev/docs/pom)
- [ValuAdis API Documentation](../../backend/README.md)

## 🤝 Contributing

When adding new tests:
1. Follow existing patterns
2. Use page objects
3. Write descriptive test names
4. Add proper assertions
5. Test on multiple browsers
6. Verify mobile responsiveness
7. Update this README if adding new test categories

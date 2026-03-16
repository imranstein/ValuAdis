/**
 * E2E Test Credentials - ValuAdis
 * Align with Comprehensive E2E Testing Plan Phase 1
 * 
 * Valid credentials per plan: admin@valuadis.com / Admin1!
 * Login page hint shows: admin@valuadis.com / Admin123!
 * Backend may use: admin@valuadis.com / admin123
 * 
 * Use TEST_CREDENTIALS for consistency across all specs.
 */
export const TEST_CREDENTIALS = {
  // Primary: per plan and login.vue hint
  email: 'admin@valuadis.com',
  password: process.env.E2E_TEST_PASSWORD || 'Admin123!',
  // Fallback if backend uses different password
  fallbackPassword: 'admin123',
} as const;

export const INVALID_CREDENTIALS = {
  invalidEmail: 'invalid@email.com',
  invalidPassword: 'wrongpassword',
  malformedEmail: 'invalid-email',
} as const;

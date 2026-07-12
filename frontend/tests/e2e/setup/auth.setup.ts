import { promises as fs } from 'node:fs';
import path from 'node:path';
import { test as setup } from '@playwright/test';
import { MOCK_TOKEN, MOCK_USER } from './api-mock';

const authFile = 'tests/e2e/.auth/user.json';
const e2eBaseURL = process.env.E2E_BASE_URL || 'http://127.0.0.1:3020';

setup('authenticate', async () => {
  const absolutePath = path.resolve(process.cwd(), authFile);
  const authState = {
    cookies: [],
    origins: [
      {
        origin: e2eBaseURL,
        localStorage: [
          { name: 'valuadis_token', value: MOCK_TOKEN },
          { name: 'valuadis_refresh_token', value: MOCK_TOKEN },
          { name: 'valuadis_user', value: JSON.stringify(MOCK_USER) },
        ],
      },
    ],
  };

  await fs.mkdir(path.dirname(absolutePath), { recursive: true });
  await fs.writeFile(absolutePath, JSON.stringify(authState, null, 2));
});

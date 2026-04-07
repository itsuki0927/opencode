import { access } from 'node:fs/promises';
import process from 'node:process';

import { loadPlaywright } from './load-playwright.mjs';

const AUTH_PATH = process.env.TIKTOK_ADS_AUTH_PATH ?? 'playwright-auth/.auth/tiktok-ads.json';
const DEFAULT_TARGET_URL = 'https://ads.tiktok.com/creative/creativestudio/create';

function getTargetUrl() {
  const targetUrl = process.env.TIKTOK_ADS_TARGET_URL ?? DEFAULT_TARGET_URL;
  const parsedUrl = new URL(targetUrl);

  if (parsedUrl.hostname !== 'ads.tiktok.com' || !parsedUrl.pathname.startsWith('/creative/')) {
    throw new Error(`TIKTOK_ADS_TARGET_URL must stay under https://ads.tiktok.com/creative/... Received: ${targetUrl}`);
  }

  return parsedUrl.toString();
}

async function main() {
  const { chromium } = loadPlaywright();
  const targetUrl = getTargetUrl();

  await access(AUTH_PATH).catch(() => {
    throw new Error(`Missing auth state at ${AUTH_PATH}. Run save-auth.mjs first.`);
  });

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: false,
    slowMo: 50,
  });

  const context = await browser.newContext({
    storageState: AUTH_PATH,
  });

  const page = await context.newPage();

  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle', { timeout: 30_000 }).catch(() => {});

    if (page.url().includes('/login')) {
      throw new Error('Saved auth state is no longer valid. Re-run save-auth.mjs and refresh the login session.');
    }

    console.log(`Opened: ${page.url()}`);
    console.log(`Title: ${await page.title()}`);
    console.log('Browser is left open for manual inspection. Close the browser window when you are done.');

    await browser.waitForEvent('disconnected');
  } finally {
    if (browser.isConnected()) {
      await context.close();
      await browser.close();
    }
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});

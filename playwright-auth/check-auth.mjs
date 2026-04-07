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
    throw new Error(`Missing auth state at ${AUTH_PATH}`);
  });

  const browser = await chromium.launch({
    channel: 'chrome',
    headless: true,
  });

  const context = await browser.newContext({
    storageState: AUTH_PATH,
  });

  const page = await context.newPage();

  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 20_000 });
    await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => {});

    const currentUrl = page.url();
    if (currentUrl.includes('/login')) {
      throw new Error(`Auth state redirected to login: ${currentUrl}`);
    }

    if (!currentUrl.startsWith('https://ads.tiktok.com/creative/')) {
      throw new Error(`Unexpected TikTok Ads URL after auth check: ${currentUrl}`);
    }

    console.log(`VALID_AUTH ${currentUrl}`);
  } finally {
    await context.close();
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
